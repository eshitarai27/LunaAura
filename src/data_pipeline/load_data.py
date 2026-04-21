import pandas as pd
import os

def load_raw_data(data_dir="data/raw"):
    """
    Loads the unprocessed source datasets.
    """
    depression_path = os.path.join(data_dir, "depression_dataset.csv")
    sleep_path = os.path.join(data_dir, "sleep_lifestyle.csv")
    cycle_path = os.path.join(data_dir, "menstrual_cycle.csv")
    
    # Strip column whitespaces immediately
    df_dep = pd.read_csv(depression_path)
    df_dep.columns = df_dep.columns.str.strip()
    
    df_sleep = pd.read_csv(sleep_path)
    df_sleep.columns = df_sleep.columns.str.strip()
    
    df_cycle = pd.read_csv(cycle_path)
    df_cycle.columns = df_cycle.columns.str.strip()
    
    return df_dep, df_sleep, df_cycle
