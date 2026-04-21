# Luna Aura - Behavioral Analytics Platform

A research-grade AI dashboard for analyzing mental wellbeing through behavioral signals and menstrual cycle patterns.

## Quick Start

### Open in Browser
Simply open `index.html` directly in your browser. No build step required.

```bash
# Navigate to the project directory
open index.html
# or
firefox index.html
```

## Backend Connection

The UI connects to a Flask backend running at `http://localhost:5000`.

### Prediction Endpoint
**POST** `/predict`

Expected request body:
```json
{
    "day_index": 0,
    "age": 25,
    "mood_score": 3,
    "stress_level": 2,
    "stress_cycle_interaction": 28,
    "cycle_day": 14,
    "hormone_intensity": 2,
    "luteal_flag": 0,
    "sleep_duration": 7,
    "physical_activity": 30,
    "stress_squared": 4,
    "sleep_stress_ratio": 3.5,
    "hormone_stress_interaction": 4,
    "cycle_phase_luteal": 0,
    "cycle_phase_menstrual": 0,
    "cycle_phase_ovulatory": 1
}
```

Expected response:
```json
{
    "wellbeing_score": 72,
    "anxiety_risk": 0.24,
    "depression_risk": 0.18
}
```

If the backend is unavailable, the UI uses simulated predictions.

## Features

### Dashboard
- Real-time wellbeing metrics
- Mood trend visualization
- Sleep pattern analysis

### Daily Log
- Age input
- Mood state selector (emoji scale)
- Stress level selector (emoji scale)
- Sleep duration slider (0-12 hours)
- Fatigue level slider (1-5)
- Physical activity slider (0-120 minutes)
- Hormonal symptom intensity slider (1-5)
- Cycle day slider (1-28)
- Run AI prediction button

### Analytics
- Mood vs Cycle Phase chart
- Sleep vs Stress relationship scatter plot
- Activity vs Wellbeing Score bar chart

### Model Insights
- Feature importance analysis
- Machine learning model explanation

### Research Mode
- Model comparison table
- Accuracy, precision, recall metrics

## Authentication

Simple localStorage-based authentication (simulated).
- Email and password required to access the platform
- Credentials stored in browser localStorage
- Click "Logout" to clear session

## Technology Stack

- **HTML5** - Semantic markup
- **Tailwind CSS** - Utility-first styling (CDN)
- **Vanilla JavaScript** - No frameworks
- **Chart.js** - Data visualization

## File Structure

```
index.html     - Main HTML document with authentication UI
script.js      - All application logic and page rendering
```

## Notes

- The application is fully functional without a backend for UI testing
- Backend connection failures gracefully fallback to simulated predictions
- All data is stored in browser localStorage
- No external dependencies required beyond CDN-hosted libraries
