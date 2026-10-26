import streamlit as st
import pandas as pd
import plotly.express as px

def render_dashboard(df):
    d = df.copy()
    total = len(d)
    pending = int((d["Status"].astype(str).str.lower()=="pending").sum()) if "Status" in d else 0
    high_queue = int((pd.to_numeric(d["Queue_Length"], errors="coerce") > 15).sum()) if "Queue_Length" in d else 0
    incomplete = int((d["Required_Documents_Complete"].astype(str).str.lower()=="no").sum()) if "Required_Documents_Complete" in d else 0
    a,b,c,dcol = st.columns(4)
    a.metric("Total requests", f"{total:,}"); b.metric("Pending", f"{pending:,}")
    c.metric("Queue > 15", f"{high_queue:,}"); dcol.metric("Documents incomplete", f"{incomplete:,}")
    st.markdown("### Queue review list")
    if "Queue_Length" in d:
        d["Queue_Length"] = pd.to_numeric(d["Queue_Length"], errors="coerce")
        review = d[(d["Queue_Length"] > 15) | (d.get("Required_Documents_Complete", pd.Series(index=d.index,dtype=str)).astype(str).str.lower()=="no")].copy()
        review["Review reason"] = review.apply(lambda r: "; ".join((["Queue > 15"] if pd.notna(r.get("Queue_Length")) and r.get("Queue_Length")>15 else []) + (["Documents incomplete"] if str(r.get("Required_Documents_Complete","")).lower()=="no" else [])), axis=1)
        cols=[c for c in ["Request_ID","Service_Type","Assigned_Office","Priority","Queue_Length","Required_Documents_Complete","Status","Review reason"] if c in review]
        st.dataframe(review[cols].head(100), use_container_width=True)
        st.download_button("Download review queue CSV", review[cols].to_csv(index=False).encode("utf-8"), "review_queue.csv", "text/csv")
    if "Assigned_Office" in d and "Queue_Length" in d:
        chart=d.groupby("Assigned_Office",dropna=False)["Queue_Length"].mean().reset_index()
        st.plotly_chart(px.bar(chart,x="Assigned_Office",y="Queue_Length",title="Average queue length by office"),use_container_width=True)
    st.info("Review flags prioritize staff attention only. They do not authorize automatic denial of student services.")
