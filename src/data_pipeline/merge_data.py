import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

def perform_statistical_matching(df_primary, df_donor, match_cols, donor_cols):
    """
    Matches records from df_primary to the closest demographic neighbor in df_donor.
    """
    primary = df_primary.copy()
    donor = df_donor.copy()
    
    # Filter out NaNs in match spaces
    donor = donor.dropna(subset=match_cols)
    primary_clean = primary.dropna(subset=match_cols)
    
    if len(donor) == 0 or len(primary_clean) == 0:
        for c in donor_cols:
            primary[c] = np.nan
        return primary
        
    # Scale match variables simply for KNN
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_donor = scaler.fit_transform(donor[match_cols])
    X_primary = scaler.transform(primary_clean[match_cols])
    
    # Fit KNN
    knn = NearestNeighbors(n_neighbors=1, algorithm='auto')
    knn.fit(X_donor)
    
    distances, indices = knn.kneighbors(X_primary)
    
    # Fetch donor values
    matched_values = donor.iloc[indices.flatten()][donor_cols].reset_index(drop=True)
    
    # Reassign
    for i, col in enumerate(donor_cols):
        primary.loc[primary_clean.index, col] = matched_values[col].values
        
    return primary

def generate_cycle_history(df):
    """
    For Female participants, simulate 1-30 days cycle distribution using realistic cycle lengths.
    Builds temporal dynamics using rolling statistical aggregates to capture behavioral momentum.
    """
    all_user_records = []
    
    for idx, row in df.iterrows():
        base_cycle = row.get("Base_Cycle_Length", 28)
        if pd.isna(base_cycle):
             base_cycle = 28.0
             
        start_day = np.random.randint(1, int(base_cycle) + 1)
        user_timeline = []
        
        # Base stats for this user
        base_sleep = row.get("Sleep Duration", 7)
        base_stress = row.get("Stress Level", 5)
        
        for t in range(1, 15):
            day_log = dict(row)
            day_log["Tracking_Day"] = t
            
            if row["Gender"] == "Female":
                cycle_day = ((start_day + t - 1) % int(base_cycle)) + 1
                if cycle_day <= 5: phase = "Menstrual"
                elif cycle_day <= 13: phase = "Follicular"
                elif cycle_day <= 16: phase = "Ovulatory"
                else: phase = "Luteal"
                hormone = np.sin(2 * np.pi * cycle_day / base_cycle)
            else:
                cycle_day = 0
                phase = "N/A"
                hormone = 0.0
                
            day_log["Cycle_Day"] = cycle_day
            day_log["Cycle_Phase"] = phase
            day_log["Hormone_Proxy"] = hormone
            
            # Simulated variance
            if not pd.isna(base_sleep):
                day_log["Sleep Duration"] = base_sleep + np.random.normal(0, 0.7)
            if not pd.isna(base_stress):
                day_log["Stress Level"] = base_stress + np.random.normal(0, 0.5)
                
            user_timeline.append(day_log)
            
        user_df = pd.DataFrame(user_timeline)
        
        # Temporal Momentum Extraction (Feature Engineering Novelty)
        user_df["Sleep_Rolling_Mean_3d"] = user_df["Sleep Duration"].rolling(window=3, min_periods=1).mean()
        user_df["Stress_Rolling_Mean_3d"] = user_df["Stress Level"].rolling(window=3, min_periods=1).mean()
        user_df["Stress_Volatility_3d"] = user_df["Stress Level"].rolling(window=3, min_periods=1).std().fillna(0)
        
        all_user_records.append(user_df)
            
    return pd.concat(all_user_records, ignore_index=True)

def create_master_dataset(df_dep, df_sleep_donor, df_cycle_map):
    """
    Orchestrates the statistical merge matching and time-series expansion.
    """
    # 1. Base dataset is depression dataset (preserves real clinical target)
    master = df_dep.copy()
    
    # Enhance depression data with an encoded Gender map for k-NN
    master["Gender_Code"] = (master["Gender"] == "Female").astype(int)
    df_sleep_donor["Gender_Code"] = (df_sleep_donor["Gender"] == "Female").astype(int)
    
    # 2. Match Sleep features based on Demographics (Age, Gender)
    donor_cols = ["Sleep Duration", "Physical Activity Level", "Stress Level"]
    match_cols = ["Age", "Gender_Code"]
    master = perform_statistical_matching(master, df_sleep_donor, match_cols, donor_cols)
    
    # 3. Match Cycle Length map for Females exactly based on Age
    master = pd.merge(master, df_cycle_map, on="Age", how="left")
    
    # 4. Expand into 14-day temporal logs yielding cyclic dynamics
    master_expanded = generate_cycle_history(master)
    
    # Clean up and ensure features
    master_expanded.drop(columns=["Gender_Code"], inplace=True)
    master_expanded["Stress Level"] = np.clip(master_expanded["Stress Level"], 1, 10)
    master_expanded["Sleep Duration"] = np.clip(master_expanded["Sleep Duration"], 2, 14)
    
    return master_expanded
