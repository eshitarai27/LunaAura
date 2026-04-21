# Backend Integration Guide

## Flask Backend Setup

The Luna Aura frontend expects a Flask backend running at `http://localhost:5000`.

### Required Endpoint

**Endpoint:** `POST /predict`

**Purpose:** Accepts behavioral signals and returns mental wellbeing predictions.

### Request Format

The frontend sends the following JSON payload:

```json
{
    "day_index": number,           // Day of study (0-365)
    "age": number,                 // User age (18-100)
    "mood_score": number,          // 1-5 scale
    "stress_level": number,        // 1-5 scale
    "stress_cycle_interaction": number,  // stress_level * cycle_day
    "cycle_day": number,           // 1-28
    "hormone_intensity": number,   // 1-5 scale
    "luteal_flag": number,         // 1 if cycle_day > 18, else 0
    "sleep_duration": number,      // 0-12 hours
    "physical_activity": number,   // 0-120 minutes
    "stress_squared": number,      // stress_level * stress_level
    "sleep_stress_ratio": number,  // sleep_duration / (stress_level + 1)
    "hormone_stress_interaction": number,  // hormone_intensity * stress_level
    "cycle_phase_luteal": number,  // 1 if cycle_day > 18, else 0
    "cycle_phase_menstrual": number,  // 1 if cycle_day <= 7, else 0
    "cycle_phase_ovulatory": number   // 1 if 12 <= cycle_day <= 16, else 0
}
```

### Response Format

The backend must return JSON with these predictions:

```json
{
    "wellbeing_score": number,      // 0-100
    "anxiety_risk": number,         // 0-1 probability
    "depression_risk": number       // 0-1 probability
}
```

### Example Flask Implementation

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import your_ml_model  # Your trained model

app = Flask(__name__)
CORS(app)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    
    # Extract features in order
    features = [
        data['day_index'],
        data['age'],
        data['mood_score'],
        data['stress_level'],
        data['stress_cycle_interaction'],
        data['cycle_day'],
        data['hormone_intensity'],
        data['luteal_flag'],
        data['sleep_duration'],
        data['physical_activity'],
        data['stress_squared'],
        data['sleep_stress_ratio'],
        data['hormone_stress_interaction'],
        data['cycle_phase_luteal'],
        data['cycle_phase_menstrual'],
        data['cycle_phase_ovulatory']
    ]
    
    # Make prediction
    wellbeing_score = your_ml_model.predict_wellbeing(features)
    anxiety_risk = your_ml_model.predict_anxiety(features)
    depression_risk = your_ml_model.predict_depression(features)
    
    return jsonify({
        'wellbeing_score': float(wellbeing_score),
        'anxiety_risk': float(anxiety_risk),
        'depression_risk': float(depression_risk)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## Testing the Connection

1. Start your Flask backend on `http://localhost:5000`
2. Open `index.html` in a browser
3. Log in with any email/password
4. Navigate to "Daily Log"
5. Adjust sliders and click "Run Prediction"
6. Check the browser console for any errors
7. View results on the Dashboard

## Fallback Behavior

If the backend is unavailable:
- The frontend displays a warning message
- A simulated prediction is generated
- The user can still navigate and explore the UI
- No data is lost

## CORS Requirements

Ensure your Flask backend includes CORS headers:

```python
from flask_cors import CORS
CORS(app)
```

Or manually:

```python
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    return response
```

## Debugging

Check browser DevTools console (F12) for:
- Network requests to `http://localhost:5000/predict`
- JSON payload being sent
- Response data received
- Any CORS or connection errors
