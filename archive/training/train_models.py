import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    mean_squared_error,
    r2_score
)

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    RandomForestRegressor,
    GradientBoostingRegressor
)
from sklearn.svm import SVC


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv("../dataset/processed/master_dataset.csv")
print("Dataset shape:", df.shape)

# --------------------------------------------------
# FEATURE ENGINEERING (IMPROVES MODEL ACCURACY)
# --------------------------------------------------

# Sleep deviation from optimal (7 hours baseline)
if "sleep_duration" in df.columns:
    df["sleep_deviation"] = abs(df["sleep_duration"] - 7)

# Stress × sleep interaction (captures fatigue dynamics)
if "stress_level" in df.columns and "sleep_duration" in df.columns:
    df["stress_sleep_product"] = df["stress_level"] * df["sleep_duration"]

# Fatigue proxy from stress and sleep imbalance
if "stress_level" in df.columns and "sleep_duration" in df.columns:
    df["fatigue_proxy"] = df["stress_level"] / (df["sleep_duration"] + 1)

# Hormone interaction stabilizer
if "hormone_intensity" in df.columns and "stress_level" in df.columns:
    df["hormone_stress_balance"] = df["hormone_intensity"] / (df["stress_level"] + 1)

# Encode categorical variables
df = pd.get_dummies(df, columns=["cycle_phase"], drop_first=True)

# --------------------------------------------------
# DEFINE FEATURES & TARGETS
# --------------------------------------------------

X = df.drop(columns=[
    "user_id",
    "gender",
    "depression_flag",
    "wellbeing_score",
])

print("\nNaN count per column BEFORE cleaning:")
print(X.isna().sum())

y_depression = df["depression_flag"]
y_wellbeing = df["wellbeing_score"]

# --------------------------------------------------
# TRAIN-TEST SPLIT (FAIR SPLIT FOR ALL MODELS)
# --------------------------------------------------

X_train, X_test, y_train_d, y_test_d = train_test_split(
    X,
    y_depression,
    test_size=0.2,
    random_state=42,
    stratify=y_depression
)

X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
    X, y_wellbeing,
    test_size=0.2,
    random_state=42
)

# --------------------------------------------------
# SCALE FEATURES (FOR LINEAR MODELS + SVM)
# --------------------------------------------------

# IMPORTANT: Fit scaler only on training data to avoid data leakage
scaler = StandardScaler()

# Classification scaling
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Regression scaling (use a separate scaler to avoid overwriting)
scaler_reg = StandardScaler()
X_train_r_scaled = scaler_reg.fit_transform(X_train_r)
X_test_r_scaled = scaler_reg.transform(X_test_r)

# --------------------------------------------------
# RESULTS STORAGE
# --------------------------------------------------

classification_results = []
regression_results = []

def evaluate_classification(name, model, X_test, y_test):
    preds = model.predict(X_test)
    classification_results.append({
        "Model": name,
        "Accuracy": accuracy_score(y_test, preds),
        "Precision": precision_score(y_test, preds, zero_division=0),
        "Recall": recall_score(y_test, preds, zero_division=0),
        "F1 Score": f1_score(y_test, preds, zero_division=0)
    })

def evaluate_regression(name, model, X_test, y_test):
    preds = model.predict(X_test)
    regression_results.append({
        "Model": name,
        "RMSE": np.sqrt(mean_squared_error(y_test, preds)),
        "R2 Score": r2_score(y_test, preds)
    })


# ==================================================
# TASK 1 — DEPRESSION CLASSIFICATION
# ==================================================

# Logistic Regression
log_model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    solver="lbfgs"
)
log_model.fit(X_train_scaled, y_train_d)
evaluate_classification("Logistic Regression", log_model, X_test_scaled, y_test_d)

# Random Forest
rf_model = RandomForestClassifier(
    n_estimators=400,
    max_depth=None,
    min_samples_split=4,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train_d)
