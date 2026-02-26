import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import joblib
import json
from pathlib import Path
from datetime import datetime
CO2_FACTOR = 0.82  # kg CO₂ per kWh
from data_pipeline import build_pipeline
from anomaly_detection import detect_anomalies
from learning_controller import check_and_retrain
from optimizer_auto import optimize_auto
from optimizer_target import optimize_target
from golden_signature import identify_golden_signatures
from energy_intelligence import compute_energy_intelligence
from golden_updater import check_and_update_golden
from correction_engine import analyze_batch_against_golden

st.set_page_config(page_title="Adaptive Batch Intelligence", layout="wide")

# =========================================================
# SESSION STATE
# =========================================================
if "golden_updated" not in st.session_state:
    st.session_state.golden_updated = False

if "golden_update_time" not in st.session_state:
    st.session_state.golden_update_time = None

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    return build_pipeline()


@st.cache_data
def run_anomaly(df):
    return detect_anomalies(df)

@st.cache_resource
def load_model():
    model = joblib.load(MODEL_DIR / "model.pkl")
    feature_cols = joblib.load(MODEL_DIR / "feature_columns.pkl")
    return model, feature_cols


df = load_data()
df_with_anomaly = run_anomaly(df)
df_energy = compute_energy_intelligence(df)

st.title("Adaptive Batch Intelligence System")

# =========================================================
# SYSTEM SUMMARY
# =========================================================
st.header("System Summary")

with st.expander("Detailed Technical Explanation"):
    st.markdown("""
    This system integrates:
    • Isolation Forest for anomaly detection  
    • Supervised ML model for quality prediction  
    • Multi-objective optimization for process improvement  

    Quality Score = composite of hardness, dissolution rate and uniformity  
    Energy = total batch energy aggregation  
    Anomalies = multivariate statistical deviations  

    The system is designed for actionable manufacturing optimization.
    """)

col1, col2, col3 = st.columns(3)
col1.metric("Average Quality Score", f"{df['quality_score'].mean():.2f}")
col2.metric("Average Energy per Batch", f"{df['total_energy'].mean():.0f} kWh")
col3.metric("Detected Anomalies", int(df_with_anomaly["anomaly_flag"].sum()))

# =========================================================
# FEATURE IMPORTANCE
# =========================================================
st.header("Model Feature Importance")

with st.expander("Importance Computation"):
    st.markdown("""
    Derived from tree-based model feature importances.  
    Higher value → stronger influence on predictions.
    """)

try:
    model, feature_cols = load_model()
    rf_model = model.estimators_[0]          # first target RF
    imp = rf_model.feature_importances_

    df_imp = pd.DataFrame({
        "Feature": feature_cols,
        "Importance": imp
    }).sort_values("Importance", ascending=False)

    df_imp["Cumulative"] = df_imp["Importance"].cumsum()

    fig_imp = px.bar(
        df_imp.head(15),
        x="Importance",
        y="Feature",
        orientation="h",
        title="Top Feature Drivers"
    )
    st.dataframe(df_imp.head(15))
    st.plotly_chart(fig_imp, width='stretch')

except Exception:
    st.warning("Train model to view feature importance.")

import json
from pathlib import Path

st.header("Model Performance")

metrics_path = Path(__file__).resolve().parent.parent / "models" / "model_metrics.json"

if metrics_path.exists():
    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    perf_df = pd.DataFrame(metrics).T.reset_index()
    perf_df.rename(columns={"index": "Target"}, inplace=True)

    st.dataframe(perf_df)

    avg_r2 = perf_df["r2"].mean()
    st.metric("Average R² Score", f"{avg_r2:.3f}")

else:
    st.warning("Train model to view performance metrics.")

# =========================================================
# PERFORMANCE MAP
# =========================================================
st.header("Batch Performance Map")

with st.expander("How to Interpret This Chart"):
    st.markdown("""
    Each point represents one batch.  
    X-axis → Total energy consumption  
    Y-axis → Composite quality score  

    Red points are flagged by Isolation Forest as anomalous.  
    The ideal operational zone is High Quality + Low Energy.
    """)

df_with_anomaly["Status"] = df_with_anomaly["anomaly_flag"].map({
    0: "Normal",
    1: "Anomaly"
})

fig = px.scatter(
    df_with_anomaly,
    x="total_energy",
    y="quality_score",
    color="Status",
    color_discrete_map={
        "Normal": "#1f77b4",
        "Anomaly": "#e63946"
    }
)

st.plotly_chart(fig, width='stretch')

