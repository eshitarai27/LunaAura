import pandas as pd
import numpy as np

def clean_depression_data(df):
    """
    Ensures PHQ_Total and numeric columns are clean.
    Creates the true target 'PHQ_Severity' uniformly.
    """
    df = df.copy()
    
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df["Gender"] = df["Gender"].astype(str).str.strip().str.title()
    df["PHQ_Total"] = pd.to_numeric(df["PHQ_Total"], errors="coerce")
    
    # Drop rows without our ground truth target
    df = df.dropna(subset=["PHQ_Total"])
    
    # Re-standardize severity band just in case it was incorrectly labeled
    bins = [-1, 4, 9, 14, 19, 30]
    labels = ["Minimal", "Mild", "Moderate", "Moderately Severe", "Severe"]
    df["PHQ_Severity"] = pd.cut(df["PHQ_Total"], bins=bins, labels=labels)
    
    # Impute missing Ages using median
    df["Age"] = df["Age"].fillna(df["Age"].median())
    
    # Encode binary target for referral
    df["Referral_Flag"] = (df["PHQ_Total"] >= 10).astype(int)
    
    return df

def clean_sleep_data(df):
    """
    Cleans sleep and lifestyle data.
    """
    df = df.copy()
    df["Gender"] = df["Gender"].astype(str).str.strip().str.title()
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df["Sleep Duration"] = pd.to_numeric(df["Sleep Duration"], errors="coerce")
    df["Physical Activity Level"] = pd.to_numeric(df["Physical Activity Level"], errors="coerce")
    df["Stress Level"] = pd.to_numeric(df["Stress Level"], errors="coerce")
    
    df = df.dropna(subset=["Age", "Gender"])
    return df

def process_cycle_data(df):
    """
    Extracts mean cycle length characteristics for mapping.
    """
    df = df.copy()
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["cycle_length"] = pd.to_numeric(df["cycle_length"], errors="coerce")
    
    df = df.dropna(subset=["age", "cycle_length"])
    
    # Aggregate cycle lengths by age to provide a realistic map
    cycle_map = df.groupby("age")["cycle_length"].mean().reset_index()
    cycle_map.rename(columns={"age": "Age", "cycle_length": "Base_Cycle_Length"}, inplace=True)
    
    return cycle_map
