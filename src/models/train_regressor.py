import os
import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def train_and_save_regressor():
    print("--- Training LunaAura Quantile Regressors ---")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, "data", "processed", "master_dataset.csv")
    model_dir = os.path.join(base_dir, "src", "models")
    
    df = pd.read_csv(data_path)
    
    drop_cols = ["PHQ_Total", "PHQ_Severity", "Referral_Flag", "Tracking_Day"]
    
    X = df.drop(columns=[col for col in drop_cols if col in df.columns])
    X = X.select_dtypes(exclude=['object', 'category'])
    y = df["PHQ_Total"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Non-Parametric Distributional Modeling via Quantile Regression
    print("Training 10th Percentile (Lower Bound)...")
    q10 = HistGradientBoostingRegressor(loss='quantile', quantile=0.1, max_iter=150, random_state=42)
    q10.fit(X_train, y_train)
    
    print("Training 50th Percentile (Median Estimator)...")
    q50 = HistGradientBoostingRegressor(loss='quantile', quantile=0.5, max_iter=150, random_state=42)
    q50.fit(X_train, y_train)
    
    print("Training 90th Percentile (Upper Bound)...")
    q90 = HistGradientBoostingRegressor(loss='quantile', quantile=0.9, max_iter=150, random_state=42)
    q90.fit(X_train, y_train)
    
    preds = q50.predict(X_test)
    
    print("\n--- Regression Report (PHQ_Total 50th Quantile) ---")
    print(f"RMSE: {mean_squared_error(y_test, preds)**0.5:.2f}")
    print(f"R-squared: {r2_score(y_test, preds):.2f}")
    
    # Save objects
    joblib.dump({"q10": q10, "q50": q50, "q90": q90}, os.path.join(model_dir, "phq_quantiles.pkl"))
    
    print("Quantile Regressors saved successfully.")

if __name__ == "__main__":
    train_and_save_regressor()