# =========================================================
# ANOMALY TABLE
# =========================================================
st.subheader("Anomalous Batches")

with st.expander("Anomaly Scoring Method"):
    st.markdown("""
    Isolation Forest assigns anomaly scores based on isolation depth.  
    Higher anomaly_score → More abnormal  
    Risk levels are categorized based on score percentiles.
    """)

anomalies = df_with_anomaly[df_with_anomaly["anomaly_flag"] == 1]

important_cols = [
    "Batch_ID",
    "quality_score",
    "total_energy",
    "anomaly_score",
    "risk_level"
]

def highlight_anomaly(row):
    return ["background-color: #4b1d1d"] * len(row)

if not anomalies.empty:
    anomalies = anomalies.reset_index(drop=True)

    st.dataframe(
        anomalies[important_cols]
        .sort_values("anomaly_score", ascending=False)
        .style.apply(highlight_anomaly, axis=1),
        width='stretch'
    )

    anomalies.insert(0, "S. No.", anomalies.index + 1)

else:
    st.success("No anomalies detected.")

# =====================================================
# ENERGY PATTERN INTELLIGENCE
# =====================================================
st.header("Energy Pattern Intelligence")

with st.expander("How reliability insights are derived"):
    st.markdown("""
    Energy consumption patterns reveal equipment health.  
    The system analyses:
    • rolling energy behavior  
    • drift from baseline  
    • instability variance  

    Flags:
    - Efficiency Loss → machine wear or friction  
    - Process Instability → inconsistent operations  
    - Calibration Gain → improvement detected
    """)

state_counts = df_energy["reliability_state"].value_counts()
fig = px.bar(state_counts, title="Reliability State Distribution")
st.plotly_chart(fig, width='stretch')

problem_df = df_energy[df_energy["reliability_state"] != "Stable"]

if not problem_df.empty:
    st.subheader("Batches Requiring Attention")

    problem_df = problem_df.reset_index(drop=True)
    problem_df.insert(0, "S. No.", problem_df.index + 1)

    st.dataframe(
        problem_df[[
            "S. No.",
            "Batch_ID",
            "total_energy",
            "energy_drift",
            "instability_score",
            "reliability_state"
        ]],
        width='stretch'
    )
else:
    st.success("All batches operating in stable energy regime.")

# =====================================================
# MODEL GOVERNANCE
# =====================================================
from model_governance import detect_model_drift

drift_detected, drift_flags = detect_model_drift(df_with_anomaly)
st.header("Model Governance")

from learning_controller import check_and_retrain

retrained, flags = check_and_retrain()

if retrained:
    st.success("Model drift detected. Model retrained automatically.")
    st.write(flags)

elif flags.get("cooldown_active"):
    st.warning("Drift detected but cooldown active.")

else:
    st.success("Model operating within stable regime.")

version_log_path = Path(__file__).resolve().parent.parent / "models" / "model_versions.json"

if version_log_path.exists():
    with open(version_log_path, "r") as f:
        history = json.load(f)

    if history:
        st.subheader("Model Version History")
        hist_df = pd.DataFrame(history)
        st.dataframe(hist_df)

# =========================================================
# OPTIMIZATION
# =========================================================
st.header("Optimization")

with st.expander("Optimization Logic"):
    st.markdown("""
    Multi-objective evolutionary optimization searches for parameter sets that  
    maximize Quality, Yield, and Performance while minimizing Energy and CO₂.  

    The system compares results with historical golden batches and proposes  
    updates when improvement is detected.
    """)

# ---------------------------------------------------------
# SCENARIO MODE
# ---------------------------------------------------------
mode = st.selectbox(
    "Optimization Scenario",
    ["balanced", "eco", "quality", "yield", "performance"]
)

optimization_type = st.radio(
    "Optimization Strategy",
    ["Automatic (Learn Best Process)", "Target-Based (Meet Defined Goal)"]
)

# ---------------------------------------------------------
# TARGET MODE INPUTS
# ---------------------------------------------------------
if optimization_type.startswith("Target-Based"):

    st.subheader("Target Constraints")

    user_reduction = st.slider("Required CO₂ Reduction (%)", 0.0, 10.0, 2.0)

    user_quality = st.slider(
        "Minimum Quality",
        float(df["quality_score"].min()),
        float(df["quality_score"].max()),
        float(df["quality_score"].mean())
    )

    user_yield = st.slider(
        "Minimum Yield",
        float(df["yield_score"].min()),
        float(df["yield_score"].max()),
        float(df["yield_score"].mean())
    )

    user_perf = st.slider(
        "Minimum Performance",
        float(df["performance_score"].min()),
        float(df["performance_score"].max()),
        float(df["performance_score"].mean())
    )

