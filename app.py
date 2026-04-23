import streamlit as st
import fastf1
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from utils.data_loader import get_lap_data

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(layout="wide", page_title="F1 Analytics Platform")
st.title("🏎️ F1 Analytics Platform")
st.caption("Race Intelligence • Strategy • Performance Analysis")

# =====================================================
# HEADER (PORTFOLIO READY)
# =====================================================
st.markdown("""
# 🏎️ F1 Race Intelligence Dashboard

**Analyze race performance, strategy, and tyre degradation using real F1 telemetry data**

Built with:
- FastF1 (real race data)
- Python (data analysis)
- Streamlit (interactive dashboard)
""")

with st.expander("📌 What this dashboard does"):
    st.markdown("""
### 🔍 Key Features

- **Session Analysis** → Compare drivers across FP, Qualifying, Sprint, Race  
- **Race Strategy** → Automatically extract tyre strategies  
- **Performance Metrics** → Pace, consistency, and statistical breakdowns  
- **Weekend Dominance Model** → Identify the most complete driver performance  
- **Tyre Degradation Modeling** → Measure tyre performance drop-off  
- **Lap Progression Analysis** → Visualize race pace evolution  

### 🎯 Goal
Provide **data-driven insights into race performance and strategy decisions**
""")

# =====================================================
# HELPERS
# =====================================================
def to_seconds(x):
    if pd.isnull(x): return None
    if hasattr(x, "total_seconds"): return x.total_seconds()
    try: return float(x)
    except: return None

def fmt(x):
    t = to_seconds(x)
    if t is None: return None
    return f"{int(t//60)}:{t%60:06.3f}"

# =====================================================
# CLEAN DATA ENGINE
# =====================================================
def clean_laps(df):

    df = df.copy()
    df["LapSec"] = df["LapTime"].apply(to_seconds)
    df = df[df["LapSec"].notna()]

    if "PitInTime" in df.columns:
        df = df[df["PitInTime"].isna()]
    if "PitOutTime" in df.columns:
        df = df[df["PitOutTime"].isna()]

    if "TrackStatus" in df.columns:
        df = df[df["TrackStatus"] == 1]

    low = df["LapSec"].quantile(0.05)
    high = df["LapSec"].quantile(0.95)
    df = df[(df["LapSec"] >= low) & (df["LapSec"] <= high)]

    return df


def compute_metrics(df, driver):
    ddf = df[df["Driver"] == driver]["LapSec"].dropna()
    if ddf.empty:
        return None

    avg = ddf.mean()
    std = ddf.std()
    consistency = std / avg if avg else 0

    return avg, std, consistency


# =====================================================
# TYRE DEGRADATION MODEL
# =====================================================
def compute_degradation(df):

    results = []

    for (driver, stint), group in df.groupby(["Driver", "Stint"]):

        g = group.copy()
        g["LapSec"] = g["LapTime"].apply(to_seconds)
        g = g.dropna(subset=["LapSec"])

        if len(g) < 5:
            continue

        g = g.sort_values("LapNumber")
        g["StintLap"] = range(1, len(g)+1)

        x = g["StintLap"]
        y = g["LapSec"]

        slope = np.polyfit(x, y, 1)[0]

        compound = g["Compound"].iloc[0] if "Compound" in g else "Unknown"

        results.append({
            "Driver": driver,
            "Stint": stint,
            "Compound": compound,
            "Degradation (s/lap)": round(slope, 4)
        })

    return pd.DataFrame(results)


# =====================================================
# SIDEBAR
# =====================================================
year = st.sidebar.selectbox("Season", [2021, 2022, 2023, 2024])
schedule = fastf1.get_event_schedule(year)
gp = st.sidebar.selectbox("Grand Prix", schedule["EventName"].tolist())
session_type = st.sidebar.selectbox("Session", ["FP1","FP2","FP3","Q","S","R"])

