import sqlite3, random
from datetime import datetime, timedelta
import math

conn = sqlite3.connect('data/lunaaura.db')
cur = conn.cursor()

cur.execute("SELECT id, name, cohort_group FROM users WHERE name != 'Eshita'")
users = cur.fetchall()

for u in users:
    uid, uname, cohort = u
    
    cur.execute("SELECT COUNT(*) FROM user_history WHERE user_id = ?", (uid,))
    count = cur.fetchone()[0]
    
    if count < 30:
        cur.execute("SELECT date FROM user_history WHERE user_id = ? ORDER BY date DESC LIMIT 1", (uid,))
        last_date_str = cur.fetchone()[0]
        last_date = datetime.fromisoformat(last_date_str)
        
        for i in range(1, 30 - count + 1):
            past_date = (last_date - timedelta(days=i)).isoformat()
            
            # Predictable traces based on cohort
            if cohort == "High":
                sleep = round(random.uniform(3, 5.5), 1)
                stress = random.randint(7, 10)
                activity = random.randint(0, 20)
                mood = round(random.uniform(1.0, 2.5), 1)
            elif cohort == "Moderate":
                sleep = round(random.uniform(5.5, 7), 1)
                stress = random.randint(4, 7)
                activity = random.randint(20, 60)
                mood = round(random.uniform(2.5, 4.0), 1)
            else:
                sleep = round(random.uniform(7, 9), 1)
                stress = random.randint(1, 4)
                activity = random.randint(60, 120)
                mood = round(random.uniform(4.0, 5.0), 1)
                
            cycle_day = random.randint(0, 28)
            if cycle_day <= 7: phase = "Menstrual"
            elif cycle_day <= 11: phase = "Follicular"
            elif cycle_day <= 17: phase = "Ovulatory"
            else: phase = "Luteal"
            
            n_sleep = max(0.0, min(100.0, 100.0 - (abs(sleep - 8.0) * 15.0)))
            n_stress = max(0.0, min(100.0, 100.0 - ((stress - 1.0) * 11.1)))
            n_activity = max(0.0, min(100.0, (activity / 60.0) * 100.0))
            n_anxiety = max(0.0, min(100.0, 100.0 - ((5 - 1.0) * 11.1)))
            n_water = max(0.0, min(100.0, (2.0 / 2.5) * 100.0))
            n_cycle = 75.0 if phase in ["Luteal", "Menstrual"] else 100.0
            
            wellness = int((n_sleep * 0.25) + (n_stress * 0.20) + (n_activity * 0.15) + (n_anxiety * 0.15) + (n_water * 0.05) + (100 * 0.05) + (n_cycle * 0.10) + (75 * 0.05))
            wellness = max(0, min(100, wellness))
            pred_risk = str(max(5, 100 - wellness + random.randint(-5, 5))) + "%"
            
            cur.execute('''
                INSERT INTO user_history (user_id, date, sleep_duration, stress_level, mood_score, cycle_day, phase, activity, wellness_score, predicted_risk, anxiety_level, water_liters)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (uid, past_date, sleep, stress, mood, cycle_day, phase, activity, wellness, pred_risk, 5, 2.0))

conn.commit()
conn.close()
