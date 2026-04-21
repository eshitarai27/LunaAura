import os
import joblib
import pandas as pd
import shap

class ExplainerSystem:
    def __init__(self, model_dir):
        # We load the Random Forest model designed for TreeExplainer compatibility
        self.shap_model = joblib.load(os.path.join(model_dir, "shap_classifier.pkl"))
        self.features = joblib.load(os.path.join(model_dir, "model_features.pkl"))
        self.explainer = shap.TreeExplainer(self.shap_model)

    def explain_instance(self, input_df):
        input_df = input_df[self.features].copy()
        
        # RF model needed NaNs imputed during training, so we impute here for SHAP
        input_df = input_df.fillna(input_df.median())
        
        shap_values = self.explainer.shap_values(input_df)
        
        # Scikit-learn RF generates list of arrays corresponding to classes
        # List index 1 is the positive 'Referral' class
        if isinstance(shap_values, list):
            sv = shap_values[1][0]
        elif len(shap_values.shape) == 3:
            # New shap behavior returns 3D array
            sv = shap_values[0, :, 1]
        else:
            sv = shap_values[0]
            
        feature_contributions = dict(zip(self.features, sv))
        top_factors = sorted(feature_contributions.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        
        nlg_text = self._generate_nlg(top_factors, input_df.iloc[0])
        return top_factors, nlg_text

    def _generate_nlg(self, top_factors, row_data):
        pos_drivers = [f[0] for f in top_factors if f[1] > 0]
        
        reasons = []
        if "Sleep Duration" in pos_drivers and row_data.get("Sleep Duration", 7) < 6:
            reasons.append("reduced sleep duration")
        if "Stress Level" in pos_drivers and row_data.get("Stress Level", 5) > 6:
            reasons.append("elevated physiological stress levels")
        if "Hormone_Proxy" in pos_drivers and row_data.get("Hormone_Proxy", 0) < -0.5:
             reasons.append("luteal phase variations")
             
        if not reasons:
            reasons = pos_drivers[:2]
            
        if reasons:
            explanation = f"Your current prediction is heavily influenced by {', '.join(reasons).replace('_', ' ').lower()}."
        else:
            explanation = "Your behavioral patterns appear stable overall."
            
        return explanation
