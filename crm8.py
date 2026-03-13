import streamlit as st
from classifier import predict_email, predict_spam
from email_insights import email_summary, get_metric_scores
from email_insights import save_to_log

# --- Page Configuration ---
st.set_page_config(page_title="BFSI Email Analyzer", layout="wide")

# --- initialize session state ---
if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = None

st.title("📧 CRM Email Intelligence")
st.write("Banking CRM system to manage customer emails, analyze intent, emotion, and urgency.")

# --- Sidebar demo emails ---
# categories = {"Bank Accounts & Services","Credit Reporting & Credit Services","Credit card & prepaid card","Loans & Debt Management","Mortgage","Payments & Remittances","Vehicle loan or lease"}
DEMO_EMAILS = {
    "Bank Accounts & Services": [
        "Hi, I'm currently traveling in Europe and my HDFC debit card was declined at a cafe in Paris today, December 24th. I checked my mobile app and I have over ₹3,50,000 in my savings account. I didn't receive any OTP or fraud alert SMS. Please unblock my card immediately as I am stranded without cash.",
        "Dear Customer Service, I am writing to formally complain about a ₹590 'Non-Maintenance Charges' (AMB) fee applied to my account. According to my records, I had a pending NEFT credit of ₹50,000 from my employer which should have cleared before the month-end check. I have been a loyal customer at the Bandra branch for 8 years and I request a waiver of this fee."
    ],
    "Credit Reporting & Credit Services": [
        "I recently noticed five 'Hard Inquiries' on my credit profile from your institution within a single week. I only authorized one application. These excessive hits are dropping my score. I request you to retract the unauthorized inquiries and update the credit agencies accordingly. This incorrect reporting is negatively affecting my credit score. I request you to investigate and rectify this with the bureau at the earliest.",
        "There is an unknown account on my Equifax report that does not belong to me. This reporting error is dropping my credit score. Please remove this entry from my file."
    ],
    "Credit card & prepaid card": [
        "There is a charge for ₹9,999 from 'Flipkart' on my credit card statement from yesterday that I did not authorize. I did not receive any OTP for this transaction, and the card is safely in my wallet. This looks like a fraudulent transaction; please block the card and initiate a dispute.",
        "I am disputing a transaction of ₹45,000 made at 'Reliance Digital' on November 12, 2025. I was at my office in Bengaluru during the time this purchase was made in Delhi. My physical card is with me, so I believe my details were skimmed. I have already blocked the card via the app, but the charge is still reflecting in my 'Outstanding' balance. Please reverse this."
    ],
    "Loans & Debt Management": [
        "I have recently faced a medical emergency in my family and can no longer afford the ₹15,000 monthly EMI on my personal loan. Can we discuss a moratorium for two months or a restructuring of the loan tenure to reduce the EMI amount?",
        "I am writing regarding my education loan. I submitted my degree completion certificate and employment details to the branch for the subsidy claim under the CSIS scheme back in August, but my interest subsidy hasn't been credited yet. Every time I visit the branch, I am told the portal is down. Please review my file and confirm when the subsidy will be adjusted."
    ],
    "Mortgage": [
        "The loan department at ICICI Bank failed to renew my property insurance premium this year despite having an active ECS mandate. Now I've received a notice from the insurance company that my policy has lapsed, leaving my mortgaged property at risk. Please resolve this immediately.",
        "Dear Home Loan Department, I am inquiring about the status of my Top-up loan application (Ref #IND882109). We submitted all documents three weeks ago, but I haven't heard from the legal verifier yet. My house renovation is stalled. Please provide an update on what documents are still outstanding from my side."
    ],
    "Payments & Remittances": [
        "I used UPI to send ₹12,000 to my landlord, but the transaction status is 'Pending' even though the money has been debited from my SBI account. My landlord has not received the funds. Please provide the UTR number and clarify if the money will be refunded or settled.",
        "On Friday afternoon, I initiated an IMPS transfer of ₹50,000 for a hospital bill. The transaction failed, but the amount has not been credited back to my account yet. This is an urgent medical requirement and I am extremely stressed. Please reverse the funds immediately so I can retry the payment."
    ],
    "Vehicle loan or lease": [
        "I just sold my Maruti Swift and the buyer is waiting for the transfer, but the RTO says you haven't issued the Form 35 (NOC) yet, even though I closed the car loan in full last Tuesday. Please courier the NOC to my registered address.",
        "I am writing to dispute the ₹12,500 'Repossession Charges' added to my final settlement. I had already informed the bank that I would be making the overdue payment by the 10th of the month. The vehicle was picked up from my office parking without prior notice even after I shared the payment screenshot. I refuse to pay these additional charges."
    ],
    "Positive feedback":[
        '''I would like to take a moment to sincerely appreciate the support and service provided by your credit card department.
The assistance I received was prompt, clear, and professional. The team handled my query efficiently and ensured that all details were explained in a transparent and customer-friendly manner. This level of responsiveness and attention reflects a strong commitment to customer satisfaction.
Positive experiences like this build trust and confidence in your services, and I truly value the effort your team puts into maintaining high service standards.
Thank you for your continued dedication and support. Please keep up the excellent work.'''
    ]
}
# --- Sidebar Implementation ---
with st.sidebar:
    st.title("🚀 Quick Demo Tools")
    st.info("Click the copy icon next to an email to use it for testing.")
    
    for category, emails in DEMO_EMAILS.items():
        with st.expander(f"📁 {category}"):
            for idx, email in enumerate(emails):
                st.caption(f"Example {idx+1}:")
                st.code(email, language='text') # Display in a code block; This creates a small text area with a copy button next to it


