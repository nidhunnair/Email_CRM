import streamlit as st
import uuid
import datetime
import os
from dotenv import load_dotenv

from classifier import predict_email
from email_insights import get_metric_scores
from email_insights import save_to_log
from emailfetch1 import fetch_and_save_emails

def run_pipeline(username, password, n_emails=2):
    """
    1. Fetches new unread emails.
    2. Updates local CSV to mark them as 'read' (processed).
    3. Runs classification and scoring.
    4. Saves final analysis to analysis_log.csv.
    """
    print(f"--- Pipeline Started at {datetime.datetime.now().strftime('%H:%M:%S')} ---")
    
    # Fetch and Save to fetched_emails.csv
    emails_df, new_count = fetch_and_save_emails(username, password, n=n_emails)
    
    if new_count == 0:
        print("No new emails found. Pipeline exiting.")
        st.toast("No new emails found")
        return
    
    print(f"Processing {new_count} new emails...")

    # Process only the "unread" emails in dataframe
    # as the fetch_and_save_emails() marks new ones as 'unread' by default
    new_mails = emails_df.tail(new_count)
    for row in new_mails.itertuples(index=True):
        # Check if it was already processed (just in case)
        if row.Status == 'read':
            continue

        # row.Body gives just the body string
        email_body = str(row.Body).replace('\r', '').replace('\n', ' ').strip()
        
        # Run Analysis Functions
        prediction_res = predict_email(email_body)
        winner = prediction_res['top_prediction']
        
        metric_res = get_metric_scores(email_body)
        scores = metric_res['scores']
        
        # Generate Unique Ticket ID
        unique_id = f"TIC-{datetime.datetime.now().strftime('%Y%m%D')}-{str(uuid.uuid4())[:4].upper()}"

        # Prepare Data for saving to Analysis Log
        csv_data = {
            "Ticket_ID": unique_id,
            "email_text": email_body,
            "category": winner['label'],
            "confidence": winner['confidence_pct'],
            "urgency": scores['urgent_action'],
            "financial_loss": scores['financial_loss'],
            "security_threat": scores['security_threat'],
            "anger": scores['anger'],
            "sadness": scores['sadness'],
            "frustration": scores['frustration'],
            "joy": scores['joy'],
            "satisfaction": scores['satisfaction'],
            "Status": "Open"
        }
        
        # Save to analysis_log.csv
        save_to_log(csv_data, filename="analysis_log.csv")
        
        # Update status to 'read' in the csv
        emails_df.at[row.Index, 'Status'] = 'read'
    
    # Save the updated email list (with 'read' statuses)
    emails_df.to_csv("fetched_emails.csv", index=False)
    print(f"--- Pipeline Finished. {new_count} emails logged to analysis_log.csv ---")

if __name__ == "__main__":

    load_dotenv()

    username = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    run_pipeline(username, password)