from pathlib import Path
import streamlit as st
import pandas as pd
from modules.data_processing import validate_and_clean, REQUIRED_COLUMNS, FEATURES
from modules.exploratory_analysis import render_eda
from modules.prediction import load_model, predict_one, model_metrics
from modules.dashboard import render_dashboard

st.set_page_config(page_title="Student Service Request Monitoring", page_icon="🎓", layout="wide")
st.title("🎓 Student Service Request Monitoring System")
st.caption("SLA breach prediction • Request-delay and workload dashboard • Staff review")

with st.sidebar:
    st.header("Navigation")
    page = st.selectbox("Choose module", ["Home", "Dataset", "Data Analysis", "Prediction", "Dashboard", "System Design"])
    st.divider()
    st.caption("Decision support only. A prediction must not automatically deny or reject student services.")

@st.cache_data
def load_demo_data():
    p = Path("sample_data/student_service_requests_demo.csv")
    return pd.read_csv(p) if p.exists() else pd.DataFrame()

if "service_df" not in st.session_state:
    st.session_state.service_df = load_demo_data()
df = st.session_state.service_df

if page == "Home":
    st.subheader("Project overview")
    st.write("This application supports student-service staff in reviewing request workload and potential SLA breaches using submission-time information.")
    c1,c2,c3 = st.columns(3)
    c1.metric("Model", "Decision Tree"); c2.metric("Input features", len(FEATURES)); c3.metric("Review policy", "Human-led")
    st.markdown("### Modules")
    st.markdown("- **Dataset:** upload CSV, validate schema, inspect missing values and duplicates.\\n- **Data Analysis:** summary statistics, target distribution, and interactive charts.\\n- **Prediction:** estimate breach risk from submission-time request fields.\\n- **Dashboard:** queue review list, workload KPIs, and follow-up guidance.\\n- **System Design:** requirements, actors, use-case diagram, and decision workflow.")
    st.info("The included CSV is synthetic demonstration data because the uploaded midterm notebook generates fallback synthetic data when its expected CSV is absent. Replace it with your authorized midterm dataset before claiming empirical results.")

elif page == "Dataset":
    st.subheader("Dataset upload and validation")
    uploaded = st.file_uploader("Upload service request CSV", type=["csv"])
    if uploaded:
        try:
            raw = pd.read_csv(uploaded)
            st.write("Uploaded data preview"); st.dataframe(raw.head(30), use_container_width=True)
            cleaned, report = validate_and_clean(raw)
            st.session_state.service_df = cleaned; df = cleaned
            st.success("CSV loaded. Review the validation summary below."); st.json(report)
        except Exception as e: st.error(f"Could not read or validate this CSV: {e}")
    if not df.empty:
        st.write(f"Rows: **{len(df):,}** · Columns: **{len(df.columns)}**")
        st.dataframe(df.head(50), use_container_width=True)
        st.markdown("**Missing values by column**"); st.dataframe(df.isna().sum().rename("Missing values").to_frame())
        st.metric("Duplicate Request_ID rows", int(df["Request_ID"].duplicated().sum()) if "Request_ID" in df else int(df.duplicated().sum()))
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing: st.error("Required columns missing: " + ", ".join(missing))
        else: st.success("Required schema columns are present.")
        st.download_button("Download current dataset", df.to_csv(index=False).encode("utf-8"), "service_requests_checked.csv", "text/csv")
    else: st.info("Upload a CSV or use the bundled synthetic demo dataset.")

elif page == "Data Analysis":
    st.subheader("Exploratory data analysis")
    if df.empty: st.warning("No dataset loaded yet.")
    else: render_eda(df)

