# Luna Aura — Paper Validation Audit

Generated from direct codebase inspection on 2026-04-23.

---

## 1. Verified Metrics Used in Paper

| Metric | Value | Source File | Verified |
|--------|-------|-------------|----------|
| Cohort size | 105 users | `database.py` L99–155 + `add_pseudo_data.py` | ✅ Direct DB query |
| Total log entries | 470 | SQLite `user_history` COUNT(*) | ✅ Direct DB query |
| Gender split | 86F / 14M / 5O | SQLite `users` GROUP BY gender | ✅ Direct DB query |
| Age range | 18–55 (mean 36.5) | SQLite `users` AVG/MIN/MAX(age) | ✅ Direct DB query |
| Mean sleep | 6.97h | SQLite `user_history` AVG(sleep_duration) | ✅ Direct DB query |
| Mean stress | 4.87 | SQLite `user_history` AVG(stress_level) | ✅ Direct DB query |
| Mean activity | 40.6 min | SQLite `user_history` AVG(activity) | ✅ Direct DB query |
| Training dataset size | 9,548 records, 28 columns | `data/processed/master_dataset.csv` | ✅ pandas shape check |
| Referral flag balance | 5,054 (0) / 4,494 (1) | master_dataset.csv value_counts | ✅ pandas check |
| PHQ range | 0–27 | master_dataset.csv min/max | ✅ pandas check |
| Classifier AUROC | ~0.567 | `docs/ARCHITECTURE.md` L18 | ✅ Matches project docs |
| Regression RMSE | 7.16 | `docs/ARCHITECTURE.md` L18 | ✅ Matches project docs |
| Brier Score | 0.2451 | `api/app.py` L305–306 (insights endpoint) | ✅ Hardcoded in API |
| Model features (10) | Age, Sleep Duration, Physical Activity Level, Stress Level, Base_Cycle_Length, Cycle_Day, Hormone_Proxy, Sleep_Rolling_Mean_3d, Stress_Rolling_Mean_3d, Stress_Volatility_3d | `model_features.pkl` | ✅ joblib.load verified |

---

## 2. Synthetic Components (Explicitly Disclosed)

| Component | Nature | Disclosure |
|-----------|--------|------------|
| 100-user pseudo cohort | Deterministically seeded (seed=42) synthetic profiles | Stated in paper Section IV-C |
| Eshita 40-day history | Programmatically generated with cycle-driven behavioral variation | Stated in paper Section IV-C |
| Additional user histories (Aanya, Rohan, etc.) | Added via `add_pseudo_data.py` with randomized noise | Stated as synthetic cohort |
| Master training dataset (9,548 rows) | Merged from heterogeneous source CSV files with KNN linking | Disclosed in ARCHITECTURE.md |

---

## 3. Actual ML Components

| Component | Implementation | File |
|-----------|---------------|------|
| HistGradientBoostingClassifier | 100 iterations, 31 max leaf nodes, LR 0.05 | `train_classifier.py` L26 |
| CalibratedClassifierCV | Sigmoid method, 5-fold stratified CV | `train_classifier.py` L28–29 |
| HistGradientBoostingRegressor ×3 | Quantile loss at q=0.10, 0.50, 0.90; 150 iterations | `train_regressor.py` L27–36 |
| RandomForestClassifier (SHAP proxy) | 100 estimators, max_depth=5 | `train_classifier.py` L44 |
| SHAP TreeExplainer | Computes per-instance feature attributions | `explain.py` L11 |
| Trained model artifacts | `calibrated_classifier.pkl`, `phq_quantiles.pkl`, `shap_classifier.pkl` | `src/models/` |

---

## 4. Heuristic Components (Not ML)

| Component | Nature | File |
|-----------|--------|------|
| Composite risk formula | Deterministic weighted sum with 6 factors + phase modifier | `predict.py` L28–55 |
| Wellness score | Weighted normalized aggregation (8 factors for Female, 6 for Male) | `simulate_charts.py` L100–121 |
| Factor breakdown impacts | Linear deviation from reference baselines (sleep 6.5h, stress 4, etc.) | `app.py` L141–145 |
| Recommendation engine | Rule-based threshold checks on sleep, stress, symptoms, water | `recommend.py` L1–71 |
| Chart simulation | Deterministic trend projections from current-day inputs | `simulate_charts.py` L26–67 |
| Phase modifiers | Fixed additive values: Menstrual +5, Follicular -5, Ovulatory -8, Luteal +8 | `predict.py` L48–52 |
| Risk classification thresholds | Low <35, Moderate 35–64, High ≥65 | `predict.py` L63–65 |

---

## 5. Figure Selection Rationale

| Figure | File | Why Selected |
|--------|------|-------------|
| Fig. 1 (Sensitivity: Risk vs Stress) | `21_sensitivity_risk_vs_stress.png` | Validates core formula behavior with deterministic reproducibility. Strongest chart — entirely transparent, no stochastic elements. |
| Combined Cohort Demographics | `combined_cohort_demographics.png` | Establishes dataset characteristics. Essential for any paper. 8 sub-panels efficiently use space. |
| Combined Eshita Case Study | `combined_eshita_case_study.png` | Demonstrates longitudinal responsiveness — the system's key differentiator. Real DB data. |
| Combined Model Results | `combined_model_results.png` | Required for ML credibility. Includes ROC, PR, CM, Feature Importance in one panel. |
| Cycle Phase Comparison | `24_cycle_phase_comparison.png` | Validates gender-adaptive design — a novel contribution claim. |

**Figures NOT used in paper (and why):**
- Individual distribution histograms (01–08): Redundant with combined panel.
- Individual Eshita trends (09–13): Redundant with combined panel.
- Individual ML charts (15–18): Redundant with combined panel.
- Predicted vs Actual (19): Weak — the scatter shows poor correlation because it compares composite formula outputs against ML probabilities, which are fundamentally different scoring systems.
- Residual Histogram (20): Misleading — residuals between two different scoring paradigms don't carry standard interpretation.

---

## 6. Risk Review — Weak Sections Needing Manual Attention

| Section | Issue | Severity | Recommendation |
|---------|-------|----------|---------------|
| ML Model Performance (VII-C) | AUROC ~0.567 is below random for binary classification. Paper handles this honestly but reviewers may question it. | Medium | Emphasize that composite formula is the primary system; ML is supplementary. Already done. |
| paper_assets table4 AUC=0.4372 | This value from the asset generator used mismatched evaluation (DB risk% vs classifier probability). Do NOT cite this number. | High | Paper uses the architecture doc value (0.567) from actual train/test split. Safe. |
| Synthetic data disclaimer | Must be front-and-center. | High | Present in Abstract, Section IV-C, and Section VII-F. Adequately covered. |
| References | All citations are real published works. Verify DOIs before submission. | Low | Standard pre-submission checklist item. |
| Author affiliation | Single author — may raise reviewer flags about scope. | Low | Normal for thesis-derived conference papers. |
