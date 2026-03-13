import streamlit as st
import pandas as pd
import plotly.express as px

analysis_log_csv = "analysis_log.csv"
def show_manager_page():
    
    try:
        df_mgr = pd.read_csv(analysis_log_csv) #  Load Data 
        
        st.title("📊 Executive Oversight Dashboard")
        st.markdown("Real-time operational metrics for Banking Email Intelligence.")

        if st.checkbox("Show only unsolved cases"):
            df_mgr = df_mgr[df_mgr['Status'] == 'Open']

        # Top Level KPI Metrics
        total_tickets = len(df_mgr)
        open_tickets = len(df_mgr[df_mgr['Status'] == 'Open'])
        avg_urgency = df_mgr['urgency'].mean()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Tickets", total_tickets)
        m2.metric("Current Open Queue", open_tickets)
        m3.metric("Avg. Urgency Score", f"{avg_urgency:.2f}")

        st.divider()

        # Visuals and charts
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("📁 Volume by Category")
            # Count tickets per category
            cat_counts = df_mgr['category'].value_counts().reset_index()
            cat_counts.columns = ['category', 'count']
            fig_bar = px.bar(cat_counts, x='count', y='category', orientation='h', 
                            color='count', color_continuous_scale='Blues',
                            labels={'count': 'Number of Emails', 'category': 'Department'})
            st.plotly_chart(fig_bar, use_container_width=True)

            st.subheader("🔥 Urgency by Department")
            # urgency threshold
            threshold = st.slider(
                "Minimum Urgency", key="chart_slider",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.02
            )

            # Filter data based on slider
            urgent_df = df_mgr[df_mgr['urgency'] >= threshold]

            if not urgent_df.empty:
                # Group data to get both Count and Average Urgency
                tm_data = urgent_df.groupby('category').agg(
                    case_count=('Ticket_ID', 'count'),
                    avg_urgency=('urgency', 'mean')
                ).reset_index()

                # Create Treemap
                fig_tm = px.treemap(
                    tm_data, 
                    path=['category'], 
                    values='case_count', # Size of the box
                    color='avg_urgency',  # Color of the box
                    color_continuous_scale='Reds',
                    labels={'case_count': 'Total Cases', 'avg_urgency': 'Avg Urgency'},
                    title=f"Departments with Urgency ≥ {threshold}"
                )

                fig_tm.update_traces(textinfo="label+value")
                st.plotly_chart(fig_tm, use_container_width=True)
            else:
                st.info("No urgent cases found at this threshold.")

        with col_right:
            st.subheader("✅ Resolution Progress")
            status_counts = df_mgr['Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            fig_status = px.pie(status_counts, values='Count', names='Status', 
                            color='Status', color_discrete_map={'Open':"#f39c12", 'Solved':'#2ecc71', 'Escalated':"#e74c3c"},
                            hole=0.4)
            st.plotly_chart(fig_status, use_container_width=True)



            st.subheader("⚠️ Escalation Rate by Department")
            # Calculate % of tickets that are Escalated vs Open vs Solved
            esc_data = df_mgr.groupby(['category', 'Status']).size().reset_index(name='count')
            fig_esc = px.bar(
                esc_data, 
                x='category', y='count', color='Status',
                title="Where are tickets getting stuck?",
                barmode='stack',
                category_orders={"Status": ['Solved', 'Open', 'Escalated']},
                labels={'count': 'Ticket Count', 'category': 'Department'},
                color_discrete_map={'Escalated': '#e74c3c', 'Open': '#3498db', 'Solved': '#2ecc71'}
            )
            st.plotly_chart(fig_esc, use_container_width=True)



        st.subheader("📈 Ticket Volume Trend")
        timeframe_options = {
            "Hourly": "H",
            "Daily": "D",
            "Weekly":"W"
        }

        selected_label = st.selectbox("Select time frame", list(timeframe_options.keys()),
                                      index=list(timeframe_options.keys()).index("Daily")) #index sets the default initial value
        selected_timeframe = timeframe_options[selected_label]
        df_mgr['timestamp'] = pd.to_datetime(df_mgr['timestamp'], format='mixed', dayfirst=True)
        trend_data = df_mgr.resample(selected_timeframe, on='timestamp').size().reset_index(name='counts')
        fig_trend = px.line(trend_data, x='timestamp', y='counts')
        st.plotly_chart(fig_trend, use_container_width=True)



    except FileNotFoundError:
        st.error("No analysis log found. Please analyze and save emails on the Home page first.")

    st.markdown("---")
    st.subheader("🛠️ Manager Tools")
    # Searchable Data Table
    with st.expander("🔍 Detailed Log Table"):
        st.dataframe(df_mgr, hide_index=True, use_container_width=True)

    st.caption("Complaint Status Control")
    ticket_to_fix = st.selectbox("Select Ticket ID", df_mgr['Ticket_ID'].unique())
    new_status = st.radio("Set Status To:", ["Open", "Solved"], horizontal=True)
    
    if st.button("Apply Status Change"):
        df_mgr.loc[df_mgr['Ticket_ID'] == ticket_to_fix, 'Status'] = new_status
        df_mgr.to_csv(analysis_log_csv, index=False)
        st.toast(f"Updated {ticket_to_fix} to {new_status}")
        st.rerun()