evaluate_classification("Random Forest", rf_model, X_test, y_test_d)

# Gradient Boosting
gb_model = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=3,
    random_state=42
)
gb_model.fit(X_train, y_train_d)
evaluate_classification("Gradient Boosting", gb_model, X_test, y_test_d)

# SVM
svm_model = SVC(probability=True, kernel="rbf", C=1.0, gamma="scale")
svm_model.fit(X_train_scaled, y_train_d)
evaluate_classification("SVM", svm_model, X_test_scaled, y_test_d)


classification_df = pd.DataFrame(classification_results)
print("\n=== Classification Results ===")
print(classification_df)

classification_df.to_csv("classification_results.csv", index=False)


# ==================================================
# TASK 2 — WELLBEING REGRESSION
# ==================================================

# Linear Regression
lr = LinearRegression()
lr.fit(X_train_r_scaled, y_train_r)
evaluate_regression("Linear Regression", lr, X_test_r_scaled, y_test_r)

# Random Forest Regressor
rf_reg = RandomForestRegressor(
    n_estimators=300,
    max_depth=None,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
rf_reg.fit(X_train_r, y_train_r)
evaluate_regression("Random Forest Regressor", rf_reg, X_test_r, y_test_r)

# Gradient Boosting Regressor
gb_reg = GradientBoostingRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=3,
    random_state=42
)
gb_reg.fit(X_train_r, y_train_r)
evaluate_regression("Gradient Boosting Regressor", gb_reg, X_test_r, y_test_r)


regression_df = pd.DataFrame(regression_results)
print("\n=== Regression Results ===")
print(regression_df)

regression_df.to_csv("regression_results.csv", index=False)


# ==================================================
# CROSS VALIDATION (ROBUSTNESS)
# ==================================================

cv_scores = cross_val_score(rf_model, X, y_depression, cv=5, scoring="accuracy", n_jobs=-1)
print("\nRandom Forest 5-Fold CV Accuracy:", cv_scores.mean())


# ==================================================
# EXPERIMENT — WITH VS WITHOUT CYCLE FEATURES
# ==================================================

cycle_cols = [col for col in X.columns if "cycle" in col or "luteal" in col]

X_no_cycle = X.drop(columns=cycle_cols)

X_train_nc, X_test_nc, y_train_nc, y_test_nc = train_test_split(
    X_no_cycle, y_depression,
    test_size=0.2,
    random_state=42
)

rf_nc = RandomForestClassifier(n_estimators=100, random_state=42)
rf_nc.fit(X_train_nc, y_train_nc)

acc_no_cycle = accuracy_score(y_test_nc, rf_nc.predict(X_test_nc))
acc_with_cycle = accuracy_score(y_test_d, rf_model.predict(X_test))

print("\n=== Cycle Feature Impact ===")
print("Accuracy without cycle:", acc_no_cycle)
print("Accuracy with cycle:", acc_with_cycle)
print("Improvement:", acc_with_cycle - acc_no_cycle)


# ==================================================
# SAVE BEST MODELS
# ==================================================

joblib.dump(rf_model, "depression_model.pkl")
joblib.dump(rf_reg, "wellbeing_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("\nModels saved successfully.")



# ==================================================
# PHASE 6 — EXPLAINABLE AI (SHAP)
# ==================================================

import shap
import numpy as np

print("\nGenerating SHAP explanations...")

X_sample = X_test.sample(500, random_state=42)

explainer = shap.TreeExplainer(rf_model)

shap_values = explainer.shap_values(X_sample)

# Handle new SHAP output format (3D array)
if isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
    # Select class 1 (depression)
    shap_values = shap_values[:, :, 1]

print("Final SHAP shape:", shap_values.shape)
print("X_sample shape:", X_sample.shape)

# Beeswarm
shap.summary_plot(shap_values, X_sample)

# Bar importance
shap.summary_plot(shap_values, X_sample, plot_type="bar")
