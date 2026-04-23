import matplotlib.pyplot as plt

def plot_degradation(df, driver):
    driver_df = df[df["Driver"] == driver]

    fig, ax = plt.subplots()

    for stint in driver_df["Stint"].unique():
        stint_df = driver_df[driver_df["Stint"] == stint]

        ax.plot(
            stint_df["LapNumber"],
            stint_df["LapTime"],
            label=f"Stint {stint} ({stint_df['Compound'].iloc[0]})"
        )

    ax.set_title(f"{driver} Tire Degradation")
    ax.set_xlabel("Lap")
    ax.set_ylabel("Lap Time (s)")
    ax.legend()

    return fig