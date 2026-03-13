import imaplib
import email
import pandas as pd
import os
from dotenv import load_dotenv
from email.utils import parsedate_to_datetime

# Load the variables from .env
load_dotenv()

# Retrieve them
username = os.getenv("EMAIL_USER")
password = os.getenv("EMAIL_PASS")

# ----------- FETCH TOP N EMAILS --------
def fetch_and_save_emails(username, password, n=20, csv_path="fetched_emails.csv"):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    print("logged in")
    mail.select("inbox")
    print("opened inbox")

    # Search for UNSEEN emails
    status, data = mail.search(None, 'UNSEEN') # ALL/UNSEEN
    mail_ids = data[0].split()
    
    # Get the top N latest unread emails
    top_n_ids = mail_ids[-n:][::-1]
    
    email_list = []
    for m_id in top_n_ids:
        status, data = mail.fetch(m_id, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])
        
        # Extract Body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors='ignore')
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors='ignore')
        

        date_str = msg.get("Date")
        dt = parsedate_to_datetime(date_str) if date_str else None
        email_list.append({
            "ID": m_id.decode(),
            "From": msg.get("From"),
            "Subject": msg.get("Subject"),
            "Date": dt,
            "Body": body[:200].replace('\n', ' '), # Snippet for CSV
            "Status": "unread" # Default status
        })

    mail.logout()
    print("logged out")
    # Convert to DataFrame
    df = pd.DataFrame(email_list)
    new_count = len(df)
    # Save/Append logic
    if not os.path.isfile(csv_path):
        df.to_csv(csv_path, index=False)
    else:
        # Load existing, append new, and remove duplicates based on ID
        existing_df = pd.read_csv(csv_path)
        
        if df.empty:
            return existing_df,new_count
    
        combined_df = pd.concat([existing_df, df]).drop_duplicates(subset=['ID'], keep='last')
        combined_df.to_csv(csv_path, index=False)
        return combined_df,new_count
    
    return df,new_count

if __name__ == "__main__":
    df,count = fetch_and_save_emails(username, password,n=5, csv_path="fetched_emails.csv")
    print(df.head())