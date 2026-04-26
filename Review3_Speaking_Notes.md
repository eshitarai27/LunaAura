# LunaAura Review 3 — Speaking Notes (30 slides)

## 5-7 MINUTE SPEAKING FLOW

**Slide 1 — Title (15s):** "Good morning. I'm Eshita Rai presenting LunaAura, guided by Mrs. Sivakamasundari."

**Slide 2 — Abstract (skip or 15s):** Briefly mention scope — move to motivation.

**Slide 3 — Motivation (30s):** "970 million people worldwide have a mental health condition. Current wellness apps are shallow — they track one thing at a time with no personalization, no cycle awareness, and no explanation."

**Slide 4 — Problem (20s):** "No platform integrates behavioral + hormonal analysis with explainable ML. That's the gap."

**Slide 5 — Objectives (20s):** "Seven objectives — transparent formula, cycle modifiers, gender-adaptive weights, calibrated ML, SHAP explainability, full-stack dashboard, validated on 105 users."

**Slide 6 — Literature (30s):** "PHQ-9 is the gold standard. Saeb showed phone sensors predict depression. SHAP gives transparent explanations. Baker proved cycle phases disrupt sleep. No one has combined all of these."

**Slide 7 — Research Gap (15s):** "The gap is the integration — nobody combines multi-factor scoring, cycle awareness, and explainability."

**Slide 8 — SDG (15s):** "We align with SDG 3, 5, 9, and 10."

**Slide 9 — Phase 1 (15s):** "Originally — basic inputs, static charts, no database, no ML."

**Slide 10 — Phase 2 (15s):** "Problems: data lost on refresh, gender logic broken, no history tracking."

**Slide 11 — Phase 3 (20s):** "We rebuilt everything — SQLite backend, 105 users, dynamic charts, analytics module, gender-adaptive dashboard."

**Slide 12 — Architecture (30s):** "Three tiers: Chart.js frontend, Flask API with 7 endpoints, SQLite database. Four subsystems handle scoring, SHAP, recommendations, and chart simulation."

**Slide 13 — Inputs (15s):** "Six daily inputs: sleep, stress, activity, anxiety, water, cycle day."

**Slide 14 — Risk Formula (45s):** KEY SLIDE. "Risk uses a weighted sum — stress at 35%, sleep deficit 25%, anxiety 20%. Cycle phase adds ±5 to ±8 points. No single factor alone can trigger High severity."

**Slide 15 — Wellness (20s):** "Wellness score uses gender-dependent weights — 8 factors for female, 6 for male."

**Slide 16 — ML Models (30s):** "Three models: calibrated HistGradientBoosting for probability, quantile regressors for confidence intervals, Random Forest SHAP proxy for explanations."

**Slide 17 — Novelty (20s):** "Our novelty is the integration: deterministic + ML + SHAP + cycle-aware + gender-adaptive in one platform."

**Slide 18 — Database (15s):** "SQLite, two tables, 105 users, 470 logs."

**Slide 19 — Dashboard (15s):** "All modules update in real-time — wellness ring, risk heatmap, trends, insights."

**Slides 20-22 — Results (45s):** "AUROC 0.567 — modest but honestly reported. Feature importance shows Age, Stress, Cycle Day as top predictors. Correlation analysis validates the formula weighting."

**Slide 23 — Limitations (20s):** "Synthetic data, expert weights, no clinical validation. This is a research prototype."

**Slide 24 — Cost (15s):** "Entire stack is free. Runs on any laptop."

**Slide 25 — Ethics (15s):** "No clinical claims. Local storage. Explainable AI. Bias acknowledged."

**Slide 28 — Conclusion (20s):** "All objectives achieved. LunaAura proves cycle-aware explainable wellness analytics is feasible."

**Slide 30 — Thank You (5s):** "Thank you. Happy to take questions."

---

## SLIDES HUMANIZED (all 30)

Every slide rewritten in natural, presenter-friendly language. No AI-pattern phrases used.

## TECHNICAL TERMS TO MENTION IN VIVA

HistGradientBoosting, Platt scaling, pinball loss, quantile regression, SHAP Shapley values, TreeExplainer, sigmoid calibration, stratified CV, PHQ-9, AUROC, Brier score, allostatic load, progesterone, luteal phase, follicular phase

## RUBRIC → SLIDE MAP

| Criterion | Marks | Best Slides |
|---|---|---|
| 2.8.4 Conclusions vs Objectives | 3 | Slide 28 |
| 5.6.1 Limitations & Validation | 3 | Slide 23 |
| 4.5.1 Methodology | 4 | Slides 12, 14-16, 26 |
| 9.6.1 Team Integration | 4 | Slides 9→10→11 (evolution) |
| 10.5.2 Oral Presentation | 3 | Speaking notes above |
| 11.5.1 Economic Feasibility | 3 | Slide 24 |
| 8.4.2 Ethics | 4 | Slide 25 |
| 10.4.2 Written Engineering | 6 | Slide 27 (paper) |
| **Total** | **30** | |
