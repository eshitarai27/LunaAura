import pandas as pd
import numpy as np

np.random.seed(42)

depression_df = pd.read_csv("../dataset/raw/depression_dataset.csv")
sleep_df = pd.read_csv("../dataset/raw/sleep_lifestyle.csv")

depression_df.columns = depression_df.columns.str.strip()
sleep_df.columns = sleep_df.columns.str.strip()

depression_df["PHQ_Total"] = pd.to_numeric(depression_df["PHQ_Total"], errors="coerce")
sleep_df["Sleep Duration"] = pd.to_numeric(sleep_df["Sleep Duration"], errors="coerce")
sleep_df["Physical Activity Level"] = pd.to_numeric(sleep_df["Physical Activity Level"], errors="coerce")

depression_df.fillna(depression_df.mean(numeric_only=True), inplace=True)
sleep_df.fillna(sleep_df.mean(numeric_only=True), inplace=True)

depression_df["user_id"] = range(1, len(depression_df) + 1)

rows = []

for _, row in depression_df.iterrows():

    base_depression = 1 if row["PHQ_Total"] >= 10 else 0

    for day in range(1, 31):

        cycle_day = day % 28
        if cycle_day == 0:
            cycle_day = 28

        if cycle_day <= 5:
            phase = "menstrual"
        elif cycle_day <= 13:
            phase = "follicular"
        elif cycle_day <= 16:
            phase = "ovulatory"
        else:
            phase = "luteal"

        hormone = np.sin(2 * np.pi * cycle_day / 28)

        # Strong cycle dominance
        luteal_effect = 0.45 if phase == "luteal" else 0.0
        hormone_effect = 0.25 * abs(hormone)

        stress_map = {"Good": 1, "Average": 2, "Bad": 3}
        study = stress_map.get(row["Study Pressure"], 2)
        financial = stress_map.get(row["Financial Pressure"], 2)
        stress_level = (study + financial) / 2

        # Interaction term
        stress_cycle_interaction = stress_level * (1 if phase == "luteal" else 0)

        depression_prob = (
            0.35 * base_depression
            + luteal_effect
            + hormone_effect
            + 0.10 * stress_cycle_interaction
        )

        depression_prob = min(depression_prob, 0.95)
        depression_flag = np.random.binomial(1, depression_prob)

        mood = np.clip(
            5 - (row["PHQ_Total"] / 6)
            + hormone * 1.2
            - stress_level * 0.2
            + np.random.normal(0, 0.7),
            1,
            5
        )

        rows.append({
            "user_id": row["user_id"],
            "day_index": day,
            "age": row["Age"],
            "gender": row["Gender"],
            "mood_score": mood,
            "stress_level": stress_level,
            "stress_cycle_interaction": stress_cycle_interaction,
            "depression_flag": depression_flag,
            "cycle_day": cycle_day,
            "cycle_phase": phase,
            "hormone_intensity": hormone,
            "luteal_flag": 1 if phase == "luteal" else 0
        })

master_df = pd.DataFrame(rows)

sleep_sample = sleep_df.sample(len(master_df), replace=True).reset_index(drop=True)

master_df["sleep_duration"] = sleep_sample["Sleep Duration"]
master_df["physical_activity"] = sleep_sample["Physical Activity Level"]

# --------------------------------------------------
# ENGINEERED NONLINEAR FEATURES (FOR REGRESSION)
# --------------------------------------------------

master_df["stress_squared"] = master_df["stress_level"] ** 2

master_df["sleep_stress_ratio"] = (
    master_df["sleep_duration"] /
    (master_df["stress_level"] + 1)
)

master_df["hormone_stress_interaction"] = (
    master_df["hormone_intensity"] *
    master_df["stress_level"]
)

master_df["wellbeing_score"] = (
    70
    - master_df["depression_flag"] * 20
    - master_df["stress_level"] * 7
    + master_df["sleep_duration"] * 2
    + master_df["physical_activity"] * 2
    + master_df["hormone_intensity"] * 10
    + np.random.normal(0, 7, size=len(master_df))
)

master_df["wellbeing_score"] = master_df["wellbeing_score"].clip(0, 100)

master_df.to_csv("../dataset/processed/master_dataset.csv", index=False)

print("Stronger biological dataset created.")
print("Shape:", master_df.shape)
