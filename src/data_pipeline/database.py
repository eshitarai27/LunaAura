import sqlite3
import os
import random
import math
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "lunaaura.db")

INDIAN_NAMES = ['Aanya', 'Priya', 'Kavya', 'Riya', 'Neha', 'Aditi', 'Rohan', 'Aarav', 'Ishaan', 'Kartik', 
                'Rahul', 'Ananya', 'Diya', 'Tanya', 'Sneha', 'Arjun', 'Vikram', 'Kiara', 'Aisha', 'Simran', 
                'Sanya', 'Maya', 'Nisha', 'Ravi', 'Om', 'Dev', 'Tara', 'Mila', 'Ayush', 'Karan',
                'Vivaan', 'Anika', 'Kabir', 'Myra', 'Aryan', 'Samar', 'Kyra', 'Trisha', 'Prisha', 'Aditya',
                'Vedant', 'Nandini', 'Shruti', 'Varun', 'Rishi', 'Abhinav', 'Yash', 'Shrutika', 'Ishika', 'Isha',
                'Navya', 'Navin', 'Kriti', 'Sanvi', 'Aadhya', 'Aarohi', 'Aarya', 'Abhay', 'Abhishek', 'Akshay',
                'Amit', 'Anjali', 'Ankita', 'Ansh', 'Anushka', 'Anupam', 'Arnav', 'Atharv', 'Avani', 'Ayushmann',
                'Bhavya', 'Chirag', 'Darshan', 'Dhruv', 'Divya', 'Gaurav', 'Harsh', 'Harshita', 'Himanshu', 'Ira',
                'Jatin', 'Jay', 'Jiya', 'Jyoti', 'Kajal', 'Kalpana', 'Kalyani', 'Kamal', 'Kanak', 'Kavish',
                'Khushi', 'Kiran', 'Kunal', 'Lakshay', 'Lavanya', 'Madhav', 'Mahika', 'Manish', 'Manvi', 'Meera']

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if DB is already initialized
    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone()[0] == 1:
        cursor.execute("SELECT count(*) FROM users")
        if cursor.fetchone()[0] > 10:
            conn.close()
            print("Database already populated. Bypassing initialization.")
            return

    # User Profile Table
    cursor.execute('DROP TABLE IF EXISTS users;')
    cursor.execute('DROP TABLE IF EXISTS user_history;')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        age INTEGER,
        gender TEXT,
        height_cm REAL,
        weight_kg REAL,
        cycle_length INTEGER,
        sleep_target REAL,
        created_at TEXT,
        updated_at TEXT,
        cohort_group TEXT,
        source TEXT
    )
    ''')
    
    # User Daily History Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        sleep_duration REAL,
        stress_level INTEGER,
        mood_score REAL,
        cycle_day INTEGER,
        phase TEXT,
        activity INTEGER,
        wellness_score REAL,
        predicted_risk TEXT,
        anxiety_level INTEGER DEFAULT 5,
        water_liters REAL DEFAULT 2.0,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    
    # Check if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    
    if count == 0:
        _seed_db(cursor)
        
    conn.commit()
    conn.close()

def _add_user(cursor, username, pw_hash, age, gender, height_cm, weight_kg, cycle, sleep, cohort, source, created_at):
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, age, gender, height_cm, weight_kg, cycle_length, sleep_target, created_at, updated_at, cohort_group, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (username, pw_hash, age, gender, height_cm, weight_kg, cycle, sleep, created_at, created_at, cohort, source))
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    return cursor.fetchone()[0]

def _add_history(cursor, user_id, date, sleep, stress, mood, cycle_day, phase, activity, wellness, risk, anxiety=5, water=2.0):
    cursor.execute('''
        INSERT INTO user_history (user_id, date, sleep_duration, stress_level, mood_score, cycle_day, phase, activity, wellness_score, predicted_risk, anxiety_level, water_liters)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, date, sleep, stress, mood, cycle_day, phase, activity, wellness, risk, anxiety, water))

