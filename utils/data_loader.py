import os
import fastf1

CACHE_DIR = os.path.join(os.getcwd(), "cache")

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

fastf1.Cache.enable_cache(CACHE_DIR)


# -------------------------------------------------
# LOAD SESSION
# -------------------------------------------------
def load_session(year: int, gp: str, session_type: str = "R"):
    """
    Loads F1 session data using FastF1.

    Args:
        year (int): Season year (e.g. 2023)
        gp (str): Grand Prix name (e.g. "Monza")
        session_type (str): R = Race, Q = Qualifying, FP1/2/3

    Returns:
        FastF1 session object
    """
    session = fastf1.get_session(year, gp, session_type)
    session.load()
    return session


# -------------------------------------------------
# EXTRACT LAP DATA
# -------------------------------------------------
def get_lap_data(session):
    """
    Converts FastF1 lap data into a clean DataFrame
    for analytics + visualization.
    """

    laps = session.laps.copy()

    # Select useful columns
    df = laps[[
        "Driver",
        "LapNumber",
        "Stint",
        "Compound",
        "TyreLife",
        "LapTime",
        "Team"
    ]].copy()

    # Clean data
    df = df.dropna(subset=["LapTime"])

    # Convert LapTime (timedelta) → seconds
    df["LapTime"] = df["LapTime"].dt.total_seconds()

    # Sort for proper analysis
    df = df.sort_values(["Driver", "LapNumber"])

    return df


# -------------------------------------------------
# DRIVER LIST HELPER (OPTIONAL BUT USEFUL)
# -------------------------------------------------
def get_drivers(session):
    """
    Returns list of drivers in session.
    """
    return sorted(session.laps["Driver"].unique())