# ---------------------------------------------------------
# RUN OPTIMIZATION
# ---------------------------------------------------------
if st.button("Run Optimization"):

    if optimization_type.startswith("Automatic"):

        results, proposal, cluster_id = optimize_auto(mode=mode)

        best_row = results.iloc[0] if results is not None else None

    else:

        results = optimize_target(
            required_reduction=user_reduction,
            min_quality=user_quality,
            min_yield=user_yield,
            min_performance=user_perf,
            mode=mode
        )

        proposal = False
        cluster_id = None
        best_row = results.iloc[0] if results is not None else None

    st.session_state.results = results
    st.session_state.proposal = proposal
    st.session_state.cluster_id = cluster_id
    st.session_state.best_row = best_row


# =========================================================
# RESULTS DISPLAY
# =========================================================
if "results" in st.session_state and st.session_state.results is not None:

    results = st.session_state.results.copy()

    if "Score" in results.columns:
        results = results.sort_values("Score", ascending=False)

    st.subheader("Recommended Parameter Sets")

    def highlight_best(row):
        if row.name == results.index[0]:
            return ["background-color: #1f4e79; font-weight: bold"] * len(row)
        return [""] * len(row)

    display_cols = [
        c for c in ["Score", "Quality", "Yield", "Performance", "Energy", "CO2"]
        if c in results.columns
    ] + [c for c in results.columns if c not in ["Score", "Quality", "Yield", "Performance", "Energy", "CO2"]]

    results = results[display_cols].reset_index(drop=True)
    results.insert(0, "S. No.", results.index + 1)

    st.dataframe(
        results.head(10).style.apply(highlight_best, axis=1),
        width="stretch"
    )

    # -----------------------------------------------------
    # GOLDEN UPDATE PROPOSAL
    # -----------------------------------------------------
    if st.session_state.get("proposal", False):

        st.warning("A better golden batch has been discovered.")

        col1, col2 = st.columns(2)

        if col1.button("Approve Golden Update"):

            success = check_and_update_golden(
                st.session_state.best_row,
                mode,
                st.session_state.cluster_id,
                force=True
            )

            if success:
                st.success("Golden signature updated.")
            else:
                st.error("Update blocked due to reliability constraints.")

            # 🔥 CRITICAL: Reset proposal state
            st.session_state.proposal = False
            st.session_state.best_row = None

            st.rerun()

        if col2.button("Reject Proposal"):

            st.info("Golden update rejected.")

            # 🔥 CRITICAL: Reset proposal state
            st.session_state.proposal = False
            st.session_state.best_row = None

            st.rerun()

    # =====================================================
    # IMPACT
    # =====================================================
    st.header("Projected Impact")

    with st.expander("Impact Estimation Method"):
        st.markdown("""
        Energy saved = Baseline − Optimized  
        CO₂ saved = Energy saved × CO2_FACTOR  
        Baseline derived from dataset mean.
        """)

    baseline = df["total_energy"].mean()

    if "results" in st.session_state and len(st.session_state.results) > 0:
        best_energy = st.session_state.results.iloc[0]["Energy"]
    else:
        best_energy = baseline
    saved = max(0, baseline - best_energy)
    co2_saved = saved * 0.82

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Energy Saved / Batch", f"{saved:.1f} kWh")
    c2.metric("CO₂ Saved / Batch", f"{co2_saved:.1f} kg")

    if "results" in st.session_state and len(st.session_state.results) > 0:
        r = st.session_state.results.iloc[0]
        c3.metric("Quality Score", f"{r['Quality']:.2f}")
        c4.metric("Yield Score", f"{r['Yield']:.2f}")
        c5.metric("Performance Score", f"{r['Performance']:.2f}")

    # =====================================================
    # INDUSTRIAL ROI ANALYSIS (EXECUTIVE GRADE)
    # =====================================================

    CO2_FACTOR = 0.82  # kg CO₂ per kWh, adjust for local energy mix
    st.header("Industrial ROI Analysis")

    # ------------------------------
    # Baseline + Optimized Metrics
    # ------------------------------
    baseline_energy = df["total_energy"].mean()
    baseline_co2 = baseline_energy * CO2_FACTOR

    best_row = st.session_state.get("best_row", None)

    if best_row is not None:
        optimized_energy = float(best_row.get("Energy", baseline_energy))
    else:
        optimized_energy = baseline_energy

    optimized_co2 = optimized_energy * CO2_FACTOR

    energy_saved_per_batch = max(0, baseline_energy - optimized_energy)
    co2_saved_per_batch = max(0, baseline_co2 - optimized_co2)

    # ------------------------------
    # Adjustable Assumptions
    # ------------------------------
    with st.expander("Adjust Industrial Assumptions"):

        batches_per_year = st.slider("Batches per Year", 200, 5000, 1200)

        energy_cost_per_kwh = st.slider("Electricity Cost (₹/kWh)", 5.0, 20.0, 9.0)

        carbon_price_per_ton = st.slider("Internal Carbon Price (₹/ton)", 0, 5000, 800)

        downtime_cost_per_hour = st.slider("Downtime Cost (₹/hour)", 5000, 50000, 18000)

        minutes_saved_per_batch = st.slider("Downtime Reduction (minutes/batch)", 0.0, 5.0, 1.0)

        realization_factor = st.slider("Savings Realization Factor", 0.5, 1.0, 0.7)

        implementation_cost = st.slider("Implementation Cost (₹)", 500000, 5000000, 1500000)

        annual_maintenance = st.slider("Annual Maintenance Cost (₹)", 50000, 500000, 200000)

    # ------------------------------
    # Savings Calculation
    # ------------------------------

    annual_energy_saved = energy_saved_per_batch * batches_per_year
    annual_energy_value = annual_energy_saved * energy_cost_per_kwh

    annual_co2_saved_tons = (co2_saved_per_batch * batches_per_year) / 1000
    carbon_value_saved = annual_co2_saved_tons * carbon_price_per_ton

    hours_saved_year = (minutes_saved_per_batch / 60) * batches_per_year
    downtime_value_saved = hours_saved_year * downtime_cost_per_hour

    annual_savings = (
        annual_energy_value
        + carbon_value_saved
        + downtime_value_saved
    )

    annual_savings *= realization_factor

    net_annual_gain = annual_savings - annual_maintenance

    if net_annual_gain > 0:
        roi_percent = (net_annual_gain / implementation_cost) * 100
        payback_years = implementation_cost / net_annual_gain
    else:
        roi_percent = -abs((net_annual_gain / implementation_cost) * 100)
        payback_years = None

    # ------------------------------
    # Display Metrics
    # ------------------------------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Annual Savings", f"₹{annual_savings:,.0f}")
    c2.metric("Annual Maintenance", f"₹{annual_maintenance:,.0f}")
    c3.metric("Net Annual Gain", f"₹{net_annual_gain:,.0f}")
    c4.metric("ROI", f"{roi_percent:.1f}%")

    if payback_years is None:
        st.metric("Estimated Payback Period", "Not achievable")
    else:
        st.metric("Estimated Payback Period", f"{payback_years:.1f} years")


    # =====================================================
    # ADAPTIVE CARBON ALIGNMENT
    # =====================================================

    st.header("Adaptive Carbon Alignment")

    achievable_reduction_pct = 0
    if baseline_co2 > 0:
        achievable_reduction_pct = (
            (baseline_co2 - optimized_co2) / baseline_co2
        ) * 100

    # Region-based regulatory profile
    with st.expander("Select Regulatory Scenario"):

        regulatory_scenario = st.selectbox(
            "Regulatory Profile",
            ["India 2026", "EU 2030", "Internal ESG Aggressive"]
        )

    if regulatory_scenario == "India 2026":
        regulatory_target_pct = 5
    elif regulatory_scenario == "EU 2030":
        regulatory_target_pct = 8
    else:
        regulatory_target_pct = 12

    esg_target_pct = regulatory_target_pct + 3

    reg_gap = achievable_reduction_pct - regulatory_target_pct
    esg_gap = achievable_reduction_pct - esg_target_pct

    c1, c2, c3 = st.columns(3)

    c1.metric("Achievable Reduction", f"{achievable_reduction_pct:.2f}%")
    c2.metric("Regulatory Target", f"{regulatory_target_pct:.2f}%", delta=f"{reg_gap:.2f}%")
    c3.metric("Internal ESG Target", f"{esg_target_pct:.2f}%", delta=f"{esg_gap:.2f}%")

    if achievable_reduction_pct >= esg_target_pct:
        st.success("System exceeds internal ESG targets.")
    elif achievable_reduction_pct >= regulatory_target_pct:
        st.warning("Meets regulatory requirement but below ESG ambition.")
    else:
        st.error("Below regulatory carbon requirement.")


