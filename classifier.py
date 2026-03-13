from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# Path to model folder
model_path = "cfpbfinetune2"

# Load the model and tokenizer from that folder
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)


def predict_email(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=256)
    
    with torch.no_grad():
        logits = model(**inputs).logits
    
    probs = torch.nn.functional.softmax(logits, dim=-1).squeeze()
    
    # Get the top 3 results (indices and values)
    top_probs, top_indices = torch.topk(probs, k=3)
    
    # Create a list of top results
    results = []
    for i in range(len(top_indices)):
        results.append({
            "label": model.config.id2label[top_indices[i].item()],
            "confidence_score": top_probs[i].item(),
            "confidence_pct": f"{top_probs[i].item()*100:.2f}%"
        })
    
    return {
        "top_prediction": results[0], # The Winner
        "alternatives": results[1:],  # The Runners-up
        "all_probabilities": probs.tolist()
    }
    

########### SPAM CLASSIFIER ##############

# Path to model folder
spam_model_path = "spamclassifier1"

#  Load the model and tokenizer from that folder
spam_tokenizer = AutoTokenizer.from_pretrained(spam_model_path)
spam_model = AutoModelForSequenceClassification.from_pretrained(spam_model_path)

def predict_spam(text):
    inputs = spam_tokenizer(text, return_tensors="pt", truncation=True, padding=True, return_token_type_ids=False)

    with torch.no_grad():
        logits = spam_model(**inputs).logits

    # Convert logits to probabilities
    probabilities = torch.nn.functional.softmax(logits, dim=1)
    predicted_class_id = torch.argmax(probabilities).item()

    labels = {0: "HAM", 1: "SPAM"}

    return predicted_class_id