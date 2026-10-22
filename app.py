import io
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Mini FMEA Analyzer", page_icon="🛡️", layout="wide")

st.title("🛡️ Mini FMEA Analyzer")
st.caption("A learning-oriented Failure Mode and Effects Analysis tool using synthetic automotive examples.")

st.info(
    "Educational prototype only. RPN is a prioritization aid, not a substitute for engineering judgment, "
    "safety analysis, company procedures, or an ISO 26262 ASIL determination."
)

DEFAULT_ROWS = [
    {
        "System": "Vehicle speed sensing",
        "Function": "Provide vehicle speed estimate",
        "Failure Mode": "Signal stuck at constant value",
        "Effect": "Downstream functions may use stale speed information",
        "Potential Cause": "Sensor, wiring, or communication fault",
        "Current Controls": "Plausibility check and signal timeout (example)",
        "Severity (1-10)": 7,
        "Occurrence (1-10)": 3,
        "Detection (1-10)": 5,
        "Recommended Action": "Add independent plausibility checks and verify timeout behavior",
        "Owner": "Embedded software",
        "Status": "Open",
    },
    {
        "System": "Temperature sensing",
        "Function": "Report component temperature",
        "Failure Mode": "Signal out of valid range",
        "Effect": "Incorrect thermal status may be reported",
        "Potential Cause": "Sensor damage or ADC/wiring issue",
        "Current Controls": "Range check (example)",
        "Severity (1-10)": 5,
        "Occurrence (1-10)": 4,
        "Detection (1-10)": 3,
        "Recommended Action": "Test boundary values and define a safe diagnostic response",
        "Owner": "System engineering",
        "Status": "Open",
    },
    {
        "System": "ECU communication",
        "Function": "Receive periodic status message",
        "Failure Mode": "Message timeout",
        "Effect": "Receiver may operate with outdated data",
        "Potential Cause": "Bus interruption or sender failure",
        "Current Controls": "Timeout monitoring (example)",
        "Severity (1-10)": 8,
        "Occurrence (1-10)": 3,
        "Detection (1-10)": 4,
        "Recommended Action": "Verify timeout threshold, reaction, and recovery behavior",
        "Owner": "Communication software",
        "Status": "In progress",
    },
]

RATING_COLS = ["Severity (1-10)", "Occurrence (1-10)", "Detection (1-10)"]

if "fmea_df" not in st.session_state:
    st.session_state.fmea_df = pd.DataFrame(DEFAULT_ROWS)

with st.sidebar:
    st.header("Analysis settings")
    st.write("RPN = Severity × Occurrence × Detection")
    st.write("Ratings: 1 (low) to 10 (high), based on your defined rating criteria.")
    st.caption("The example thresholds below are illustrative only; tailor them to your process.")
    high_rpn = st.number_input("Illustrative high-RPN threshold", min_value=1, max_value=1000, value=200)
    st.divider()
    if st.button("Restore example data"):
        st.session_state.fmea_df = pd.DataFrame(DEFAULT_ROWS)
        st.rerun()

st.subheader("1. Failure mode register")
st.write("Edit the example rows or add your own. Keep ratings aligned with a documented rating scale.")

edited = st.data_editor(
    st.session_state.fmea_df,
    num_rows="dynamic",
    use_container_width=True,
    key="fmea_editor",
    column_config={
        "Severity (1-10)": st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
        "Occurrence (1-10)": st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
        "Detection (1-10)": st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
        "Status": st.column_config.SelectboxColumn(options=["Open", "In progress", "Closed"]),
    },
)
st.session_state.fmea_df = edited.copy()

required = ["Failure Mode"] + RATING_COLS
missing = [c for c in required if c not in edited.columns]
if missing:
    st.error(f"Missing required columns: {', '.join(missing)}")
    st.stop()

analysis = edited.copy()
for col in RATING_COLS:
    analysis[col] = pd.to_numeric(analysis[col], errors="coerce")
valid = analysis[RATING_COLS].notna().all(axis=1)
valid &= analysis[RATING_COLS].apply(lambda col: col.between(1, 10)).all(axis=1)
analysis = analysis.loc[valid].copy()

if analysis.empty:
    st.warning("Enter at least one row with valid Severity, Occurrence, and Detection ratings from 1 to 10.")
    st.stop()

analysis["RPN"] = (
    analysis["Severity (1-10)"]
    * analysis["Occurrence (1-10)"]
    * analysis["Detection (1-10)"]
).astype(int)
analysis["Illustrative Priority"] = analysis["RPN"].apply(
    lambda x: "Review first" if x >= high_rpn else "Review"
)
analysis = analysis.sort_values("RPN", ascending=False).reset_index(drop=True)

st.subheader("2. Risk overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Valid failure modes", len(analysis))
c2.metric("Highest RPN", int(analysis["RPN"].max()))
c3.metric("At/above illustrative threshold", int((analysis["RPN"] >= high_rpn).sum()))
c4.metric("Open items", int((analysis.get("Status", pd.Series(dtype=str)) == "Open").sum()))

st.subheader("3. Ranked analysis")
st.dataframe(analysis, use_container_width=True, hide_index=True)

chart_data = analysis.copy()
chart_data["Failure Mode"] = chart_data["Failure Mode"].fillna("Unnamed failure mode")
fig = px.bar(
    chart_data,
    x="RPN",
    y="Failure Mode",
    orientation="h",
    color="RPN",
    title="RPN by failure mode (higher values shown first)",
    hover_data=[c for c in ["Severity (1-10)", "Occurrence (1-10)", "Detection (1-10)", "Illustrative Priority"] if c in chart_data.columns],
)
fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=max(350, 65 * len(chart_data)))
st.plotly_chart(fig, use_container_width=True)

st.subheader("4. Export")
csv_bytes = analysis.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "Download analyzed FMEA as CSV",
    data=csv_bytes,
    file_name="mini_fmea_analysis.csv",
    mime="text/csv",
)
st.caption(
    "RPN does not capture every safety concern: a low RPN must not automatically dismiss a high-severity failure. "
    "Use approved rating criteria, action tracking, and appropriate safety methods for real projects."
)
