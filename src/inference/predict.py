import os
import joblib
import pandas as pd
import numpy as np

class LunaInference:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_dir = os.path.join(base_dir, "src", "models")
        
        # Load objects
        self.calibrated_clf = joblib.load(os.path.join(model_dir, "calibrated_classifier.pkl"))
        self.quantiles = joblib.load(os.path.join(model_dir, "phq_quantiles.pkl"))
        self.features = joblib.load(os.path.join(model_dir, "model_features.pkl"))

    def predict(self, input_dict):
        """
        Takes raw dictionary input and routes to ML models.
        """
        df_in = pd.DataFrame([input_dict])
        
        for col in self.features:
            if col not in df_in.columns:
                df_in[col] = np.nan
                
        df_in = df_in[self.features]
        
        # 1. Composite Risk Formula (Deterministic Override)
        sleep = float(input_dict.get("Sleep Duration", 7.0))
        stress = float(input_dict.get("Stress Level", 5.0))
        anxiety = float(input_dict.get("anxiety_level", 5.0))
        activity = float(input_dict.get("Physical Activity Level", 30.0))
        water = float(input_dict.get("water_intake", 2.0))
        
        stress_w = (stress / 10.0) * 35.0
        sleep_def = max(0.0, min(100.0, (8.0 - sleep) / 8.0 * 100.0))
        sleep_w = sleep_def * 0.25
        anxiety_w = (anxiety / 10.0) * 20.0
        act_def = max(0.0, min(100.0, (60.0 - activity) / 60.0 * 100.0))
        act_w = act_def * 0.10
        water_def = max(0.0, min(100.0, (2.5 - water) / 2.5 * 100.0))
        water_w = water_def * 0.05
        trend_w = 5.0 # baseline 5% nominal trend penalty
        
        cycle_day = int(input_dict.get("Cycle_Day", 14))
        gender = input_dict.get("Gender", "Female")
        phase_modifier = 0.0
        if gender == "Female":
            if cycle_day <= 5: phase_modifier = 5.0      # Menstrual mitigates risk slightly (natural fatigue)
            elif cycle_day <= 13: phase_modifier = -5.0  # Follicular increases baseline expectation
            elif cycle_day <= 16: phase_modifier = -8.0  # Ovulatory highly protective
            else: phase_modifier = 8.0                   # Luteal naturally elevates baseline risk

        composite_risk = stress_w + sleep_w + anxiety_w + act_w + water_w + trend_w + phase_modifier
        composite_risk = float(max(0, min(100, composite_risk)))

        # 2. Distributional Regression
        lower_bound = max(0, self.quantiles["q10"].predict(df_in)[0])
        phq_estimate = self.quantiles["q50"].predict(df_in)[0]
        upper_bound = min(27, self.quantiles["q90"].predict(df_in)[0])
        
        # Determine Severity ordinally via Custom Thresholds
        if composite_risk < 35: severity = "Low"
        elif composite_risk < 65: severity = "Moderate"
        else: severity = "High"
            
        return {
            "referral_probability": composite_risk / 100.0,
            "phq_point_estimate": float(phq_estimate),
            "confidence_interval": [float(lower_bound), float(upper_bound)],
            "predicted_severity": severity,
            "processed_input": df_in.iloc[0].to_dict()
        }
