# Student Service Request Monitoring System

Streamlit app for student-service request dataset validation, exploratory analysis, advisory SLA-breach prediction, queue review, and SAD documentation.

## Run locally
1. Install Python 3.10 or 3.11.
2. Extract this folder and open a terminal in it.
3. Create/activate a virtual environment (recommended).
4. Run `pip install -r requirements.txt`.
5. Run `streamlit run app.py`.

## Pages
Home, Dataset, Data Analysis, Prediction, Dashboard, System Design.

## Model and data provenance — read before submission
The uploaded `Midterm_Examanition.ipynb` expects `student_service_requests.csv`, but that dataset was not included with the uploaded files. Its notebook generates synthetic fallback data when that CSV is missing. To make this package runnable, the included demo CSV and `models/trained_model.joblib` were generated from synthetic demonstration records using the notebook's documented feature list and a Decision Tree pipeline. This is a runnable scaffold, **not a verified reproduction of the original midterm model or the PDF's reported metrics**. The generated model's evaluation metrics are in `models/model_metrics.json`. Replace the demo dataset/model with your actual authorized midterm dataset and saved pipeline before reporting real-world results.

The PDF reports Decision Tree metrics of accuracy 84.50%, class-1 precision 78.20%, recall 71.40%, and F1 0.7463. Those values are preserved in the source report, but were not independently reproduced because the original CSV was not supplied.

## Input features
`Service_Type`, `Requester_Type`, `Requested_Channel`, `Priority`, `Assigned_Office`, `Queue_Length`, `Required_Documents_Complete`, `SLA_Days`.

Post-event fields such as `Processing_Days`, `Status`, `Reopened`, and `Satisfaction_Score` are excluded from model inference to reduce leakage risk.

## Deploy to Streamlit Community Cloud
1. Create a GitHub repository and upload the project files.
2. Visit https://share.streamlit.io and sign in.
3. Create an app, select the repository and branch, set main file to `app.py`, then deploy.
4. Check the deployed URL and logs. Add the actual repository and deployed URLs to your submission after publishing.

## Privacy and limitations
Use synthetic or properly authorized data only for public deployment. Risk scores are advisory, can be wrong, and must not automatically deny services. The model is trained on synthetic demonstration data until replaced with the original midterm dataset.
