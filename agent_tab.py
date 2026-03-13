import streamlit as st
import pandas as pd

analysis_log_csv = "analysis_log.csv"

# define color scheme for urgency sorted table
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

def kpi_circle(label, value, color="#2ecc71", is_score=True):
    # Generates a circular KPI indicator using custom HTML/CSS.
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

def show_agent_page():
    st.header("👨‍💼 Agent Workspace")
        
    try:
        # Load the latest data
        df_agent = pd.read_csv(analysis_log_csv)
        
        # Setup Filters for the Agent's Queue
        col_filt1, col_filt2 = st.columns([1, 1])
        with col_filt1:
            depts = ["All Departments"] + list(df_agent['category'].unique())
            selected_dept = st.selectbox("Your Department", depts)
        
        with col_filt2:
            # Only show 'Open' cases to the agent
            open_queue = df_agent[df_agent['Status'] == 'Open']
            if selected_dept != "All Departments":
                open_queue = open_queue[open_queue['category'] == selected_dept]
            
            selected_ticket_id = st.selectbox(
                "Select Ticket to Process", 
                options=open_queue['Ticket_ID'].tolist() if not open_queue.empty else ["No Open Tickets"]
            )
        col_filt1.caption(f"{len(open_queue)} unresolved tickets")

        st.divider()

        if not open_queue.empty and selected_ticket_id != "No Open Tickets":
            # Get the data for the specific selected ticket
            ticket_data = open_queue[open_queue['Ticket_ID'] == selected_ticket_id].iloc[0]

            # Insights & Drafting 
            col_email, col_tools = st.columns([1, 1])

            with col_email:
                st.subheader("📩 Customer Communication")
                st.markdown(f"**Ticket ID:** `{selected_ticket_id}`")
                st.info(ticket_data['email_text'])
                
                # Show Category and Confidence
                st.caption(f"Classification: {ticket_data['category']} ({ticket_data['confidence']})")

            with col_tools:
                st.subheader("💡 AI Insights")
                u_val = ticket_data['urgency']
                u_color = "#e74c3c" if u_val > 0.7 else ("#f39c12" if u_val > 0.3 else "#2ecc71")
                
                # Frustration Color (high score = red)
                f_val = ticket_data['frustration']
                f_color = "#e74c3c" if f_val > 0.6 else ("#f39c12" if f_val > 0.3 else "#2ecc71")
                
                # Risk Profile (Based on max of security/financial)
                risk_score = max(ticket_data['financial_loss'], ticket_data['security_threat'])
                risk_label = "CRITICAL" if risk_score > 0.4 else "STABLE"
                risk_color = "#c0392b" if risk_score > 0.4 else "#27ae60"

                # KPI CIRCLES
                kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
                
                with kpi_col1:
                    kpi_circle("Urgency", u_val, color=u_color)
                
                with kpi_col2:
                    kpi_circle("Frustration", f_val, color=f_color)
                
                with kpi_col3:
                    kpi_circle("Financial Risk", risk_label, color=risk_color, is_score=False)

            st.markdown("---")
            # Draft Area
            st.subheader("📝 Draft Resolution")
            reply_text = st.text_area(
                "Compose your response:", 
                placeholder="Provide a solution or request more details...",
                height=200
            )

            btn_col1, or_col, btn_col2 = st.columns([1,0.1,1])
            
            if btn_col1.button("Send & Mark Solved", type="primary", use_container_width=True):
                if reply_text.strip() == "":
                    st.error("Please draft a reply before closing the case.")
                else:
                    # Logic to update CSV
                    # Update the status and add the reply text
                    df_agent.loc[df_agent['Ticket_ID'] == selected_ticket_id, 'Status'] = 'Solved'
                    df_agent.loc[df_agent['Ticket_ID'] == selected_ticket_id, 'Agent_Reply'] = reply_text
                    
                    # Save back to CSV
                    df_agent.to_csv(analysis_log_csv, index=False)
                    
                    st.toast(f"Reply sent to customer for {selected_ticket_id}!", icon="🚀")
                    st.rerun()

            or_col.write("#### OR")

            if btn_col2.button("Escalate Case", type="primary", use_container_width=True):
                df_agent.loc[df_agent['Ticket_ID'] == selected_ticket_id, 'Status'] = 'Escalated'
                df_agent.to_csv(analysis_log_csv, index=False)
                st.warning("Case escalated to Senior Manager.")
                st.rerun()

            open_queue = open_queue.sort_values(by="urgency", ascending=False)
            styled_df = open_queue.style.apply(color_urgency, axis=1)

            
            st.write("### 📊 Priority View")
            st.dataframe(styled_df, hide_index=True, use_container_width=True)
        else:
            st.success("🎉 Excellent work! Your current queue is empty.")

    except FileNotFoundError:
        st.info("The analysis log is currently empty. Please assign cases from the Home tab.")

