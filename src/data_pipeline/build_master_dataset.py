"""
Master Orchestrator for Data Pipeline.
Run this script to rebuild mapping from raw files.
"""

import os
import pandas as pd
from load_data import load_raw_data
from preprocess import clean_depression_data, clean_sleep_data, process_cycle_data
from merge_data import create_master_dataset

def main():
    print("--- LunaAura: Building Master Dataset ---")
    
    # Define paths
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_dir = os.path.join(base_dir, "data", "raw")
    processed_dir = os.path.join(base_dir, "data", "processed")
    
    os.makedirs(processed_dir, exist_ok=True)
    
    print(f"Loading raw data from {raw_dir}...")
    df_dep_raw, df_sleep_raw, df_cycle_raw = load_raw_data(data_dir=raw_dir)
    
    print("Cleaning data components...")
    df_dep = clean_depression_data(df_dep_raw)
    df_sleep = clean_sleep_data(df_sleep_raw)
    df_cycle_map = process_cycle_data(df_cycle_raw)
    
    print("Performing statistical matching & temporal expansion...")
    master_df = create_master_dataset(df_dep, df_sleep, df_cycle_map)
    
    output_path = os.path.join(processed_dir, "master_dataset.csv")
    master_df.to_csv(output_path, index=False)
    
    print(f"Master Dataset created successfully. Saved to {output_path}")
    print(f"Final shape: {master_df.shape}")
    
    # Brief stats 
    print(f"Target Distribution (PHQ_Severity):\n{master_df['PHQ_Severity'].value_counts(normalize=True)}")

if __name__ == "__main__":
    main()
