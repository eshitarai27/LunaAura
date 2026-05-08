import os
import sqlite3
import pandas as pd
import numpy as np
import joblib
import shap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Load Data
conn = sqlite3.connect('/Users/prashantkumar/Desktop/Luna_Aura/data/lunaaura.db')
hist = pd.read_sql("SELECT * FROM user_history", conn)
conn.close()

# Prepare Data
hist['sleep_duration'] = pd.to_numeric(hist['sleep_duration'], errors='coerce')
hist['stress_level']   = pd.to_numeric(hist['stress_level'],   errors='coerce')
hist['activity']       = pd.to_numeric(hist['activity'],       errors='coerce')
hist['risk_num'] = hist['predicted_risk'].str.replace('%','').astype(float, errors='ignore')
hist['risk_num'] = pd.to_numeric(hist['risk_num'], errors='coerce')

eval_df = hist[['sleep_duration','stress_level','activity','risk_num']].dropna()
eval_df = eval_df[eval_df['risk_num'] <= 100]

# Load model
model_dir = '/Users/prashantkumar/Desktop/Luna_Aura/src/models'
clf = joblib.load(os.path.join(model_dir, 'calibrated_classifier.pkl'))
features = joblib.load(os.path.join(model_dir, 'model_features.pkl'))

# Build compatible feature frame
X_sim = pd.DataFrame({
    'Age': np.random.randint(18, 55, len(eval_df)),
    'Sleep Duration': eval_df['sleep_duration'].values,
    'Stress Level': eval_df['stress_level'].values,
    'Physical Activity Level': eval_df['activity'].values,
    'Base_Cycle_Length': np.random.randint(25, 35, len(eval_df)).astype(float),
    'Cycle_Day': np.random.randint(1, 28, len(eval_df)).astype(float),
})
for f in features:
    if f not in X_sim.columns:
        X_sim[f] = 0.0
X_sim = X_sim[features].fillna(0)

# Extract base estimator (RandomForestClassifier) for SHAP
try:
    base_clf = clf.calibrated_classifiers_[0].estimator
except:
    base_clf = clf # fallback if not calibrated

# Compute SHAP values
explainer = shap.TreeExplainer(base_clf)
shap_values = explainer.shap_values(X_sim)

# For binary classification, shap_values might be a list of arrays (one per class). We want the positive class (1).
if isinstance(shap_values, list):
    shap_vals_to_plot = shap_values[1]
else:
    shap_vals_to_plot = shap_values

# Plot
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_vals_to_plot, X_sim, plot_type="bar", show=False, color="#7C3AED")
plt.title("SHAP Feature Importance (Average Impact on Model Output Magnitude)", fontweight='bold', fontsize=12, pad=20)
plt.tight_layout()

# Save
out_path = '/Users/prashantkumar/Desktop/Luna_Aura/paper_assets/shap_feature_importance.png'
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"SHAP graph saved to {out_path}")