# =====================================================
# PARETO FRONTIER
# =====================================================
st.header("Trade-off Frontier")

with st.expander("Pareto Optimality Explanation"):
    st.markdown("""
    A solution is Pareto optimal if no other solution improves Quality
    without worsening Energy or CO₂.
    These represent efficient trade-offs.
    """)

if "pareto" not in st.session_state or "results" not in st.session_state:
    st.info("Run optimization to visualize trade-off frontier.")
else:
    pareto = st.session_state.pareto
    results = st.session_state.results

    if len(results) == 0:
        st.warning("No optimization results available.")
    else:
        fig_pareto = px.scatter(
            results,
            x="Energy",
            y="Quality",
            color="CO2",
            opacity=0.4
        )

        fig_pareto.add_scatter(
            x=pareto["Energy"],
            y=pareto["Quality"],
            mode="markers",
            marker=dict(size=12, color="red"),
            name="Pareto Frontier"
        )

        st.plotly_chart(fig_pareto, width='stretch')

# =====================================================
# GOLDEN SIGNATURE
# =====================================================
st.header("Golden Signature")

with st.expander("Golden Range Computation"):
    st.markdown("""
    Golden ranges are computed from top-performing batches.

    For each critical parameter:
    • Mean  
    • Min  
    • Max  
    • Standard deviation  

    These define the optimal operational envelope.
    """)

