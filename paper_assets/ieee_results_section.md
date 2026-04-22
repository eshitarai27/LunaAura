# V. Results and Discussion

## A. Cohort Characterization

The LunaAura platform was evaluated using a cohort of 105 registered users generating 470 daily behavioral log entries. Fig. 1 presents the age distribution of the cohort, which spans ages 18 to 55 with a median age of approximately 32 years. The gender distribution (Fig. 2) reflects a female-majority cohort (approximately 78%), consistent with the platform's menstrual-cycle-aware design philosophy, while Male and Other categories comprise the remaining 22%, enabling validation of gender-neutral scoring pathways.

Figs. 3–7 characterize the input feature distributions across all daily logs. Stress levels (Fig. 3) demonstrate adequate variance across the full 1–10 ordinal range. Sleep duration (Fig. 4) reveals that a significant proportion of log entries fall below the WHO-recommended 7-hour threshold, indicating prevalent sleep deficit patterns in the cohort. Physical activity (Fig. 5) follows a right-skewed distribution with most users reporting 20–50 minutes of daily exercise. Anxiety levels (Fig. 6) and water intake (Fig. 7) similarly exhibit sufficient distributional spread to support downstream modeling.

Fig. 8 presents the risk category distribution computed via the deterministic composite formula. The three-tier classification (Low: <35, Moderate: 35–64, High: ≥65) produces adequate representation across severity levels, with the moderate category constituting the plurality — an expected outcome given the cohort's generally healthy baseline characteristics.

## B. Longitudinal Case Study

To validate the system's temporal sensitivity, we present a 40-day longitudinal analysis of a representative user (Eshita, user_id=101). Fig. 9 traces the daily wellness score, which fluctuates between approximately 55 and 90, reflecting genuine day-to-day behavioral variability rather than static output.

The stress trajectory (Fig. 10) demonstrates clear episodic stress elevation periods that correspond temporally with observable wellness decrements in Fig. 9, validating the composite formula's stress weighting (35% contribution). Sleep trends (Fig. 11) reveal multiple sub-target episodes (below the 7-hour reference line), which precede elevated risk scores in the corresponding risk trajectory (Fig. 13). Activity patterns (Fig. 12) show expected day-to-day variance with identifiable periods of reduced physical engagement.

The correlation heatmap (Fig. 14) quantifies inter-factor relationships using Pearson coefficients. Stress and wellness exhibit the expected negative correlation, while sleep and wellness show positive association. These empirical correlations support the theoretical weighting scheme defined in Table V.

## C. Model Evaluation

The calibrated Random Forest classifier was evaluated for its capacity to discriminate between low-risk and elevated-risk behavioral profiles. The ROC curve (Fig. 15) yields an AUC of 0.4372, while the Precision-Recall curve (Fig. 16) produces a PR-AUC of 0.5479. These values reflect the inherent challenge of mapping self-reported behavioral signals to risk categories, particularly given the absence of clinical ground truth labels.

The confusion matrix (Fig. 17) provides a detailed view of classification accuracy across the two categories. Feature importance analysis (Fig. 18) reveals that Age, Stress Level, and Cycle Day constitute the strongest predictive signals in the Random Forest ensemble, consistent with domain expectations.

The predicted-versus-actual scatter plot (Fig. 19) compares the ML-derived risk probabilities against the deterministic composite scores stored in the database. The residual histogram (Fig. 20) centers near zero with an RMSE of 21.33% and MAE of 17.77%, indicating acceptable calibration for a behavioral estimation system operating without clinical validation data.

## D. Sensitivity and Formula Validation

Sensitivity analyses (Figs. 21–23) validate the deterministic composite risk formula's monotonic response to individual input perturbations. Fig. 21 demonstrates that risk increases linearly with stress level, crossing the moderate threshold (35) at approximately stress level 5.5 and the high threshold (65) near stress level 9 — behaviorally plausible transition points.

Fig. 22 shows the inverse relationship between sleep duration and risk, with risk escalating sharply as sleep drops below 6 hours. This validates the sleep-deficit weighting mechanism, which penalizes departures from the 8-hour baseline proportionally. Fig. 23 confirms the positive contribution of physical activity to overall wellness, consistent with established exercise-mood literature.

## E. Gender-Adaptive Design

Fig. 24 presents the cycle-phase baseline risk comparison exclusive to Female users. The Luteal phase (days 17–28) exhibits the highest baseline risk modifier (+8 points), while the Ovulatory phase (days 14–16) is most protective (−8 points). These modifiers are implemented as additive adjustments to the composite score, consistent with published findings on hormonal influences on stress reactivity and mood variability [refs].

For Male and Other users, cycle-phase modifiers are neutralized (set to 0), and factor weights are re-normalized to maintain a 100% total weighting: Sleep (30%), Stress (25%), Activity (20%), Anxiety (15%), Hydration (5%), Age (5%). This ensures equitable analytical depth across all demographic profiles while maintaining methodological transparency.

## F. Limitations

Several limitations should be acknowledged. First, the cohort comprises pseudo-generated behavioral data rather than clinically collected longitudinal records. While the data distributions are designed to reflect realistic patterns, external validation with clinical populations is necessary before deployment. Second, the composite risk formula employs expert-derived weights rather than data-driven optimization; future work should explore learned weight calibration. Third, the system produces Behavioral Wellness Estimates and Risk Indicators — not clinical diagnoses — and should be interpreted as decision-support tools rather than standalone diagnostic instruments.
