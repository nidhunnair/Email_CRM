import re
import torch
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import DistilBertTokenizer, DistilBertModel
from nltk.tokenize import sent_tokenize
import nltk

# run only once for downloading
# nltk.download('punkt_tab')
# nltk.download('punkt')
# nltk.download('vader_lexicon')

POV_MAP = {
    r"\bi am\b": "the customer is",
    r"\bi'm\b": "the customer is",
    r"\bi was\b": "the customer was",
    r"\bi have\b": "the customer has",
    r"\bi've\b": "the customer has",
    r"\bi\b": "the customer",
    r"\bmy\b": "the customer's",
    r"\bme\b": "the customer",
    r"\bwe\b": "the customer",
    r"\bus\b": "the customer",
    r"\bour\b": "the customer's",
    r"\bours\b": "the customer's"
}
SALUTATION_PATTERN = r"""
^\s*(
    hi|hello|hlo|hey|
    dear\s+(sir|madam|mam|sir/madam)|
    respected\s+(sir|madam|mam)
)
[\s,:\-]* 
"""

def normalize_pov(sentence):
    for pattern, replacement in POV_MAP.items():
        sentence = re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)
        sentence = re.sub(SALUTATION_PATTERN, "", sentence, flags=re.IGNORECASE | re.VERBOSE)
    sentence = sentence[0].upper() + sentence[1:]
    return sentence


def email_summary(text, n_sentences=2):
    text = re.sub(r"\s+", " ", text).strip()

    sentences = sent_tokenize(text)
    if len(sentences) <= n_sentences:
        # return (List, List)
        normalized = [normalize_pov(s) for s in sentences]
        return (normalized, sentences)
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(sentences)
    sentence_scores = np.asarray(tfidf.sum(axis=1)).ravel()
    ranked_indices = np.argsort(sentence_scores)[::-1][:n_sentences]
    ranked_indices = sorted(ranked_indices)

    summary_normalized = []
    summary_customer = []
    for i in ranked_indices:
        normalized = normalize_pov(sentences[i])
        
        summary_normalized.append(normalized)
        summary_customer.append(sentences[i])

    return (summary_normalized,summary_customer)



# Prototype emails for scoring
df_prototypes = pd.read_csv("bfsi_prototypes.csv")


#using the standard distilbert model
model_name = "distilbert-base-uncased"
tokenizer = DistilBertTokenizer.from_pretrained(model_name)
model = DistilBertModel.from_pretrained(model_name)
model.eval() # Set to evaluation mode


def get_embedding(text):
    #Extracts the 768-dim vector from the CLS token.
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
    # The [CLS] token is the first token in the sequence (index 0)
    return outputs.last_hidden_state[:, 0, :].numpy()


# Pre-compute embeddings for prototype emails
prototype_embeddings = np.vstack([get_embedding(x) for x in df_prototypes['core_intent']])

# --- Setup KNN ---
from sklearn.neighbors import NearestNeighbors

# using metric='cosine' which is suitable for text
# n_neighbors=3
k = 3
knn = NearestNeighbors(n_neighbors=k, metric='cosine')
knn.fit(prototype_embeddings)

def get_metric_scores(new_email_text):
    #  Vectorize incoming email
    new_emb = get_embedding(new_email_text).reshape(1, -1)
    
    # Find the Nearest Neighbors
    # distances: cosine distance (1 - similarity)
    # indices: index of the matching prototypes in df_prototypes
    distances, indices = knn.kneighbors(new_emb)
    
    # Flatten because kneighbors returns a 2D array
    distances = distances[0]
    indices = indices[0]
    
    # Convert Distance to Similarity 
    # Cosine Distance = 1 - Cosine Similarity
    top_sims = 1 - distances # sim stands for similarity
    
    # Calculate Weights
    exp_weights = np.exp(top_sims * 10) # Higher multiplier = more "decisive" scoring
    weights = exp_weights / np.sum(exp_weights)

    # Aggregate Column Scores
    score_cols = ['anger', 'sadness', 'frustration', 'joy', 'satisfaction',
                  'security_threat', 'financial_loss', 'urgent_action']
    
    final_scores = {}
    for col in score_cols:
        # Weighted average of the top k prototypes
        weighted_val = sum(weights[i] * df_prototypes.iloc[indices[i]][col] for i in range(k))
        
        # Scale to 0-1 for your final output
        final_scores[col] = round(float(weighted_val), 3)
    
    return {
        "top_match_intent": df_prototypes.iloc[indices[0]]['core_intent'],
        "confidence": round(float(top_sims[0]), 4),
        "cluster_intents": df_prototypes.iloc[indices]['core_intent'].tolist(),
        "scores": final_scores
    }




import os
from datetime import datetime

def save_to_log(data_dict, filename="analysis_log.csv"):
    """Appends analysis results to a CSV file."""
    file_exists = os.path.isfile(filename)
    df = pd.DataFrame([data_dict])
    # Add a timestamp to know when the mail was saved
    df.insert(0, 'timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Append to CSV (header only if file doesn't exist; append mode)
    df.to_csv(filename, mode='a', index=False, header=not file_exists)