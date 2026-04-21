import os
import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, roc_auc_score, brier_score_loss

def train_and_save_classifier():
    print("--- Training LunaAura Classifier ---")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, "data", "processed", "master_dataset.csv")
    model_dir = os.path.join(base_dir, "src", "models")
    
    df = pd.read_csv(data_path)
    
    drop_cols = ["PHQ_Total", "PHQ_Severity", "Referral_Flag", "Tracking_Day"]
    
    X = df.drop(columns=[col for col in drop_cols if col in df.columns])
    X = X.select_dtypes(exclude=['object', 'category'])
    y = df["Referral_Flag"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    
    base_model = HistGradientBoostingClassifier(max_iter=100, max_leaf_nodes=31, learning_rate=0.05, random_state=42)
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    calibrated_clf = CalibratedClassifierCV(estimator=base_model, method='sigmoid', cv=cv)
    calibrated_clf.fit(X_train, y_train)
    
    preds = calibrated_clf.predict(X_test)
    probs = calibrated_clf.predict_proba(X_test)[:, 1]
    
    print("\n--- Classification Report (Referral_Flag) ---")
    print(classification_report(y_test, preds))
    print(f"ROC AUC Score: {roc_auc_score(y_test, probs):.4f}")
    
    brier = brier_score_loss(y_test, probs)
    print(f"Brier Score (Calibration error, lower is better): {brier:.4f}")
    
    # SHAP Proxy Model
    X_imputed = X.fillna(X.median())
    shap_model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    shap_model.fit(X_imputed, y)
    
    joblib.dump(calibrated_clf, os.path.join(model_dir, "calibrated_classifier.pkl"))
    joblib.dump(shap_model, os.path.join(model_dir, "shap_classifier.pkl"))
    joblib.dump(list(X.columns), os.path.join(model_dir, "model_features.pkl"))
    
    print("Models saved successfully.")

if __name__ == "__main__":
    train_and_save_classifier()
