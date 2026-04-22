# Luna Aura: Behavioral Risk Stratification Platform

Luna Aura is a comprehensive predictive machine learning platform designed to model the intricate relationships between lifestyle metrics (sleep, stress, physical activity), menstrual cycle topologies, and behavioral wellness. 

Moving beyond generic off-the-shelf tracking, this project has evolved into a fully functional, mathematically defensible full-stack application featuring dynamic UI data maturity paths, persistent user accounts, and real-time inference charting.

## 🚀 Key Features

- **Dynamic Visual Dashboard:** A beautiful, responsive interface that unlocks progressive analytics (7-day heatmaps, 14-day rolling averages, 30-day distributions) purely based on a user's data maturity.
- **Robust Authentication & Privacy:** Secure, localized SQLite schema managing both persistent demographic anchors (Age, Gender) and temporal physiological telemetry. Session tracking natively intercepts unauthenticated requests.
- **Machine Learning Inference:** A proprietary ensemble Random Forest architecture trained on a mathematically constrained 100-user pseudo-cohort. It isolates non-linear lifestyle thresholds to generate probabilistic Risk Estimates instead of deterministic diagnostic points.
- **Academic Research Module:** A transparent, in-app documentation module detailing exact baseline equations, SQL topological logic, penalty deductions, and explicit ethical constraints guarding the model's behavioral assumptions.
- **Persistent Backend:** Seamlessly integrates a Flask API gateway to manage real-time payload generation, connecting Chart.js frontend canvas rendering instantly with backend Python matrix operations.

## ⚙️ Running the Project

Getting the platform up and running locally is handled by a single unified bootstrapper script.

```bash
sh run.sh
```

**What this does:**
1. Cleans up abandoned background ports natively.
2. Detects or creates a Python virtual environment (`venv`) and installs dependencies (`Flask`, `Pandas`, `Scikit-Learn`, `Chart.js`).
3. Bootstraps the backend server locally on port `5001`.

Once the server is running, simply open `web/index.html` in your favorite web browser!

## 🧪 Demo Mode & Demo Accounts

For instant exploration, the system initiates with a 100-user generated cohort tracking exactly 30 days of synthetic (yet mathematically constrained) physiological variance. 

You can log in and view highly saturated data arrays instantly using any of the generated identities:
- **Username:** `Eshita` / **Password:** `eshita_dummy`
- **Username:** `Aanya` / **Password:** `aanya_dummy`
- **Username:** `Rohan` / **Password:** `rohan_dummy`

Alternatively, you can skip login via "Explore Demo" to view population macro-telemetry securely abstracted from individual profiles.

## 📖 Extended Documentation

- Read **`ARCHITECTURE.md`** for a deep dive into the ML ensemble structure, data structuring via k-NN loops, and explainability implementations.
- Read **`RUN_STEPS.md`** for further technical step-by-step diagnostic workflows.
