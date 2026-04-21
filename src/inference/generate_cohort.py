import random
import uuid
from datetime import datetime, timedelta

def generate_pseudo_cohort():
    """Generates 100 realistic pseudo-users with a fixed random seed."""
    random.seed(42)
    cohort = []
    
    # Distributions
    profiles = [
        {"risk": "High", "count": 30, "sleep_range": (3, 5.5), "stress_range": (7, 10), "act_range": (0, 20)},
        {"risk": "Moderate", "count": 40, "sleep_range": (5.5, 7), "stress_range": (4, 7), "act_range": (20, 60)},
        {"risk": "Low", "count": 30, "sleep_range": (7, 9), "stress_range": (1, 4), "act_range": (60, 120)}
    ]
    
    now = datetime.now()
    
    for p in profiles:
        for _ in range(p["count"]):
            age = random.randint(18, 55)
            sleep = round(random.uniform(*p["sleep_range"]), 1)
            stress = random.randint(*p["stress_range"])
            activity = random.randint(*p["act_range"])
            cycle_day = random.randint(0, 28)
            
            # Phase
            if cycle_day == 0: phase = "Unknown/Male"
            elif cycle_day <= 7: phase = "Menstrual"
            elif cycle_day <= 11: phase = "Follicular"
            elif cycle_day <= 17: phase = "Ovulatory"
            else: phase = "Luteal"
                
            # Mood Mapping (Inverse to Risk)
            if p["risk"] == "High": mood = round(random.uniform(1.0, 2.5), 1)
            elif p["risk"] == "Moderate": mood = round(random.uniform(2.5, 4.0), 1)
            else: mood = round(random.uniform(4.0, 5.0), 1)
                
            # Wellness Score calculation matching UI logic
            h_sleep = max(0, min(100, int((sleep / 8.0) * 100)))
            h_act = max(0, min(100, int((activity / 60.0) * 100)))
            h_str = max(0, min(100, int(((10 - stress) / 10.0) * 100)))
            h_mood = max(0, min(100, int((mood / 5.0) * 100)))
            wellness = int((h_sleep + h_act + h_str + h_mood) / 4)
            
            # Prediction Target
            pred_risk = 100 - wellness + random.randint(-5, 5)
            
            record = {
                "id": str(uuid.uuid4())[:8],
                "age": age,
                "sleep_duration": sleep,
                "stress_level": stress,
                "activity": activity,
                "cycle_day": cycle_day,
                "phase": phase,
                "mood_score": mood,
                "predicted_risk": min(100, max(0, pred_risk)),
                "wellness_score": min(100, max(0, wellness)),
                "cohort_group": p["risk"],
                "source": "synthetic",
                "timestamp": (now - timedelta(days=random.randint(0, 30))).isoformat()
            }
            cohort.append(record)
            
    # Shuffle the set deterministically
    random.shuffle(cohort)
    return cohort

# In-memory singleton caching
COHORT_DATA = generate_pseudo_cohort()

def get_cohort():
    return COHORT_DATA

def get_analytics_aggregations():
    cohort = COHORT_DATA
    # Avgs
    avg_wellness = sum(r["wellness_score"] for r in cohort) / 100
    avg_stress = sum(r["stress_level"] for r in cohort) / 100
    
    # Phase Breakdown
    phases = {"Menstrual": 0, "Follicular": 0, "Ovulatory": 0, "Luteal": 0, "Unknown/Male": 0}
    for r in cohort: phases[r["phase"]] += 1
    
    # Stress Dist
    stress_dist = {"Low (1-3)": 0, "Med (4-7)": 0, "High (8-10)": 0}
    for r in cohort:
        if r["stress_level"] <= 3: stress_dist["Low (1-3)"] += 1
        elif r["stress_level"] <= 7: stress_dist["Med (4-7)"] += 1
        else: stress_dist["High (8-10)"] += 1
        
    # Population Mood Trends (Mock 7-day trailing average calculation from timestamps)
    # Since we generated timestamps spanning 30 days, we'll map a smooth 7-day vector logically
    mood_trend = [3.5, 3.6, 3.4, 3.5, 3.7, 3.6, sum(r["mood_score"] for r in cohort)/100]
    
    return {
        "avg_wellness": round(avg_wellness, 1),
        "avg_stress": round(avg_stress, 1),
        "phases": phases,
        "stress_distribution": stress_dist,
        "mood_trend": mood_trend,
        "total_population": len(cohort)
    }
