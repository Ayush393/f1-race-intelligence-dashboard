import pandas as pd
import numpy as np

def stint_analysis(df, driver):
    driver_df = df[df["Driver"] == driver]

    results = []

    for stint in driver_df["Stint"].unique():
        stint_df = driver_df[driver_df["Stint"] == stint]

        compound = stint_df["Compound"].iloc[0]

        avg_lap = stint_df["LapTime"].mean()
        deg = np.polyfit(stint_df["LapNumber"], stint_df["LapTime"], 1)[0]

        results.append({
            "Stint": stint,
            "Compound": compound,
            "AvgLapTime": avg_lap,
            "Degradation": deg,
            "Laps": len(stint_df)
        })

    return pd.DataFrame(results)


def best_compound(df):
    return df.groupby("Compound")["AvgLapTime"].mean().sort_values()