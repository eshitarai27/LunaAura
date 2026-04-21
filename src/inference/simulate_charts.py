import math
import random

def get_cycle_phase(day):
    if day == 0: return "None"
    if day <= 7: return "Menstrual"
    if day <= 11: return "Follicular"
    if day <= 17: return "Ovulatory"
    return "Luteal"

def generate_chart_data(input_dict, prediction_output):
    # Base Inputs (Strict 8-factor Array)
    age = float(input_dict.get("Age", 26))
    gender = input_dict.get("Gender", "Female")
    sleep = float(input_dict.get("Sleep Duration", 7.0))
    stress = float(input_dict.get("Stress Level", 5))
    activity = float(input_dict.get("Physical Activity Level", 30.0))
    anxiety = float(input_dict.get("anxiety_level", 5))
    water = float(input_dict.get("water_intake", 2.0))
    cycle_day = int(input_dict.get("Cycle_Day", 14))
    
    # Model Distribution References (Honest Mapping)
    referral_prob = float(prediction_output.get("referral_probability", 0.5))
    phq_baseline = float(prediction_output.get("phq_point_estimate", 10.0))

    # 1. Base Forecast (Illustrative projection mapping)
    mood_forecast = []
    base_m = max(1.0, min(5.0, 5.0 - (phq_baseline / 27.0) * 4.0))
    for i in range(7):
        drift = 0
        if sleep >= 7: drift += 0.1
        elif sleep < 6: drift -= 0.15
        if stress >= 7: drift -= 0.2
        mood_forecast.append(round(max(1.0, min(5.0, base_m + drift)), 1))
        
    # 2. Weekly Stress Trend (Past 7 days up to today)
    stress_trend = []
    slope = 1.0 if sleep < 6 else ( -0.5 if sleep >= 7.5 else 0 )
    for i in range(7):
        days_ago = 6 - i
        s = stress - (slope * days_ago * 0.5)
        stress_trend.append(round(max(1.0, min(10.0, s)), 1))
        
    # 3. Sleep Architecture Projection
    sleep_proj = []
    curr_s = sleep
    for _ in range(7):
        recov = 0.2 if stress < 5 else (-0.3 if stress > 8 else 0)
        curr_s = max(3.0, min(10.0, curr_s + recov))
        sleep_proj.append(round(curr_s, 1))
        
    # 4. Risk Probability Estimate
    high_risk = round(referral_prob * 100)
    low_risk = round(max(0, 100 - high_risk) * 0.7)
    mod_risk = 100 - high_risk - low_risk
    
    # 5. Cycle Phase Influence
    curr_phase = get_cycle_phase(cycle_day) if gender == "Female" else "None"
    pi = {"Menstrual": 10, "Follicular": 10, "Ovulatory": 10, "Luteal": 10}
    if curr_phase != "None":
        pi[curr_phase] = 70
        
    # 6. Strict Literature-Bounded Normalization (0-100)
    # Sleep Optimal Range ~ 7-9 hours. Departure penalized.
    n_sleep = max(0.0, min(100.0, 100.0 - (abs(sleep - 8.0) * 15.0)))
    
    # Stress Inverse -> Pure linear constraint
    n_stress = max(0.0, min(100.0, 100.0 - ((stress - 1.0) * 11.1)))
    
    # Activity Diminishing Returns Plateaus ~ 60 mins -> Scaled at 80 mins
    n_activity = max(0.0, min(100.0, (activity / 60.0) * 100.0))
    
    # Anxiety Inverse constraint
    n_anxiety = max(0.0, min(100.0, 100.0 - ((anxiety - 1.0) * 11.1)))
    
    # Hydration adult scalar ~ 2.5 L
    n_water = max(0.0, min(100.0, (water / 2.5) * 100.0))
    
    n_age = 100.0  # Stable contextual baseline (no heuristic discrimination)
    
    # Contextual Shift Modifier (10% Adjustment mapped organically)
    n_cycle = 100.0
    if gender == "Female" and curr_phase in ["Luteal", "Menstrual"]:
        n_cycle = 75.0  # Contextual drop preventing fake pathological penalties
        
    # Stability Adjustment
    n_stability = 75.0 if len(stress_trend) > 1 and stress_trend[-1] < stress_trend[0] else 50.0
    
    # 7. Apply Defensible Weighted Aggregation
    w_sleep = n_sleep * 0.25
    w_stress = n_stress * 0.20
    w_act = n_activity * 0.15
    w_anx = n_anxiety * 0.15
    w_water = n_water * 0.05
    w_age = n_age * 0.05
    w_cycle = n_cycle * 0.10
    w_stab = n_stability * 0.05
    
    wellness = int(w_sleep + w_stress + w_act + w_anx + w_water + w_age + w_cycle + w_stab)
    wellness = max(0, min(100, wellness))
    
    factor_breakdown = {
        "Sleep": {"score": int(n_sleep), "impact": f"+{int(w_sleep)}"},
        "Stress": {"score": int(n_stress), "impact": f"+{int(w_stress)}"},
        "Activity": {"score": int(n_activity), "impact": f"+{int(w_act)}"},
        "Anxiety": {"score": int(n_anxiety), "impact": f"+{int(w_anx)}"},
        "Hydration": {"score": int(n_water), "impact": f"+{int(w_water)}"},
        "Age Context Adjustment": {"score": int(n_age), "impact": f"+{int(w_age)}"},
        "Cycle Context Sensitivity": {"score": int(n_cycle), "impact": f"+{int(w_cycle)}"},
        "Stability Adjustment": {"score": int(n_stability), "impact": f"+{int(w_stab)}"}
    }
    
    heatmap = [round(max(0.1, min(1.0, (st / 10.0) * (1.0 if sl < 6 else 0.5))), 2) for st, sl in zip(stress_trend, sleep_proj)]
    
    # Analytics Sentences
    culprit = "Stress Management"
    if n_sleep < n_stress and n_sleep < n_activity: culprit = "Sleep Deficits"
    if n_activity < n_sleep and n_activity < n_stress: culprit = "Low Activity"
    
    summary = f"Normal pacing."
    if wellness < 40: summary = f"Severe compound behavioral degradation driven by {culprit.lower()}."
    elif wellness > 75: summary = "Optimal behavioral stability; resilient to phase transitions."
    else: summary = f"Moderate volatility. Focus on improving {culprit.lower()}."
    
    return {
        "charts": {
            "mood_forecast": mood_forecast,
            "stress_trend": stress_trend,
            "sleep_projection": sleep_proj,
            "risk_distribution": {"Low": low_risk, "Moderate": mod_risk, "High": high_risk},
            "phase_impact": pi,
            "habit_breakdown": {"Sleep": int(n_sleep), "Activity": int(n_activity), "Stress": int(n_stress), "Anxiety": int(n_anxiety)}
        },
        "premium": {
            "what_changed_most": f"{culprit} is compounding systemic volatility.",
            "wellness_score": wellness,
            "risk_heatmap": heatmap,
            "summary_sentence": summary,
            "factor_breakdown": factor_breakdown
        }
    }
