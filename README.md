# LunaAura Research System
**Behavioral Risk Stratification Pipeline**

LunaAura is an academically honest predictive machine learning pipeline modeling the boundaries between lifestyle metrics (sleep, stress, activity), menstrual cycle topologies, and clinical severity proxy measures.

## Architecture Highlights
- **Data Structuring**: Eliminates artificial mathematical target generation in favor of k-NN statistical matching over core demographic links, maintaining the organic nature of PHQ reporting distributions.
- **Model Base**: Uses Scikit-Learn's `HistGradientBoosting` ensemble to evaluate sequential tabular logs populated with rolling aggregates (`Stress_Rolling_Mean_3d`).
- **Distributional Prediction**: Drops standard point-estimation. Employs Non-Parametric Quantile Regression to yield uniquely tailored lower (10th percentile) and upper (90th percentile) intervals matching an individual's variance.
- **Explainability**: Applies Local Feature Attributions (SHAP) across Random Forest proximal models to infer variable directionality instantly via a Rules-based NLG interface.

See `ARCHITECTURE.md` and `RUN_STEPS.md` for specific technical flows.
