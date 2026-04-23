# 🏎️ F1 Race Intelligence Dashboard

An interactive analytics platform built using real Formula 1 telemetry data to analyze driver performance, race strategy, and tyre degradation.

---

## 🚀 Live Demo
👉 https://f1-race-intelligence-dashboard-w6oh6sht6zgjoavvmrcmkz.streamlit.app/

---

## 📌 Overview

This project leverages the FastF1 API to extract real race telemetry data and transforms it into a structured analytics dashboard.

The goal is to simulate how data analysts and race engineers evaluate performance across a race weekend using data-driven insights.

---

## 🔍 Key Features

### 📊 Driver Performance Analysis
- Compare drivers across sessions (FP, Qualifying, Sprint, Race)
- Metrics:
  - Average lap time
  - Best lap
  - Consistency (standard deviation)
- Custom performance scoring model

---

### 🏁 Race Results & Strategy Breakdown
- Displays finishing positions
- Automatically reconstructs tyre strategies
  - Example: `Soft → Medium → Hard`
- Helps understand race execution

---

### 🧠 Weekend Dominance Model
- Combines:
  - Pace (lap time performance)
  - Consistency
  - Race finishing position
- Identifies the most complete driver across the entire weekend

---

### 📉 Tyre Degradation Modeling
- Uses linear regression to estimate lap time drop-off within each stint
- Outputs degradation rate (seconds per lap)
- Helps evaluate tyre management and strategy effectiveness

---

### 📈 Lap Time Progression
- Visualizes lap-by-lap race pace
- Highlights:
  - Tyre wear
  - Pit stops
  - Performance trends

---

## 🧠 Data & Methodology

### Data Source
- FastF1 (official F1 timing data)

### Data Processing
- Removed:
  - Pit laps
  - Safety car laps
  - Outliers (extreme lap times)
- Converted lap times to numerical format for analysis

---

### Feature Engineering
- Consistency metric (std dev / avg lap time)
- Dominance scoring model
- Tyre degradation slope calculation

---

## 🛠️ Tech Stack

- Python
- FastF1
- Pandas
- NumPy
- Matplotlib
- Streamlit

---

## 📂 Project Structure
f1-strategy-analytics/
│
├── app.py
├── requirements.txt
├── README.md
├── utils/
│ └── data_loader.py

---

## ▶️ Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
