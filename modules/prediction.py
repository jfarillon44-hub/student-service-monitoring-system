from pathlib import Path
import json
import joblib
import pandas as pd
import streamlit as st

MODEL_PATH = Path("models/trained_model.joblib")
@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

def predict_one(model, row):
    from modules.data_processing import FEATURES
    x = pd.DataFrame([{k: row[k] for k in FEATURES}], columns=FEATURES)
    label = int(model.predict(x)[0])
    probability = None
    if hasattr(model, "predict_proba"):
        classes = list(model.classes_)
        if 1 in classes:
            probability = float(model.predict_proba(x)[0][classes.index(1)])
    return label, probability

def model_metrics():
    p=Path("models/model_metrics.json")
    return pd.DataFrame(json.loads(p.read_text()))
