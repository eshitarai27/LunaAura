from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import shap
import numpy as np
import pandas as pd

app = Flask(__name__)

# Enable CORS for all routes (simpler and more reliable for dev)
CORS(app)

# -----------------------------
# Load trained models
# -----------------------------
# Load best performing model (Gradient Boosting preferred)
try:
    rf_model = joblib.load("gb_depression_model.pkl")
except:
    rf_model = joblib.load("depression_model.pkl")

# Scaler is optional (tree models usually don't need it)
try:
    scaler = joblib.load("scaler.pkl")
except:
    scaler = None

# Create SHAP explainer once
explainer = shap.TreeExplainer(rf_model)

# -----------------------------
# Health check route
# -----------------------------
@app.route("/")
def home():
    return jsonify({"message": "Luna Aura Backend Running"})


# -----------------------------
# Prediction Route
# -----------------------------
@app.route("/predict", methods=["POST", "OPTIONS"])
def predict():

    # Handle browser CORS preflight request
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    try:
        data = request.get_json()

        # Features expected by the trained model (must match training dataset)
        expected_features = [
            "day_index",
            "age",
            "mood_score",
            "stress_level",
            "stress_cycle_interaction",
            "cycle_day",
            "hormone_intensity",
            "luteal_flag",
            "sleep_duration",
            "physical_activity",
            "stress_squared",
            "sleep_stress_ratio",
            "hormone_stress_interaction",
            "cycle_phase_luteal",
            "cycle_phase_menstrual",
            "cycle_phase_ovulatory"
        ]

        # Ensure all expected fields exist, default to 0 if missing or invalid
        cleaned = {}
        for f in expected_features:
            val = data.get(f, 0)

            try:
                cleaned[f] = float(val)
            except Exception:
                cleaned[f] = 0.0

        # Convert to DataFrame with correct column order
        input_df = pd.DataFrame([cleaned], columns=expected_features)

        # Apply scaler only if compatible (optional)
        if scaler is not None:
            try:
                scaled = scaler.transform(input_df)
                input_df = pd.DataFrame(scaled, columns=expected_features)
            except Exception:
                pass

        # Run prediction
        prediction = rf_model.predict(input_df)
        probability = rf_model.predict_proba(input_df)[0][1]

        # Normalize probability to safe range
        probability = max(0.0, min(1.0, float(probability)))

        # SHAP explanation
        shap_values = explainer.shap_values(input_df)

        # Handle SHAP output for binary classifiers
        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        # Map feature contributions
        feature_contributions = dict(
            zip(input_df.columns, shap_values[0])
        )

        # Sort top 3 drivers
        top_features = sorted(
            feature_contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:3]

        # Debug info (helps diagnose frontend issues)
        print("INPUT DATA:", cleaned)
        print("MODEL PROBABILITY:", probability)

        return jsonify({
            "prediction": int(prediction[0]),

            # More stable wellbeing computation
            "wellbeing_score": f"{int(max(0, min(100, (1 - probability) * 70 + (cleaned.get('sleep_duration', 0) * 2) + (cleaned.get('mood_score', 0) * 4) - (cleaned.get('stress_level', 0) * 3) - (cleaned.get('fatigue', 0) * 2))))}/100",

            # Risk probabilities derived from model probability
            "anxiety_risk": round(probability * 100, 2),
            "depression_prob": round(probability * 100, 2),
            "current_cycle_phase": (
                "Menstrual" if cleaned.get("cycle_day", 0) <= 7 else
                "Follicular" if cleaned.get("cycle_day", 0) <= 14 else
                "Ovulation" if cleaned.get("cycle_day", 0) <= 18 else
                "Luteal"
            ),
            "top_drivers": [
                {"feature": f, "impact": float(v)}
                for f, v in top_features
            ]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    # Run backend accessible to local frontend
    app.run(host="0.0.0.0", port=5000, debug=True)
