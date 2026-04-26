# LunaAura

**An Explainable Machine Learning Framework for Hormonal and Emotional Health Analysis**

By Eshita Rai | Guide: Mrs. P. Sivakamasundari  
Department of Computing Technologies, SRM Institute of Science and Technology, Chennai

---

## What is LunaAura?

LunaAura helps you understand how your daily habits affect your emotional wellbeing. You log six things daily — sleep, stress, anxiety, exercise, water intake, and menstrual cycle day — and the system calculates a personal risk score and wellness score using a transparent weighted formula. Machine learning models estimate your mental health trajectory and SHAP explains which factors matter most.

**This is a research prototype, not a medical tool.**

---

## Project Structure

```
Luna_Aura/
├── api/                    # Flask REST API (port 5001)
│   └── app.py              # 7 endpoints: health, signup, login, profile, predict, analytics, insights
├── web/                    # Frontend
│   ├── index.html           # Main UI with login, dashboard, analytics, research mode
│   └── script.js            # All rendering, chart logic, and API calls
├── src/                    # Core ML & data pipeline
│   ├── data_pipeline/       # Data loading, merging, preprocessing, SQLite management
│   ├── models/              # Trained models (.pkl), training scripts, SHAP explainer
│   └── inference/           # Cohort generation, chart simulation, prediction logic
├── data/                   # SQLite database (105 users, 470 daily logs)
│   ├── lunaaura.db          # Main database
│   ├── raw/                 # Source CSV datasets
│   └── processed/           # Merged training data
├── docs/                   # Technical documentation
├── paper_assets/           # Publication-ready charts and tables (25+ figures)
├── presentation/           # Review 3 materials
│   ├── LunaAura_Review3_Final.pptx  # 34-slide presentation
│   ├── LunaAura_Research_Paper.pdf  # IEEE-format paper
│   ├── Review3_Speaking_Notes.md    # Viva prep & speaking flow
│   └── rubric/              # Evaluation rubric & IEEE template
├── scripts/                # Utility scripts (PPT generation, data seeding, chart generation)
├── archive/                # Legacy code and old versions
├── requirements.txt        # Python dependencies
└── run.sh                  # Quick-start script
```

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python api/app.py

# Open the frontend
open web/index.html
```

The API runs on `http://localhost:5001`. The frontend connects to it automatically.

**Demo users:** `eshita / eshita123` (Female, 85 entries) | `rohan / rohan123` (Male)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, JavaScript, Chart.js, TailwindCSS |
| Backend | Python, Flask |
| Database | SQLite |
| ML Models | scikit-learn (HistGradientBoosting, RandomForest, Quantile Regression) |
| Explainability | SHAP (TreeExplainer) |

---

## Key Features

- **Transparent Risk Formula** — weighted sum of 6 factors (Stress 35%, Sleep 25%, Anxiety 20%, Activity 10%, Hydration 5%, Baseline 5%) + cycle phase modifiers
- **Cycle-Aware Scoring** — menstrual phase modifiers (±5 to ±8 points) based on published chronobiology
- **Gender-Adaptive** — male users get re-normalized weights, not reduced analytics
- **Calibrated ML** — Platt-scaled classifier + 3 quantile regressors for uncertainty
- **SHAP Explainability** — per-instance feature attributions shown as plain-language insights
- **Longitudinal Dashboard** — 30-day trends, 7-day risk heatmap, real-time charts

---

## Database

- **105 users** (86 Female, 14 Male, 5 Other)
- **470 daily log entries**
- **1 longitudinal user** (Eshita: 85 entries over 40+ days)
- Reproducible synthetic cohort (seed=42)

---

## License

Research project — SRM Institute of Science and Technology, 2026.
