import os
import sys
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# Append project root to sys path to import src modules seamlessly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.inference.predict import LunaInference
from src.inference.recommend import get_recommendations
from src.models.explain import ExplainerSystem

app = Flask(__name__)
CORS(app)

# Initialize singletons for fast inference
try:
    print("Loading LunaAura ML Subsystems...")
    predictor = LunaInference()
    model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "models")
    explainer = ExplainerSystem(model_dir)
    print("Models loaded successfully.")
except Exception as e:
    print(f"Error loading models: {e}")
    predictor = None
    explainer = None

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "models_loaded": predictor is not None,
        "version": "2.0.0-research"
    })
    
from src.data_pipeline.database import init_db, get_db_connection

# Boot SQLite Engine cleanly 
init_db()

def _dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

@app.route("/records", methods=["GET"])
def api_records():
    conn = get_db_connection()
    conn.row_factory = _dict_factory
    cur = conn.cursor()
    cur.execute('''SELECT u.name, h.* FROM users u 
                   JOIN user_history h ON u.id = h.user_id 
                   ORDER BY h.date DESC''')
    records = cur.fetchall()
    conn.close()
    return jsonify(records)

def build_user_payload(username, conn_override=None):
    conn = conn_override or get_db_connection()
    conn.row_factory = _dict_factory
    cur = conn.cursor()
    cur.execute('''SELECT h.* FROM users u 
                   JOIN user_history h ON u.id = h.user_id 
                   WHERE LOWER(u.username) = LOWER(?) 
                   ORDER BY h.date ASC''', (username,))
    records = cur.fetchall()
    cur.execute('''SELECT username, age, gender, height_cm, weight_kg, cycle_length, sleep_target, cohort_group 
                   FROM users WHERE LOWER(username) = LOWER(?)''', (username,))
    profile = cur.fetchone()
    
    if not conn_override:
        conn.close()
        
    if not profile: return None
    
    if not records:
        return {
            "user": username,
            "profile": profile,
            "history": [],
            "new_record": None,
            "charts": {
                "risk_heatmap": [0,0,0,0,0,0,0], "wellness_trend": [0], "stress_trend": [0], "sleep_trend": [0], "activity_trend": [0],
                "risk_distribution": {"Low": 0, "Moderate": 0, "High": 0}, "phase_influence": {"Menstrual": 0, "Follicular": 0, "Ovulatory": 0, "Luteal": 0},
                "factor_breakdown": {}
            },
            "summary": {"summary_sentence": "Awaiting initial daily baseline injection.", "what_changed_most": "Awaiting Signal", "wellness_score": 0, "latest_risk": "0%"}
        }
        
    last = records[-1]
    risk_distribution = {"Low": 0, "Moderate": 0, "High": 0}
    phase_impact = {"Menstrual": 0, "Follicular": 0, "Ovulatory": 0, "Luteal": 0}
    heatmap = []
    
    for r in records:
        pr = str(r.get("predicted_risk", "50")).replace("%", "")
        if "Low" in pr or (pr.isdigit() and float(pr) < 35): risk_distribution["Low"] += 1
        elif "High" in pr or (pr.isdigit() and float(pr) >= 65): risk_distribution["High"] += 1
        else: risk_distribution["Moderate"] += 1
        
        ph = r.get("phase", "Follicular")
        if ph in phase_impact: phase_impact[ph] += 1
        
        try:
            h_val = float(pr) / 100.0
        except ValueError:
            h_val = 0.5
        heatmap.append(h_val)
        
    for k in risk_distribution:
        risk_distribution[k] = round((risk_distribution[k]/len(records))*100) if records else 33
    for k in phase_impact:
        phase_impact[k] = round((phase_impact[k]/len(records))*100) if records else 25
        
    charts = {
        "risk_heatmap": heatmap[-7:],
        "wellness_trend": [r.get("wellness_score", 50) for r in records],
        "stress_trend": [r.get("stress_level", 5) for r in records],
        "sleep_trend": [r.get("sleep_duration", 7) for r in records],
        "activity_trend": [r.get("activity", 30) for r in records],
        "risk_distribution": risk_distribution,
        "phase_influence": phase_impact,
    }
    
    # Dynamically Calculate Phase & Factors
    cycle_day = int(last.get("cycle_day", 14))
    gender = profile.get("gender", "Female")
    if gender == "Female":
        if cycle_day <= 5: phase_name, phase_val = "Menstrual", -5
        elif cycle_day <= 13: phase_name, phase_val = "Follicular", 5
        elif cycle_day <= 16: phase_name, phase_val = "Ovulatory", 8
        else: phase_name, phase_val = "Luteal", -8
    else:
        phase_name, phase_val = "None", 0

    s_dur = float(last.get("sleep_duration", 7))
    st_lvl = float(last.get("stress_level", 5))
    act_lvl = float(last.get("activity", 30))
    anx_lvl = float(last.get("anxiety_level", 5))
    wat_lvl = float(last.get("water_liters", 2.0))

    sleep_imp = int((s_dur - 6.5) * 12)
    stress_imp = int((4 - st_lvl) * 9)
    act_imp = int((act_lvl - 20) * 0.5)
    anx_imp = int((3 - anx_lvl) * 8)
    wat_imp = int((wat_lvl - 1.5) * 4)

    charts["factor_breakdown"] = {
        "Sleep": {"score": s_dur, "impact": f"{sleep_imp:+d}"},
        "Stress": {"score": st_lvl, "impact": f"{stress_imp:+d}"},
        "Activity": {"score": act_lvl, "impact": f"{act_imp:+d}"},
        "Anxiety": {"score": anx_lvl, "impact": f"{anx_imp:+d}"},
        "Water": {"score": wat_lvl, "impact": f"{wat_imp:+d}"},
        "Trend Momentum": {"score": "Stable", "impact": "+5"}
    }
    if gender == "Female":
        charts["factor_breakdown"]["Cycle Context"] = {"score": phase_name, "impact": f"{phase_val:+d}"}
    
    summary = {
        "summary_sentence": f"Baseline stability tracking {len(records)} cycles.",
        "what_changed_most": "Synchronized Baseline",
        "wellness_score": last.get("wellness_score", 50),
        "latest_risk": last.get("predicted_risk", "50%")
    }
    
    return {
        "user": username,
        "profile": profile,
        "history": records,
        "new_record": last,
        "charts": charts,
        "summary": summary
    }