# =====================================================
# LOAD SESSION
# =====================================================
@st.cache_data(ttl=3600)
def load_session(year, gp, session_type):
    try:
        session = fastf1.get_session(year, gp, session_type)
        session.load()
        return session, get_lap_data(session)
    except:
        return None, None

session, df = load_session(year, gp, session_type)

if session is None:
    st.warning("No session data available.")
    st.stop()

st.success(f"{gp} {year} - {session_type}")

# =====================================================
# DRIVER SELECTION
# =====================================================
drivers = sorted(df["Driver"].unique())
selected = st.multiselect("Select Drivers", drivers, default=drivers[:2])
comp = df[df["Driver"].isin(selected)]

# =====================================================
# DRIVER COMPARISON
# =====================================================
st.subheader("📊 Driver Performance Analysis")
st.caption("Compare driver pace, consistency, and overall performance")

if session_type != "R":

    clean = clean_laps(comp)
    global_median = clean["LapSec"].median()

    rows = []

    for d in selected:

        metrics = compute_metrics(clean, d)
        if metrics is None:
            continue

        avg, std, consistency = metrics

        pace_score = (global_median / avg) * 100 if avg else 0
        consistency_score = (1 / (1 + consistency)) * 100

        rows.append({
            "Driver": d,
            "Avg Lap": fmt(avg),
            "Best Lap": fmt(clean[clean["Driver"]==d]["LapSec"].min()),
            "Consistency": round(consistency,4),
            "Score": round(0.7*pace_score + 0.3*consistency_score,2)
        })

    st.dataframe(pd.DataFrame(rows).sort_values("Score", ascending=False))

else:

    st.markdown("### 🏁 Weekend Dominance Model")

    weekend_frames = []

    for s in ["FP1","FP2","FP3","Q","S"]:
        try:
            sess = fastf1.get_session(year, gp, s)
            sess.load()
            weekend_frames.append(get_lap_data(sess))
        except:
            pass

    weekend_frames.append(df)
    weekend = pd.concat(weekend_frames)

    clean_weekend = clean_laps(weekend)
    global_median = clean_weekend["LapSec"].median()
    race_results = session.results.set_index("Abbreviation")

    rows = []

    for d in selected:

        metrics = compute_metrics(clean_weekend, d)
        if metrics is None:
            continue

        avg, std, consistency = metrics

        pace_score = (global_median / avg) * 100 if avg else 0
        consistency_score = (1 / (1 + consistency)) * 100

        pos = race_results.loc[d,"Position"] if d in race_results.index else None
        pos_score = max(0,(20-pos)*5) if pos else 0

        wds = 0.5*pace_score + 0.3*pos_score + 0.2*consistency_score

        rows.append({
            "Driver": d,
            "Race Position": pos,
            "Weekend Dominance Score": round(wds,2)
        })

    result = pd.DataFrame(rows).sort_values("Weekend Dominance Score", ascending=False)
    st.dataframe(result)

    st.success(f"🏆 Most Dominant Driver: {result.iloc[0]['Driver']}")
    st.info("""
💡 **Insight**: The dominance score combines pace, race result, and consistency across all sessions, 
highlighting the most complete performance over the entire race weekend.
""")
    
# =====================================================
# PRACTICE
# =====================================================
if session_type in ["FP1","FP2","FP3"]:
    st.subheader("🏁 Practice Top 3")
    top3 = session.laps.groupby("Driver")["LapTime"].min().dropna().sort_values().head(3)
    for d,t in top3.items():
        st.write(f"{d}: {fmt(t)}")

# =====================================================
# QUALIFYING
# =====================================================
if session_type == "Q":
    st.subheader("⏱️ Qualifying Top 10")
    q = session.results.sort_values("Position").head(10)
    for c in ["Q1","Q2","Q3"]:
        if c in q.columns:
            q[c] = q[c].apply(fmt)
    st.dataframe(q)

