# LunaAura — Paper Asset Report
Generated: 2026-04-23 03:07

## Dataset
- **Users:** 105 registered profiles (SQLite `users` table)
- **Log Entries:** 470 daily behavioral records (`user_history` table)
- **Longitudinal User:** Eshita (user_id=101) — 40-day tracked history

---

## Section A — Cohort Visualizations

| File | Fig | Use In Paper |
|------|-----|--------------|
| 01_age_distribution.png | Fig 1 | Section III-A Dataset Description |
| 02_gender_distribution.png | Fig 2 | Section III-A Dataset Description |
| 03_stress_distribution.png | Fig 3 | Section III-B Feature Analysis |
| 04_sleep_distribution.png | Fig 4 | Section III-B Feature Analysis |
| 05_activity_distribution.png | Fig 5 | Section III-B Feature Analysis |
| 06_anxiety_distribution.png | Fig 6 | Section III-B Feature Analysis |
| 07_water_distribution.png | Fig 7 | Section III-B Feature Analysis |
| 08_risk_category_distribution.png | Fig 8 | Section III-C Label Distribution |

---

## Section B — Longitudinal Analytics

| File | Fig | Use In Paper |
|------|-----|--------------|
| 09_eshita_wellness_trend.png | Fig 9 | Section IV Case Study |
| 10_eshita_stress_trend.png | Fig 10 | Section IV Case Study |
| 11_eshita_sleep_trend.png | Fig 11 | Section IV Case Study |
| 12_eshita_activity_trend.png | Fig 12 | Section IV Case Study |
| 13_eshita_risk_trend.png | Fig 13 | Section IV Risk Trajectory |
| 14_correlation_heatmap.png | Fig 14 | Section III-C Correlation Analysis |

---

## Section C — Model Performance

| File | Fig | Metric | Use In Paper |
|------|-----|--------|--------------|
| 15_roc_curve.png | Fig 15 | AUC = 0.4372 | Section V-A Classifier Evaluation |
| 16_precision_recall_curve.png | Fig 16 | PR-AUC = 0.5479 | Section V-A |
| 17_confusion_matrix.png | Fig 17 | Classification Matrix | Section V-A |
| 18_feature_importance.png | Fig 18 | Top-10 Features | Section V-B Explainability |
| 19_predicted_vs_actual.png | Fig 19 | RMSE = 21.33 | Section V-C Regression Eval |
| 20_residual_histogram.png | Fig 20 | MAE = 17.77 | Section V-C |

---

## Section D — Sensitivity Charts

| File | Fig | Use In Paper |
|------|-----|--------------|
| 21_sensitivity_risk_vs_stress.png | Fig 21 | Section V-D Formula Validation |
| 22_sensitivity_risk_vs_sleep.png | Fig 22 | Section V-D Formula Validation |
| 23_sensitivity_wellness_vs_activity.png | Fig 23 | Section V-D |
| 24_cycle_phase_comparison.png | Fig 24 | Section V-E Gender-Aware Design |

---

## Section E — IEEE Tables

| File | Table | Use In Paper |
|------|-------|--------------|
| table1_features.csv | Table I | Section III Input Features |
| table2_cohort_stats.csv | Table II | Section III Dataset Statistics |
| table3_hyperparameters.csv | Table III | Section IV-A Model Config |
| table4_performance_metrics.csv | Table IV | Section V Results |
| table5_factor_weights.csv | Table V | Section IV-B System Design |
| table6_literature.csv | Table VI | Section II Related Work |

---

## Academic Honesty Notes
- All scores are **Behavioral Wellness Estimates**, not clinical diagnoses.
- Risk scores are composite formulas; not validated in clinical trials.
- Model trained on synthetic pseudo-cohort data for research demonstration.
- Cycle context applies **only** to Female users; Male/Other receive neutral baseline.

---

## Recommended Safest Figures for IEEE Submission
1. Fig 1, 2, 8 — Dataset demographics (always safe)
2. Fig 9–13 — Longitudinal case study (real DB data)
3. Fig 15, 16, 17 — ML metrics (verifiable)
4. Fig 21–23 — Sensitivity analysis (deterministic formula, reproducible)
5. Table I, II, V — Feature and weight tables (transparent methodology)
