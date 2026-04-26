import sqlite3
import datetime
import random

conn = sqlite3.connect('data/lunaaura.db')
cur = conn.cursor()

# Get users
cur.execute("SELECT id, username, gender, cycle_length FROM users WHERE username IN ('Aanya', 'Rohan', 'Eshita', 'MaleUser', 'HealthyUser', 'Aditi', 'Om')")
users = cur.fetchall()

now = datetime.datetime.now()

def insert_history(user_id, gender, cycle_len, start_days_ago, end_days_ago, base_sleep, base_stress, base_activity):
    for i in range(start_days_ago, end_days_ago, -1):
        log_date = (now - datetime.timedelta(days=i)).isoformat()
        
        # Add some random noise
        sleep = max(2.0, min(12.0, base_sleep + random.uniform(-1.5, 1.5)))
        stress = max(1, min(10, int(base_stress + random.uniform(-2, 2))))
        activity = max(0, min(120, int(base_activity + random.uniform(-15, 15))))
        anxiety = max(1, min(10, int(stress - random.uniform(-1, 2))))
        water = max(0.5, min(5.0, round(random.uniform(1.5, 3.5), 1)))
        
        cycle_day = 0
        phase = "None"
        if gender == "Female":
            cycle_len = cycle_len if cycle_len else 28
            # Calculate a cycle day based on time
            cycle_day = (i % cycle_len) + 1
            if cycle_day <= 5: phase = "Menstrual"
            elif cycle_day <= 13: phase = "Follicular"
            elif cycle_day <= 16: phase = "Ovulatory"
            else: phase = "Luteal"
            
        # Basic heuristic for wellness score
        wellness = 100 - (stress * 3) - ((8 - sleep) * 4) + (activity * 0.2)
        wellness = max(10, min(95, wellness))
        
        cur.execute('''
            INSERT INTO user_history 
            (user_id, date, sleep_duration, stress_level, mood_score, cycle_day, phase, activity, wellness_score, predicted_risk, anxiety_level, water_liters)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, log_date, round(sleep, 1), stress, 3.5, cycle_day, phase, activity, wellness, f"{random.randint(10, 60)}%", anxiety, water))

for u in users:
    uid, uname, gender, clen = u
    # Generate 45 days of data for each
    # Rohan (Male) -> volatile slightly
    # Aanya (Female) -> healthy
    # Eshita (Female) -> slightly stressed recently
    if uname == 'Aanya':
        insert_history(uid, gender, clen, 45, 0, 8.0, 3, 45)
    elif uname == 'Rohan':
        insert_history(uid, gender, clen, 45, 0, 6.5, 6, 20)
    elif uname == 'Eshita':
        insert_history(uid, gender, clen, 45, 0, 6.0, 7, 30)
    elif uname == 'MaleUser':
        insert_history(uid, gender, clen, 45, 0, 7.5, 4, 60)
    elif uname == 'HealthyUser':
        insert_history(uid, gender, clen, 45, 0, 8.5, 2, 90)
    else:
        insert_history(uid, gender, clen, 45, 0, random.uniform(5.5, 8.5), random.uniform(3, 8), random.uniform(10, 60))

conn.commit()
conn.close()
print("Pseudo data inserted successfully.")
