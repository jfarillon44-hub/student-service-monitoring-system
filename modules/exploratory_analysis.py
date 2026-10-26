import streamlit as st
import pandas as pd
import plotly.express as px

def render_eda(df):
    st.write("### Descriptive statistics")
    st.dataframe(df.describe(include="all").transpose(), use_container_width=True)
    if "Service_Type" in df:
        st.plotly_chart(px.histogram(df, x="Service_Type", title="Requests by service type"), use_container_width=True)
    if "Assigned_Office" in df:
        st.plotly_chart(px.histogram(df, x="Assigned_Office", color="Status" if "Status" in df else None, barmode="group", title="Workload by assigned office"), use_container_width=True)
    if "Queue_Length" in df:
        st.plotly_chart(px.histogram(df, x="Queue_Length", nbins=20, title="Submission queue-length distribution"), use_container_width=True)
    if "SLA_Breached" in df:
        st.plotly_chart(px.histogram(df, x="SLA_Breached", title="Historical SLA breach class distribution"), use_container_width=True)
    elif "Processing_Days" in df and "SLA_Days" in df:
        completed = df[(df["Status"].astype(str).str.lower()=="completed") & df["Processing_Days"].notna()]
        if not completed.empty:
            completed = completed.copy()
            completed["SLA_Breached"] = (completed["Processing_Days"] > completed["SLA_Days"]).astype(int)
            st.plotly_chart(px.histogram(completed, x="SLA_Breached", title="Historical SLA breach class distribution (completed records)"), use_container_width=True)