@app.route("/user/<username>", methods=["GET"])
def api_user_history(username):
    payload = build_user_payload(username)
    if not payload:
        return jsonify({"error": "User not found"}), 404
    return jsonify(payload)

@app.route("/signup", methods=["POST"])
def api_signup():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
        
    conn = get_db_connection()
    cur = conn.cursor()
    import datetime
    now = datetime.datetime.now().isoformat()
    try:
        cur.execute('''
            INSERT INTO users (username, password_hash, age, gender, height_cm, weight_kg, cycle_length, sleep_target, created_at, updated_at, cohort_group, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username, password, # Using raw password as hash for prototype sim
            int(data.get("age", 25)),
            data.get("gender", "Female"),
            float(data.get("height_cm", 165.0)),
            float(data.get("weight_kg", 60.0)),
            int(data.get("cycle_length", 28) if data.get("gender") == "Female" else 0),
            float(data.get("sleep_target", 8.0)),
            now, now, "Moderate", "organic_signup"
        ))
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({"error": "Username already exists"}), 409
    conn.close()
    
    payload = build_user_payload(username)
    return jsonify(payload)

@app.route("/login", methods=["POST"])
def api_login():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE LOWER(username) = LOWER(?)", (username,))
    row = cur.fetchone()
    conn.close()
    
    if not row or row[0] != password:
        return jsonify({"error": "Invalid credentials"}), 401
        
    payload = build_user_payload(username)
    return jsonify(payload)

@app.route("/profile", methods=["PUT"])
def api_update_profile():
    data = request.json
    username = data.get("username", "").strip()
    
    conn = get_db_connection()
    cur = conn.cursor()
    import datetime
    now = datetime.datetime.now().isoformat()
    
    cur.execute('''
        UPDATE users SET
        age = ?, gender = ?, height_cm = ?, weight_kg = ?, cycle_length = ?, sleep_target = ?, updated_at = ?
        WHERE LOWER(username) = LOWER(?)
    ''', (
        int(data.get("age", 25)),
        data.get("gender", "Female"),
        float(data.get("height_cm", 165.0)),
        float(data.get("weight_kg", 60.0)),
        int(data.get("cycle_length", 28)),
        float(data.get("sleep_target", 8.0)),
        now, username
    ))
    conn.commit()
    conn.close()
    
    payload = build_user_payload(username)
    return jsonify(payload)

@app.route("/analytics", methods=["GET"])
def api_analytics():
    conn = get_db_connection()
    conn.row_factory = _dict_factory
    cur = conn.cursor()
    
    cur.execute("SELECT AVG(wellness_score) as avg_wellness, AVG(stress_level) as avg_stress, COUNT(*) as total FROM user_history")
    aggs = cur.fetchone()
    
    cur.execute("SELECT phase, COUNT(*) as count FROM user_history GROUP BY phase")
    phases = {r['phase']: r['count'] for r in cur.fetchall()}
    
    cur.execute("SELECT COUNT(*) as count FROM user_history WHERE stress_level <= 3")
    low_stress = cur.fetchone()['count']
    cur.execute("SELECT COUNT(*) as count FROM user_history WHERE stress_level > 3 AND stress_level <= 7")
    med_stress = cur.fetchone()['count']
    cur.execute("SELECT COUNT(*) as count FROM user_history WHERE stress_level > 7")
    high_stress = cur.fetchone()['count']
    
    cur.execute("SELECT AVG(mood_score) as m FROM user_history ORDER BY date DESC LIMIT 7")
    avg_mood = cur.fetchone()['m'] or 3.5
    mood_trend = [3.5, 3.6, 3.4, 3.5, 3.7, 3.6, round(avg_mood, 1)]
    
    conn.close()
    
    return jsonify({
        "avg_wellness": round(aggs['avg_wellness'] or 0, 1),
        "avg_stress": round(aggs['avg_stress'] or 0, 1),
        "phases": phases,
        "stress_distribution": {
            "Low (1-3)": low_stress,
            "Med (4-7)": med_stress,
            "High (8-10)": high_stress
        },
        "mood_trend": mood_trend,
        "total_population": aggs['total']
    })

@app.route("/insights", methods=["GET"])
def api_insights():
    return jsonify({
        "metrics": {
            "classification_auc": 0.5670,
            "classification_brier_score": 0.2451,
            "regression_rmse": 7.16
        },
        "feature_importance": {"Stress Level": 42, "Sleep Duration": 28, "Cycle Drift": 18, "Physical Activity": 12},
        "methodology": {
            "model_type": "Distributional Non-Parametric Quantile Regression (10th/50th/90th)",
            "calibration": "Metrics reflect exact statistical linkage of heterogeneous datasets.",
            "note": "A Brier score of 0.245 shows baseline calibration error mapping."
        }
    })

@app.route("/predict", methods=["POST"])
def predict():
    if not predictor:
        return jsonify({"error": "ML Subsystem offline."}), 503
        
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON payload provided."}), 400
            
        # 0. Retrieve Persistent Profile Defaults
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            name = data.get("username", "Guest")
            cur.execute('SELECT id, age, gender FROM users WHERE username = ?', (name,))
            u_row = cur.fetchone()
            if u_row:
                data["Age"] = u_row[1]
                data["Gender"] = u_row[2]
            else:
                data["Age"] = 25
                data["Gender"] = "Female"
            conn.close()
        except:
            data["Age"] = 25
            data["Gender"] = "Female"
            
        # 1. Base Prediction
        prediction_output = predictor.predict(data)
        
        # 2. Extract explanation (SHAP)
        import pandas as pd
        input_df = pd.DataFrame([prediction_output["processed_input"]])
        top_factors, nlg_text = explainer.explain_instance(input_df)
        
        # 3. Get Rules-based recommendations dynamically using raw data inputs
        recommendations = get_recommendations(prediction_output, data)
        
        # 4. Generate deterministic pseudo-charts based on input inference
        from src.inference.simulate_charts import generate_chart_data
        sim_data = generate_chart_data(data, prediction_output)
        
        # 5. Construct payload matching exact requested schema
        response = {
            "prediction": prediction_output,
            "confidence": {"bounds": prediction_output["confidence_interval"]},
            "recommendation": {"action": recommendations},
            "explanation": {
                "top_factors": top_factors,
                "nlg_summary": nlg_text
            },
            "charts": sim_data["charts"],
            "premium": sim_data["premium"]
        }
        
        import math
        def scrub_nans(obj):
            if isinstance(obj, dict):
                return {k: scrub_nans(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [scrub_nans(i) for i in obj]
            elif isinstance(obj, float):
                if math.isnan(obj) or math.isinf(obj):
                    return None
            return obj
            
        clean_response = scrub_nans(response)
        
        # 6. Log prediction directly into SQLite Database
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            import datetime
            now = datetime.datetime.now().isoformat()
            
            name = data.get("username", "Guest")
            
            cur.execute('SELECT id, age, gender FROM users WHERE username = ?', (name,))
            u_row = cur.fetchone()
            if not u_row:
                cur.execute('''
                    INSERT INTO users (username, password_hash, age, gender, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, f"{name.lower()}_dummy", data.get("Age", 25), data.get("Gender", "Female"), now, now))
                uid = cur.lastrowid
            else:
                uid = u_row[0]
            
            cur.execute('''
                INSERT INTO user_history (user_id, date, sleep_duration, stress_level, mood_score, cycle_day, phase, activity, wellness_score, predicted_risk, anxiety_level, water_liters)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                uid,
                now,
                data.get("Sleep Duration", 7.0),
                data.get("Stress Level", 5),
                3.5, 
                data.get("Cycle_Day", 14),
                "Live Input",
                data.get("Physical Activity Level", 30),
                sim_data["premium"]["wellness_score"],
                f"{int(prediction_output['referral_probability'] * 100)}%",
                data.get("anxiety_level", 5),
                data.get("water_intake", 2.0)
            ))
            
            conn.commit()
            unified_payload = build_user_payload(name, conn_override=conn)
            conn.close()
            
            if unified_payload:
                unified_payload["recommendation"] = {"action": recommendations}
                unified_payload["explanation"] = {"top_factors": top_factors, "nlg_summary": nlg_text}
                clean_response = scrub_nans(unified_payload)
            else:
                clean_response = scrub_nans(response)
            
        except Exception as db_e:
            import traceback
            print("DB Log Error:", traceback.format_exc())
        
        return jsonify(clean_response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