elif page == "Prediction":
    st.subheader("Predictive modeling")
    st.write("Enter values known when a request is submitted. Post-event fields are intentionally excluded.")
    try:
        model = load_model()
        with st.form("prediction_form"):
            a,b = st.columns(2)
            with a:
                service = st.selectbox("Service Type", ["Records","Certification","IT Support","Scholarship Inquiry"])
                requester = st.selectbox("Requester Type", ["Student","Faculty","Staff"])
                channel = st.selectbox("Requested Channel", ["Portal","Email","Walk-in"])
                priority = st.selectbox("Priority", ["Low","Normal","High"])
            with b:
                office = st.selectbox("Assigned Office", ["Registrar","IT Helpdesk","Cashier","Student Affairs"])
                queue = st.number_input("Queue Length", min_value=0, max_value=1000, value=8)
                docs = st.selectbox("Required Documents Complete", ["Yes","No"])
                sla = st.number_input("SLA Days", min_value=1, max_value=90, value=5)
            go = st.form_submit_button("Predict SLA breach risk")
        if go:
            row = {"Service_Type":service,"Requester_Type":requester,"Requested_Channel":channel,"Priority":priority,"Assigned_Office":office,"Queue_Length":queue,"Required_Documents_Complete":docs,"SLA_Days":sla}
            label, prob = predict_one(model,row)
            if label == 1: st.error("Model classification: HIGHER SLA-BREACH RISK")
            else: st.success("Model classification: LOWER SLA-BREACH RISK")
            if prob is not None: st.metric("Estimated breach probability", f"{prob:.1%}")
            reasons=[]
            if queue > 15: reasons.append("Queue length is above 15.")
            if docs == "No": reasons.append("Required documents are incomplete.")
            if office == "Registrar": reasons.append("Registrar assignment was identified as an influential feature in the report.")
            st.markdown("**Review prompts**")
            st.write(" ".join(reasons) if reasons else "No simple rule-based review prompt triggered; still follow normal staff review.")
            st.warning("This is a model estimate, not a guarantee. Staff must verify the request and decide the appropriate next action.")
    except Exception as e: st.error(f"Model could not be loaded: {e}")
    st.markdown("### Saved evaluation metrics")
    try: st.dataframe(model_metrics(), use_container_width=True)
    except Exception as e: st.caption(f"Metrics unavailable: {e}")

elif page == "Dashboard":
    st.subheader("Decision-support dashboard")
    if df.empty: st.warning("No dataset loaded yet.")
    else: render_dashboard(df)

elif page == "System Design":
    st.subheader("Systems Analysis and Design integration")
    st.markdown("### Functional requirements")
    reqs = [
      "The system shall show delay-risk alerts for requests with Queue_Length > 15 or office historical breach rates above 25%.",
      "The system shall predict using submission-time predictors only: Service_Type, Requester_Type, Requested_Channel, Priority, Assigned_Office, Queue_Length, Required_Documents_Complete, and SLA_Days.",
      "The system shall identify missing supporting-document information for staff follow-up.",
      "The system shall provide queue workload and SLA-risk summaries to authorized service staff.",
      "The system shall leave final prioritization, reassignment, and student communication decisions to authorized human staff."
    ]
    for i,r in enumerate(reqs,1): st.markdown(f"{i}. {r}")
    st.markdown("### Non-functional requirements")
    st.markdown("- **Privacy:** use synthetic or properly authorized data; do not publish identifiable student records.\\n- **Reliability:** validate uploads, show errors, and handle missing/unknown categories safely.\\n- **Explainability:** display model limitations and human-review guidance alongside predictions.")
    st.markdown("### Actors")
    st.markdown("- Student / Requester — submits a service request and tracks status.\\n- Department Administrator — reviews queue and risk flags.\\n- Predictive Analytics API — returns advisory risk predictions.")
    img = Path("assets/use_case_diagram.png")
    if img.exists(): st.image(str(img), caption="Provided use-case diagram", use_container_width=True)
    st.markdown("### Decision-support workflow")
    st.graphviz_chart("""
    digraph workflow {
      rankdir=LR; node [shape=box, style="rounded"];
      A [label="Submit request"]; B [label="Validate submission-time fields"];
      C [label="Load saved preprocessing + model"]; D [label="Predict SLA breach risk"];
      E [label="Show queue KPIs and risk flag"]; F [label="Staff reviews context"];
      G [label="Human decision: triage, reassign, or request documents"];
      A -> B -> C -> D -> E -> F -> G;
    }""")
    st.caption("Prediction output is advisory and must not automatically deny student services.")
