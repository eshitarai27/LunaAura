
import pandas as pd

files = {
    "Depression": "../dataset/raw/depression_dataset.csv",
    "Menstrual": "../dataset/raw/menstrual_cycle.csv",
    "Sleep": "../dataset/raw/sleep_lifestyle.csv",
    "Stress": "../dataset/raw/stress.csv"
}

for name, path in files.items():
    print("\n==============================")
    print(f"DATASET: {name}")
    print("==============================")
    
    df = pd.read_csv(path)
    
    print("\nShape:", df.shape)
    print("\nColumns:")
    print(df.columns.tolist())
    
    print("\nFirst 3 rows:")
    print(df.head(3))
