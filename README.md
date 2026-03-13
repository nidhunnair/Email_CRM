# Email CRM Automation System

A machine learning powered **Email CRM system** that automatically processes customer emails, classifies them into departments, detects sentiment and urgency, and generates automated responses.

This project simulates how modern customer support systems in banks or companies handle large volumes of incoming emails.

---

## Features

* **Email Fetching**

  * Fetches customer emails from an inbox.

* **Email Classification**

  * Classifies emails into departments such as:

    * Bank Accounts & Services
    * Credit Reporting & Credit Services
    * Credit Card & Prepaid Card
    * Loans & Debt Management
    * Mortgage
    * Payments & Remittances
    * Vehicle Loan or Lease

* **Sentiment Detection**

  * Identifies customer sentiment

* **Urgency Scoring**

  * Assigns an urgency score from **0 to 1** to prioritize customer issues.

* **Reason Extraction**

  * Extracts key sentences of the complaint or request.

* **Dashboard Interface**

  * Built using **Streamlit** to visualize:

    * Email categories
    * Sentiment distribution
    * Urgency scores
    * Department routing

---

## Tech Stack

* **Python**
* **Transformers (DistilBERT)**
* **PyTorch**
* **Scikit-learn**
* **Pandas / NumPy**
* **Streamlit**

---

## Machine Learning Models

The system uses **fine-tuned DistilBERT models** for:

* Email classification
* Sentiment analysis

Additional techniques used:

* **Embedding extraction**
* **KNN based scoring**
* **Text preprocessing and tokenization**

---

## Project Workflow

1. Fetch incoming emails
2. Clean and preprocess email text
3. Classify email department
4. Detect sentiment
5. Calculate urgency score
6. Extract issue reason
7. Generate automated reply
8. Display results in the dashboard


---

## Running the Project

Run the dashboard

```
streamlit run crm8.py
```

---

## Example Use Case

A customer sends an email:

> "My credit card payment failed but the amount was deducted from my bank account."

The system will automatically:

* Route it to **Payments & Remittances**
* Detect **negative sentiment**
* Assign **high urgency**

---

## Purpose of the Project

This project demonstrates how **Natural Language Processing (NLP)** and **machine learning** can automate customer support workflows and improve response efficiency.

