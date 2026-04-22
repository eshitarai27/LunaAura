# Structural Architecture

## 1. Flow of Execution
`raw data` 
-> `src/data_pipeline/merge_data.py` (K-NN Linking on Gender/Age & 14-day Sequential Expansion)
-> `data/processed/master_dataset.csv`
-> `src/models/*.py` (Calibration/Quantile Boosting Ensembles)
-> `api/app.py` (REST Orchestration)
-> `web/index.html` (Frontend Consumer).

## 2. Statistical Design Choices
- **Regression Target:** We target pure `PHQ_Total` (0-27 axis).
- **Severity Classification:** Thresholds are bounded uniformly to standard psychiatric buckets (0-4 Minimal, etc.), routed exclusively from the regression 50th-percentile curve.
- **Feature Engineering:** `merge_data.py` calculates Pandas rolling window means specifically per user tracking window (simulated 14 days), capturing longitudinal behavioral momentum vs isolated cross-sectional polling.

## 3. Explaining ML Constraints & Honest Validity
This project eschews inflated metrics common in non-rigorous demos.
Our system hits a baseline classification AUROC of ~0.56 and regression RMSE of 7.16. 
This is mathematically inevitable when statistically bridging heterogeneous domain tables (`sleep.csv` and `depression.csv`) using generic variables alone. Instead of patching this by engineering a synthetic correlation variable (which violates clinical data integrity), we rely directly on **Quantile Regression Envelope Bounds** mapped via Brier-score logged trees. Doing so permits the system to act gracefully under extreme noise contexts while maintaining operational fidelity for actual downstream production contexts where unified datasets do exist.
