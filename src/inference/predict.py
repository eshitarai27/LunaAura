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
        
        # 1. Classification (Referral Risk Probability)
        referral_prob = self.calibrated_clf.predict_proba(df_in)[0, 1]
        
        # 2. Distributional Regression
        lower_bound = max(0, self.quantiles["q10"].predict(df_in)[0])
        phq_estimate = self.quantiles["q50"].predict(df_in)[0]
        upper_bound = min(27, self.quantiles["q90"].predict(df_in)[0])
        
        # Determine Severity ordinally
        if phq_estimate < 5: severity = "Minimal"
        elif phq_estimate < 10: severity = "Mild"
        elif phq_estimate < 15: severity = "Moderate"
        elif phq_estimate < 20: severity = "Moderately Severe"
        else: severity = "Severe"
            
        return {
            "referral_probability": float(referral_prob),
            "phq_point_estimate": float(phq_estimate),
            "confidence_interval": [float(lower_bound), float(upper_bound)],
            "predicted_severity": severity,
            "processed_input": df_in.iloc[0].to_dict()
        }
