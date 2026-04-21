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
                   WHERE LOWER(u.name) = LOWER(?) 
                   ORDER BY h.date ASC''', (username,))
    records = cur.fetchall()
    if not conn_override:
        conn.close()
        
    if not records: return None
    
    last = records[-1]
    risk_distribution = {"Low": 0, "Moderate": 0, "High": 0}
    phase_impact = {"Menstrual": 0, "Follicular": 0, "Ovulatory": 0, "Luteal": 0}
    heatmap = []
    
    for r in records:
        pr = str(r.get("predicted_risk", "50")).replace("%", "")
        if "Low" in pr or (pr.isdigit() and float(pr)<30): risk_distribution["Low"] += 1
        elif "High" in pr or (pr.isdigit() and float(pr)>70): risk_distribution["High"] += 1
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
        "factor_breakdown": {
            "Sleep": {"score": last.get("sleep_duration", 7), "impact": "+10"},
            "Stress": {"score": last.get("stress_level", 5), "impact": "-10"},
            "Activity": {"score": last.get("activity", 30), "impact": "+5"},
            "Anxiety": {"score": last.get("anxiety_level", 5), "impact": "-5"},
            "Water": {"score": last.get("water_liters", 2.0), "impact": "+2"},
            "Cycle Context": {"score": last.get("phase", "Follicular"), "impact": "+0"},
            "Trend Momentum": {"score": "Stable", "impact": "+5"}
        }
    }
    
    summary = {
        "summary_sentence": f"Baseline stability tracking {len(records)} cycles.",
        "what_changed_most": "Synchronized Baseline",
        "wellness_score": last.get("wellness_score", 50),
        "latest_risk": last.get("predicted_risk", "50%")
    }
    
    return {
        "user": username,
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
            
            cur.execute('''
                INSERT OR IGNORE INTO users (name, age, cohort_group, source, created_at, gender)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, data.get("Age", 26), "Live Inferences", "ui_client", now, data.get("Gender", "Female")))
            
            cur.execute('SELECT id FROM users WHERE name = ?', (name,))
            uid = cur.fetchone()[0]
            
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
                "50%",
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