# =====================================================
# RACE
# =====================================================
if session_type == "R":

    st.subheader("🏁 Race Results & Strategy Breakdown")
    st.caption("Final positions with tyre strategy used throughout the race")

    results = session.results.sort_values("Position")
    strategy = []

    for _,row in results.iterrows():
        ddf = df[df["Driver"]==row["Abbreviation"]]
        stints = ddf.groupby("Stint")["Compound"].first().tolist()
        strategy.append(" → ".join(stints))

    results["Strategy"] = strategy
    st.dataframe(results[["Position","Abbreviation","TeamName","Strategy"]])

    # Top 5 stats
    st.subheader("📊 Top 5 Driver Statistics (This Race)")

    df["LapSec"] = df["LapTime"].apply(to_seconds)
    top5 = results.head(5)["Abbreviation"]

    stats = []
    for d in top5:
        laps = df[df["Driver"]==d]["LapSec"].dropna()
        stats.append({
            "Driver": d,
            "Mean Lap": fmt(laps.mean()),
            "Median Lap": fmt(laps.median()),
            "Std Dev": round(laps.std(),3),
            "Best Lap": fmt(laps.min())
        })

    st.dataframe(pd.DataFrame(stats))
    st.info("""
💡 **Insight**: Drivers with lower mean and standard deviation maintain faster and more consistent race pace, 
while best lap highlights peak performance potential.
""")

    st.markdown("### 📘 Statistical Key")
    st.markdown("""
- **Mean Lap Time** → Overall race pace (lower = faster driver)  
- **Median Lap Time** → Typical performance, ignores outliers  
- **Standard Deviation** → Consistency (lower = more consistent)  
- **Best Lap** → Maximum performance potential  
    """)

    # Lap progression
    st.subheader("📈 Lap Time Progression")

    fig, ax = plt.subplots()
    for d in selected:
        ddf = df[df["Driver"]==d]
        ax.plot(ddf["LapNumber"], ddf["LapTime"].apply(to_seconds), label=d)
    ax.legend(); ax.grid()
    st.pyplot(fig)

    # =========================
    # TYRE DEGRADATION
    # =========================
    st.subheader("📉 Tyre Degradation Modeling")
    st.caption("Quantifying tyre performance drop-off within each stint")

    clean_df = clean_laps(df)
    deg_df = compute_degradation(clean_df)

    if not deg_df.empty:
        st.dataframe(deg_df.sort_values("Degradation (s/lap)"))

        best = deg_df.loc[deg_df["Degradation (s/lap)"].idxmin()]
        worst = deg_df.loc[deg_df["Degradation (s/lap)"].idxmax()]

        st.info(f"🟢 Best tyre management: {best['Driver']} ({best['Compound']})")
        st.warning(f"🔴 Highest degradation: {worst['Driver']} ({worst['Compound']})")

    st.subheader("📈 Stint Degradation Curves")

    fig, ax = plt.subplots()

    for d in selected:
        ddf = clean_df[clean_df["Driver"]==d]

        for stint in ddf["Stint"].unique():
            s_df = ddf[ddf["Stint"]==stint]

            if len(s_df) < 5:
                continue

            s_df = s_df.sort_values("LapNumber")
            s_df["LapSec"] = s_df["LapTime"].apply(to_seconds)
            s_df["StintLap"] = range(1, len(s_df)+1)

            ax.plot(s_df["StintLap"], s_df["LapSec"], label=f"{d} S{stint}")

    ax.legend(fontsize=8)
    ax.grid()
    st.pyplot(fig)

    st.info("""
💡 **Insight**: Lower degradation (flatter slope) indicates better tyre management, 
which is critical for longer stints and strategic flexibility.
""")
    
# =====================================================
# SPRINT
# =====================================================
if session_type == "S":
    st.subheader("🏁 Sprint Results")
    st.dataframe(session.results.sort_values("Position"))