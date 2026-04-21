def get_recommendations(prediction_dict, raw_data=None):
    """
    Rules engine that actions both ML probabilities and extended form attributes.
    """
    if raw_data is None: raw_data = {}
    prob = prediction_dict["referral_probability"]
    severity = prediction_dict["predicted_severity"]
    
    recommendations = []
    
    # 1. Urgent Referral Gateway
    if prob >= 0.70 or severity in ["Moderately Severe", "Severe"]:
        recommendations.append({
            "type": "behavioral_alert",
            "priority": "HIGH",
            "message": "Your behavioral metrics suggest significant overload. Moderating baseline stress should be a primary concern."
        })
        
    # 2. Moderate Nudges
    elif prob >= 0.40 or severity == "Moderate":
        recommendations.append({
            "type": "behavioral",
            "priority": "MEDIUM",
            "message": "You are approaching a moderate risk threshold. Consider practicing cognitive decompression and increasing sleep consistency."
        })
        
    # 3. Healthy Baseline
    else:
        recommendations.append({
            "type": "maintenance",
            "priority": "LOW",
            "message": "Your current patterns reflect a stable baseline. Maintain your current routines."
        })
        
    # Check specific features if available
    inputs = prediction_dict.get("processed_input", {})
    sleep = dict(inputs).get("Sleep Duration", 7)
    stress = dict(inputs).get("Stress Level", 5)
    
    if sleep < 6:
        recommendations.append({
            "type": "lifestyle",
            "priority": "MEDIUM",
            "message": "Your logged sleep is below the 6-hour threshold. Increasing sleep architecture is the most impactful physiological intervention."
        })
        
    if stress > 7:
        recommendations.append({
            "type": "lifestyle",
            "priority": "MEDIUM",
            "message": "Elevated chronic stress detected. Introduce a 10-minute vagal-nerve stimulation exercise."
        })
        
    symptoms = raw_data.get("symptom_severity", 0)
    water = raw_data.get("water_intake", 4)
    
    if symptoms > 6:
        recommendations.append({
            "type": "symptom_tracking",
            "priority": "HIGH",
            "message": f"Symptom density ({symptoms}/10) is elevated. Reduce physical load until stabilization."
        })
        
    if water < 4:
        recommendations.append({
            "type": "nutrition",
            "priority": "MEDIUM",
            "message": f"Hydration ({water} cups) is sub-optimal. Aim for baseline +4 cups to stabilize cognitive tension."
        })
        
    return recommendations