######### TABS #############
tabs = st.tabs(["🏠 Home (Process Flow)", "👨‍💼 Agent Queue", "📊 Manager Oversight"])
with tabs[0]:
    email_input = st.text_area("Paste the Email Text here:", height=200, placeholder="Dear Bank, I noticed an unauthorized transaction...")


    #   Analyse email Button
    if st.button("Analyze Email"):
        if email_input.strip() == "":
            st.warning("Please enter some text first!")
        else:
            email_input = email_input.strip()
            is_spam = predict_spam(email_input)
            if is_spam:
                st.warning("Spam or low context email detected")
            # Processing after button click
            with st.spinner("Analyzing email..."):
                class_result = predict_email(email_input)
                norm_summary, cust_summary = email_summary(email_input)
                summary_text_string = " ".join(cust_summary)
                metrics = get_metric_scores(summary_text_string)

                # STORE IN SESSION STATE 
                st.session_state.last_analysis = {
                    "raw_email": email_input,
                    "class_result": class_result,
                    "norm_summary": norm_summary,
                    "metrics": metrics
                }

    
    # defining kpi circle function
    def kpi_circle(label, value, color="#2ecc71", is_score=True):
        # Generates a circular KPI indicator using custom HTML+CSS.
        score_display = f"{value:.2f}" if is_score and isinstance(value, (int, float)) else value
        circle_html = f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 10px;">
            <div style="
                width: 85px; height: 85px; border-radius: 50%;
                background-color: {color}; display: flex;
                align-items: center; justify-content: center;
                color: white; font-weight: bold; font-size: 1.1rem;
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                border: 3px solid rgba(255,255,255,0.3);
                text-align: center; line-height: 1.2;
            ">
                {score_display}
            </div>
            <p style="margin-top: 8px; font-weight: 600; color: #555; font-size: 0.9rem; text-align: center;">{label}</p>
        </div>
        """
        st.markdown(circle_html, unsafe_allow_html=True)

    with st.expander("**Email Insights**", expanded=True):
        if st.session_state.last_analysis:
            res = st.session_state.last_analysis
            scores = res['metrics']['scores']
            
            col1, col2 = st.columns([1, 1.2])

            with col1:
                st.subheader("📌 Classification & Summary")
                class_res = res['class_result']
                winner = class_res['top_prediction']
                alternatives = class_res['alternatives']

                st.info(f"**Category:** {winner['label']}")
                st.write(f"Confidence: {winner['confidence_pct']}")
                # Runner-up Logic
                if winner['confidence_score'] < 0.70:
                    st.warning(f"⚠️ **Low Confidence Match**")
                    st.write(f"**Runner-up:** {alternatives[0]['label']} ({alternatives[0]['confidence_pct']})")
                    if winner['confidence_score'] < 0.50:
                        st.write(f"**Next best:** {alternatives[1]['label']} ({alternatives[1]['confidence_pct']})")

                # Key Points Summary
                st.markdown("---")
                st.markdown("**Key Points:**")
                for sentence in res['norm_summary']:
                    st.write(f"• {sentence}")

            with col2:
                st.subheader("📊 Strategic Intelligence")
                
                # Combined Risk
                combined_risk = max(scores['financial_loss'], scores['security_threat'])
                risk_color = "#c0392b" if combined_risk > 0.4 else "#27ae60"
                risk_label = "CRITICAL" if combined_risk > 0.4 else "STABLE"

                #  Urgency Color Intensity
                urgency_val = scores['urgent_action']
                satisfaction_val = scores['satisfaction']
                u_color = "#e74c3c" if urgency_val > 0.7 else ("#f39c12" if urgency_val > 0.5 else "#2ecc71")
                s_color = "#e74c3c" if satisfaction_val < 0.3 else ("#f39c12" if satisfaction_val < 0.7 else "#2ecc71")
                # Sentiment Ranking (Anger, Sadness, Frustration, Joy)
                emotions = {
                    "Anger": scores['anger'],
                    "Sadness": scores['sadness'],
                    "Frustration": scores['frustration'],
                    "Joy": scores['joy']
                }
                # Get top 2 emotions
                top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:2]

                # --- VISUALS: KPI CIRCLES ---
                kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
                
                with kpi_col1:
                    kpi_circle("Urgency", urgency_val, color=u_color)
                    
                with kpi_col2:
                    kpi_circle("Satisfaction", satisfaction_val, color=s_color)
                
                with kpi_col3:
                    kpi_circle("Financial Risk", risk_label, color=risk_color, is_score=False)

                # --- VISUALS: SENTIMENT TAGS ---
                st.markdown("**Dominant Sentiments:**")
                tag_col1, tag_col2 = st.columns(2)
                
                with tag_col1:
                    if top_emotions[0][0] == 'Anger':
                        st.error("ANGER")
                    elif top_emotions[0][0] == 'Frustration':
                        st.warning("FRUSTRATION")
                    elif top_emotions[0][0] == 'Sadness':
                        st.warning("SADNESS")
                    elif top_emotions[0][0] == 'Joy':
                        st.success("JOY")
                if top_emotions[1][1]>0.4:
                    with tag_col2:
                        if top_emotions[1][0] == 'Anger':
                            st.error("ANGER")
                        elif top_emotions[1][0] == 'Frustration':
                            st.warning("FRUSTRATION")
                        elif top_emotions[1][0] == 'Sadness':
                            st.warning("SADNESS")
                        elif top_emotions[1][0] == 'Joy':
                            st.success("JOY")

                with st.popover("See Raw Scores", use_container_width=True):
                    for emotion,score in scores.items():
                        st.write(emotion,score)

            # --- SAVE TO CSV BUTTON ---
            import datetime
            import uuid
            if st.button("Assign this case",type="primary"):
                # Generate a unique Ticket ID (e.g. TIC-20260303/07/26-814D)
                unique_id = f"TIC-{datetime.datetime.now().strftime('%Y%m%D')}-{str(uuid.uuid4())[:4].upper()}"
                csv_data = {
                    "Ticket_ID": unique_id,                          # Unique Identifier
                    "email_text": res['raw_email'],
                    "category": winner['label'],
                    "confidence": winner['confidence_pct'],
                    "urgency": scores['urgent_action'],
                    "financial_loss": scores['financial_loss'],
                    "security_threat": scores['security_threat'],
                    "anger": scores['anger'],
                    "sadness": scores['sadness'],
                    "frustration": scores['frustration'],
                    "joy": scores['joy'],
                    "satisfaction":scores['satisfaction'],
                    "Status": "Open"                                #  complaint state
                    }

                save_to_log(csv_data,filename="analysis_log.csv")
                st.toast("✅ Case saved to analysis_log.csv", icon="✔️")



    st.divider()
    #########################################################
    ################ EMAIL FETCHING #########################
    from emailfetch1 import fetch_and_save_emails
    import pandas as pd
    import os
    from dotenv import load_dotenv

    # Load the variables from .env
    load_dotenv()

    username = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    fetch_email_csv = "fetched_emails.csv"

    st.caption("Number of unread emails to fetch")
    # Inputs for number of emails to fetch
    n_email_col, fetch_col, status_col = st.columns([2,1,3])

    with n_email_col:
        n_emails = st.number_input("",min_value=1, max_value=20, value=5, label_visibility="collapsed")
    with fetch_col:
        if st.button("Fetch Emails"):
            
            with st.spinner("Fetching from Gmail..."):

                df,new_count = fetch_and_save_emails(username, password,n=n_emails,csv_path=fetch_email_csv)
            with status_col:
                if new_count == 0:
                    st.warning("No new unread emails to fetch")
                else:
                    st.success(f"Fetched and saved {new_count} emails to CSV.")

    #  Display and Edit read/unread status
    try:
        df_display = pd.read_csv(fetch_email_csv)
        
        # Filter to show only UNREAD emails in the UI
        unread_df = df_display[df_display["Status"] == "unread"]

        with st.expander(f"Unread inbox ({len(unread_df)})"):
            st.write("Change status to 'read' to remove it from this view.")

            # Use data_editor to allow editing the 'Status' column
            edited_df = st.data_editor(
                unread_df,
                column_config={
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["unread", "read"],
                        required=True,
                    )
                },
                disabled=["ID", "From", "Subject", "Body"], # Only status is editable
                hide_index=True,
                key="email_editor"
            )

            # Save Changes Logic
            if st.button("Apply Changes"):
                # Update the original CSV with changes from the editor
                # We find rows that were changed to 'read'
                read_ids = edited_df[edited_df["Status"] == "read"]["ID"].astype(str).tolist()
                
                # Update full dataframe
                df_display.loc[df_display["ID"].astype(str).isin(read_ids), "Status"] = "read"

                df_display.to_csv(fetch_email_csv, index=False)
                st.rerun() # Refresh UI to hide 'read' emails

    except FileNotFoundError:
        st.info("No emails fetched yet. Click the button above.")
    st.divider()

    col1, col2 = st.columns([1,2])

    with col1:
        st.write("#### Run Automation")

        from automation import run_pipeline

        if st.button("Run Pipeline", type="primary", use_container_width=True):
            with st.spinner("Running full pipeline..."):
                run_pipeline(username, password, n_emails=10)
                st.toast("Pipeline completed!")

        st.caption("Fetch emails • Mark as Read • Analyse • Save")

    st.divider()

    ###########################################################
    ##############  URGENCY SORTED TABLE  #####################

    import pandas as pd

    # Define a function to apply colors based on urgency
    def color_urgency(row):
        score = row['urgency']
        if score > 0.70:
            # High Urgency - Muted Red
            bg_color = "rgba(255, 75, 75, 0.3)" 
        elif score > 0.50:
            # Medium Urgency - Amber
            bg_color = "rgba(255, 165, 0, 0.3)"
        else:
            # Low Urgency - Soft Green
            bg_color = "rgba(37, 211, 102, 0.2)"
        return [f'background-color: {bg_color};' for _ in row]


    ############################################################################3
    def filter_analysis_log(df, category, min_urgency, risk_only):
        filtered_df = df.copy()

        if category != "All":
            filtered_df = filtered_df[filtered_df["category"] == category]

        filtered_df = filtered_df[filtered_df["urgency"] >= min_urgency]

        if risk_only:
            filtered_df = filtered_df[
                (filtered_df["financial_loss"] > 0.4) |
                (filtered_df["security_threat"] > 0.4)
            ]

        return filtered_df


    try:
        df = pd.read_csv("analysis_log.csv").sort_values(by="urgency", ascending=False)

        col1, col2, col3 = st.columns(3)
        with col1:
            selected_category = st.selectbox(
                "Category",
                options=["All"] + sorted(df["category"].unique().tolist())
            )

        with col2:
            min_urgency = st.slider(
                "Minimum Urgency",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.05
            )

        with col3:
            risk_only = st.checkbox("Show high risk cases only")

        ########## Dataframe display ##########
        if not df.empty:
            filtered_df = filter_analysis_log(
                df,
                selected_category,
                min_urgency,
                risk_only
            )

            styled_df = filtered_df.style.apply(color_urgency, axis=1)

            st.write("### 📊 Analysis Log (Priority View)")
            st.dataframe(styled_df, hide_index=True, use_container_width=True)
        else:
            st.info("No cases saved yet.")

    except FileNotFoundError:
        st.warning("No cases saved yet.")


############################################################
### AGENT TAB & MANAGER TAB ###
import plotly.express as px

from manager_tab import show_manager_page
from agent_tab import show_agent_page

with tabs[2]:
    show_manager_page()


with tabs[1]:
    show_agent_page()
    