def _seed_db(cursor):
    """Deterministically seed database with 100 users + historical inputs, then generate Eshita."""
    random.seed(42)
    
    profiles = [
        {"risk": "High", "count": 30, "sleep_range": (3, 5.5), "stress_range": (7, 10), "act_range": (0, 20)},
        {"risk": "Moderate", "count": 40, "sleep_range": (5.5, 7), "stress_range": (4, 7), "act_range": (20, 60)},
        {"risk": "Low", "count": 30, "sleep_range": (7, 9), "stress_range": (1, 4), "act_range": (60, 120)}
    ]
    
    now = datetime.now()
    name_idx = 0
    
    # 1. GENERATE THE 100 PSEUDO COHORT USERS
    for p in profiles:
        for _ in range(p["count"]):
            uname = INDIAN_NAMES[name_idx % len(INDIAN_NAMES)]
            name_idx += 1
            age = random.randint(18, 55)
            gender = random.choices(["Female", "Male", "Other"], weights=[0.8, 0.15, 0.05])[0]
            height = round(random.uniform(150, 185), 1)
            weight = round(random.uniform(50, 90), 1)
            cycle = random.randint(26, 32) if gender == "Female" else 0
            slp_target = round(random.uniform(6.5, 9.0), 1)
            created_at = (now - timedelta(days=random.randint(5, 30))).isoformat()
            
            uid = _add_user(cursor, uname, f"{uname.lower()}_dummy", age, gender, height, weight, cycle, slp_target, p["risk"], "synthetic_cohort", created_at)
            
            # Add exactly 1 log for the generic tracker to keep analytics proportional
            sleep = round(random.uniform(*p["sleep_range"]), 1)
            stress = random.randint(*p["stress_range"])
            activity = random.randint(*p["act_range"])
            cycle_day = random.randint(0, 28)
            
            if cycle_day == 0: phase = "Unknown/Male"
            elif cycle_day <= 7: phase = "Menstrual"
            elif cycle_day <= 11: phase = "Follicular"
            elif cycle_day <= 17: phase = "Ovulatory"
            else: phase = "Luteal"
                
            if p["risk"] == "High": mood = round(random.uniform(1.0, 2.5), 1)
            elif p["risk"] == "Moderate": mood = round(random.uniform(2.5, 4.0), 1)
            else: mood = round(random.uniform(4.0, 5.0), 1)
                
            n_sleep = max(0.0, min(100.0, (sleep / 8.0) * 100))
            n_stress = max(0.0, min(100.0, ((10 - stress) / 9.0) * 100))
            n_activity = max(0.0, min(100.0, (activity / 60.0) * 100))
            n_mood = max(0.0, min(100.0, ((mood - 1.0) / 4.0) * 100))
            n_cycle = 50.0 if phase in ["Luteal", "Menstrual"] else 100.0
            n_risk = 20.0 if p["risk"] == "High" else (80.0 if p["risk"] == "Low" else 50.0)
            n_recovery = max(0.0, min(100.0, 50.0 + random.uniform(-20, 20)))
            
            wellness = int((n_sleep * 0.25) + (n_stress * 0.20) + (n_activity * 0.15) + (n_mood * 0.15) + (n_cycle * 0.10) + (n_recovery * 0.10) + (n_risk * 0.05))
            wellness = max(0, min(100, wellness))
            pred_risk = str(max(5, 100 - wellness + random.randint(-5, 5))) + "%"
            
            _add_history(cursor, uid, created_at, sleep, stress, mood, cycle_day, phase, activity, wellness, pred_risk)

    # 2. GENERATE 'Eshita' SPECIFIC SUPER-PROFILE (30 DAYS)
    _generate_eshita(cursor, now)

def _generate_eshita(cursor, current_time):
    """Generates 30 realistic sequential days tracing Eshita's biological cycle drift natively."""
    base_age = 23
    start_time = (current_time - timedelta(days=30)).isoformat()
    uid = _add_user(cursor, "Eshita", "eshita_dummy", base_age, "Female", 165.0, 60.0, 28, 8.0, "Moderate", "tracked_super_user", start_time)
    
    start_cycle_day = 1 # Assuming Day 1 = Menstruation 30 days ago
    
    for day_offset in range(30, 0, -1):
        timestamp = (current_time - timedelta(days=day_offset)).isoformat()
        cycle_day = (start_cycle_day + (30 - day_offset)) % 28
        if cycle_day == 0: cycle_day = 28
        
        if cycle_day <= 7: phase = "Menstrual"
        elif cycle_day <= 11: phase = "Follicular"
        elif cycle_day <= 17: phase = "Ovulatory"
        else: phase = "Luteal"
            
        hormone_dip = 1 if phase == "Luteal" or phase == "Menstrual" else 0
        
        base_sleep = 8.0 - (hormone_dip * random.uniform(0.5, 1.5)) - random.uniform(-0.5, 0.5)
        base_stress = 3 + (hormone_dip * random.randint(1, 4)) + random.randint(-1, 2)
        base_activity = 45 - (hormone_dip * 20) + random.randint(-10, 10)
        base_mood = 4.8 - (base_stress * 0.15) - ((8.0 - base_sleep) * 0.2) + random.uniform(-0.2, 0.2)
        
        sleep = max(2.0, min(10.0, round(base_sleep, 1)))
        stress = max(1, min(10, base_stress))
        activity = max(0, min(120, base_activity))
        mood = max(1.0, min(5.0, round(base_mood, 1)))
        
        n_sleep = max(0.0, min(100.0, (sleep / 8.0) * 100))
        n_stress = max(0.0, min(100.0, ((10 - stress) / 9.0) * 100))
        n_activity = max(0.0, min(100.0, (activity / 60.0) * 100))
        n_mood = max(0.0, min(100.0, ((mood - 1.0) / 4.0) * 100))
        n_cycle = 50.0 if phase in ["Luteal", "Menstrual"] else 100.0
        n_risk = 60.0
        n_recovery = max(0.0, min(100.0, 50.0 + random.uniform(-10, 10)))
        
        wellness = int((n_sleep * 0.25) + (n_stress * 0.20) + (n_activity * 0.15) + (n_mood * 0.15) + (n_cycle * 0.10) + (n_recovery * 0.10) + (n_risk * 0.05))
        wellness = max(0, min(100, wellness))
        
        pred_risk = str(max(10, 100 - wellness + random.randint(-2, 2))) + "%"
        
        _add_history(cursor, uid, timestamp, sleep, stress, mood, cycle_day, phase, activity, wellness, pred_risk)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == '__main__':
    print("Re-initializing Schema & Re-seeding User Profile Core...")
    init_db()
    print("Database built successfully.")