optimizer_best_row = None
if "results" in st.session_state and len(st.session_state.results) > 0:
    optimizer_best_row = st.session_state.results.iloc[0]

# -----------------------------
# Attach predictions to df
# -----------------------------
model = joblib.load(MODEL_DIR / "model.pkl")
feature_cols = joblib.load(MODEL_DIR / "feature_columns.pkl")

X = df[feature_cols].copy()
preds = model.predict(X)

df["Hardness"] = preds[:, 0]
df["Dissolution_Rate"] = preds[:, 1]
df["Content_Uniformity"] = preds[:, 2]
df["Yield"] = preds[:, 3]
df["Performance"] = preds[:, 4]
df["Energy"] = preds[:, 5]

df["Quality"] = (
    0.4 * df["Hardness"]
    + 0.3 * df["Dissolution_Rate"]
    + 0.3 * df["Content_Uniformity"]
)

df["CO2"] = df["Energy"] * CO2_FACTOR

_, golden_ranges, literal_golden = identify_golden_signatures(
    df,
    optimizer_best=optimizer_best_row,
    mode=mode
)
st.session_state.golden_ranges = golden_ranges

ranges_df = pd.DataFrame(golden_ranges).T.reset_index()
ranges_df.rename(columns={"index": "Parameter"}, inplace=True)

important_cols = ["Parameter", "mean", "min", "max", "std"]
other_cols = [c for c in ranges_df.columns if c not in important_cols]

ranges_df = ranges_df[important_cols + other_cols]
ranges_df = ranges_df.reset_index(drop=True)
ranges_df.insert(0, "S. No.", ranges_df.index + 1)

st.dataframe(ranges_df, width='stretch')

# =====================================================
# REAL-TIME BATCH CORRECTION
# =====================================================
st.header("Real-Time Batch Correction")

with st.expander("How correction suggestions work"):
    st.markdown("""
    System compares selected batch parameters against golden signature.
    • Detects drift from optimal range  
    • Classifies severity  
    • Suggests corrective actions
    """)

batch_ids = df["Batch_ID"].tolist()
selected_batch = st.selectbox("Select Batch to Analyze", batch_ids)

batch_row = df[df["Batch_ID"] == selected_batch].iloc[0]

golden_ranges = st.session_state.get("golden_ranges", {})

model, feature_cols = load_model()

report_df = analyze_batch_against_golden(
    batch_row,
    golden_ranges,
    model=model,
    feature_cols=feature_cols
)

report_df = report_df.sort_values(
    by="Predicted Impact",
    key=abs,
    ascending=False
)

if len(report_df) > 0:

    def highlight(row):
        if row["Severity"] == "Critical":
            return ["background-color:#4b1d1d"] * len(row)
        if row["Severity"] == "Moderate":
            return ["background-color:#3d3d1d"] * len(row)
        return [""] * len(row)

    st.dataframe(
        report_df.style.apply(highlight, axis=1),
        width='stretch'
    )

    critical = (report_df["Severity"] == "Critical").sum()
    moderate = (report_df["Severity"] == "Moderate").sum()

    c1, c2 = st.columns(2)
    c1.metric("Critical Deviations", critical)
    c2.metric("Moderate Deviations", moderate)

else:
    st.success("Batch fully aligned with golden signature.")