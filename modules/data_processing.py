import pandas as pd
import numpy as np

REQUIRED_COLUMNS = ["Request_ID","Service_Type","Requester_Type","Requested_Channel","Priority","Assigned_Office","Queue_Length","Required_Documents_Complete","SLA_Days","Processing_Days","Status"]
FEATURES = ["Service_Type","Requester_Type","Requested_Channel","Priority","Assigned_Office","Queue_Length","Required_Documents_Complete","SLA_Days"]
CAT_COLS = ["Service_Type","Requester_Type","Requested_Channel","Priority","Assigned_Office","Required_Documents_Complete"]

def validate_and_clean(df):
    if df.empty:
        raise ValueError("The CSV contains no rows.")
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    df = df.copy()
    original_rows = len(df)
    duplicate_count = int(df["Request_ID"].duplicated().sum())
    df = df.drop_duplicates(subset=["Request_ID"], keep="first")
    for col in CAT_COLS + ["Status", "Reopened"]:
        if col in df:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip().str.title()
    df["Queue_Length"] = pd.to_numeric(df["Queue_Length"], errors="coerce")
    df["SLA_Days"] = pd.to_numeric(df["SLA_Days"], errors="coerce")
    if "Processing_Days" in df:
        df["Processing_Days"] = pd.to_numeric(df["Processing_Days"], errors="coerce")
    for col in ["Queue_Length", "SLA_Days", "Processing_Days"]:
        if col in df:
            df.loc[df[col] < 0, col] = np.nan
    for col in ["Queue_Length", "SLA_Days"]:
        median = df[col].median()
        df[col] = df[col].fillna(median if pd.notna(median) else 0)
    report = {
      "input_rows": original_rows, "output_rows": len(df),
      "duplicate_request_ids_removed": duplicate_count,
      "missing_values_after_cleaning": {str(k): int(v) for k,v in df.isna().sum().items()},
      "required_columns_present": True
    }
    return df, report
