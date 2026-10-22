import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="FMEA Studio | Automotive Risk Analysis",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --ink:#eaf0fb; --muted:#9eabc2; --panel:#111d31; --panel2:#16243b; --line:#263752; --accent:#69e0c0; --accent2:#72a7ff; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: radial-gradient(ellipse at 15% 0%, #1b3150 0%, #0b1424 42%, #08111f 100%); color: var(--ink); }
.block-container { padding-top: 1.5rem; padding-bottom: 2.5rem; max-width: 1500px; }
h1,h2,h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.03em; }
h1 { font-size: 2.35rem !important; }
[data-testid="stSidebar"] { background: #0b1526; border-right: 1px solid #263752; }
[data-testid="stMetric"] { background: linear-gradient(145deg, #172740, #101c30); padding: 17px 19px; border: 1px solid #2a3d5a; border-radius: 16px; }
[data-testid="stMetricLabel"] { color: #a8b8d1 !important; font-size: .83rem !important; }
[data-testid="stMetricValue"] { color: #f2f6ff !important; font-family: 'Space Grotesk', sans-serif; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-color: #263752 !important; border-radius: 16px; }
.stButton > button, .stDownloadButton > button { border-radius: 10px; border: 1px solid #3a5478; font-weight: 700; }
.stButton > button[kind="primary"] { background: #69e0c0; color: #071522; border: none; }
.stButton > button:hover, .stDownloadButton > button:hover { border-color: #69e0c0; color: #69e0c0; }
div[data-baseweb="tab-list"] { gap: 8px; }
button[data-baseweb="tab"] { background: #142239; border-radius: 10px 10px 0 0; padding: 10px 16px; }
button[data-baseweb="tab"][aria-selected="true"] { background: #203957; color: #69e0c0; }
div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] { border: 1px solid #2a3d5a; border-radius: 12px; overflow: hidden; }
.small-muted { color: #9eabc2; font-size: .9rem; }
.hero { padding: 24px 26px; border: 1px solid #2a3d5a; border-radius: 20px; background: linear-gradient(115deg, rgba(30,54,84,.94), rgba(14,26,44,.92)); margin-bottom: 18px; }
.eyebrow { color: #69e0c0; text-transform: uppercase; letter-spacing: .15em; font-size: .73rem; font-weight: 700; }
.pill { display:inline-block; border:1px solid #365276; color:#bcd0ec; padding:4px 9px; border-radius:999px; font-size:.78rem; margin-right:6px; }
hr { border-color: #263752; }
</style>
""", unsafe_allow_html=True)

COLUMNS = [
    "System", "Function", "Failure Mode", "Effect", "Potential Cause",
    "Current Controls", "Severity (1-10)", "Occurrence (1-10)",
    "Detection (1-10)", "Recommended Action", "Owner", "Status"
]
RATING_COLS = ["Severity (1-10)", "Occurrence (1-10)", "Detection (1-10)"]
STATUS_OPTIONS = ["Open", "In progress", "Action defined", "Verified", "Closed"]

DEFAULT_ROWS = [
    {
        "System": "Vehicle speed sensing",
        "Function": "Provide a valid vehicle speed estimate",
        "Failure Mode": "Signal stuck at constant value",
        "Effect": "Downstream functions may use stale speed information",
        "Potential Cause": "Sensor, wiring, or communication fault",
        "Current Controls": "Plausibility check and signal timeout",
        "Severity (1-10)": 7, "Occurrence (1-10)": 3, "Detection (1-10)": 5,
        "Recommended Action": "Add independent plausibility checks and verify timeout behavior",
        "Owner": "Embedded software", "Status": "Open",
    },
    {
        "System": "Temperature sensing",
        "Function": "Report component temperature",
        "Failure Mode": "Signal outside valid range",
        "Effect": "Incorrect thermal status may be reported",
        "Potential Cause": "Sensor damage or ADC/wiring issue",
        "Current Controls": "Range check",
        "Severity (1-10)": 5, "Occurrence (1-10)": 4, "Detection (1-10)": 3,
        "Recommended Action": "Test boundary values and define a diagnostic response",
        "Owner": "System engineering", "Status": "In progress",
    },
    {
        "System": "ECU communication",
        "Function": "Receive periodic status message",
        "Failure Mode": "Message timeout",
        "Effect": "Receiver may operate with outdated data",
        "Potential Cause": "Bus interruption or sender failure",
        "Current Controls": "Timeout monitoring",
        "Severity (1-10)": 8, "Occurrence (1-10)": 3, "Detection (1-10)": 4,
        "Recommended Action": "Verify timeout threshold, reaction, and recovery behavior",
        "Owner": "Communication software", "Status": "Open",
    },
    {
        "System": "Power supply",
        "Function": "Maintain ECU operating voltage",
        "Failure Mode": "Supply voltage drops below operating range",
        "Effect": "ECU reset or loss of function may occur",
        "Potential Cause": "Connector resistance, transient, or supply fault",
        "Current Controls": "Voltage monitoring",
        "Severity (1-10)": 8, "Occurrence (1-10)": 2, "Detection (1-10)": 4,
        "Recommended Action": "Exercise undervoltage profiles and verify reset/recovery strategy",
        "Owner": "Hardware / system", "Status": "Action defined",
    },
]

def blank_row():
    return {
        "System": "", "Function": "", "Failure Mode": "", "Effect": "",
        "Potential Cause": "", "Current Controls": "",
        "Severity (1-10)": 5, "Occurrence (1-10)": 3, "Detection (1-10)": 5,
        "Recommended Action": "", "Owner": "", "Status": "Open"
    }

if "fmea_df_v3" not in st.session_state:
    st.session_state.fmea_df_v3 = pd.DataFrame(DEFAULT_ROWS, columns=COLUMNS)
if "editor_version_v3" not in st.session_state:
    st.session_state.editor_version_v3 = 0

with st.sidebar:
    st.markdown("## 🛡️ FMEA Studio")
    st.markdown('<span class="pill">AUTOMOTIVE</span><span class="pill">RPN ANALYSIS</span>', unsafe_allow_html=True)
    st.caption("Failure Mode & Effects Analysis workspace")
    st.divider()
    st.markdown("### Analysis settings")
    project_name = st.text_input("Project / system name", value=st.session_state.get("project_name_v3", "Automotive ECU"))
    st.session_state.project_name_v3 = project_name
    high_rpn = st.slider("Review threshold", min_value=1, max_value=1000, value=200, step=10)
    st.caption("RPN = Severity × Occurrence × Detection")
    st.caption("Use your organization's approved rating criteria.")
    st.divider()
    if st.button("＋ Add blank failure", use_container_width=True, type="primary"):
        st.session_state.fmea_df_v3 = pd.concat(
            [st.session_state.fmea_df_v3, pd.DataFrame([blank_row()], columns=COLUMNS)],
            ignore_index=True
        )
        st.session_state.editor_version_v3 += 1
        st.rerun()
    if st.button("↺ Restore starter register", use_container_width=True):
        st.session_state.fmea_df_v3 = pd.DataFrame(DEFAULT_ROWS, columns=COLUMNS)
        st.session_state.editor_version_v3 += 1
        st.rerun()
    st.markdown("---")
    st.markdown('<div class="small-muted">FMEA Studio · v2.1<br>Editable register · Live RPN · CSV export</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="hero">
  <div class="eyebrow">ENGINEERING RISK WORKSPACE</div>
  <h1 style="margin:8px 0 4px 0;">FMEA Studio <span style="color:#69e0c0;">/</span> Risk Analyzer</h1>
  <div style="color:#b6c5dc;font-size:1.02rem;">{project_name} · Turn failure analysis into a clear, action-oriented register.</div>
  <div style="margin-top:14px;">
    <span class="pill">LIVE RPN CALCULATION</span>
    <span class="pill">EDITABLE FAILURE REGISTER</span>
    <span class="pill">CSV EXPORT</span>
  </div>
</div>
""", unsafe_allow_html=True)

tab_dashboard, tab_register, tab_method = st.tabs(["📊  Dashboard", "📝  Failure register", "📘  Method & notes"])

with tab_register:
    st.subheader("Failure mode register")
    st.markdown('<p class="small-muted">Click any cell to edit it. Use the table controls to add or delete rows. Ratings are restricted to 1–10.</p>', unsafe_allow_html=True)
    edited = st.data_editor(
        st.session_state.fmea_df_v3,
        key=f"fmea_editor_v3_{st.session_state.editor_version_v3}",
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        height=430,
        column_order=COLUMNS,
        column_config={
            "System": st.column_config.TextColumn("System / item", width="medium"),
            "Function": st.column_config.TextColumn("Function", width="medium"),
            "Failure Mode": st.column_config.TextColumn("Failure mode *", width="large", required=True),
            "Effect": st.column_config.TextColumn("Potential effect", width="large"),
            "Potential Cause": st.column_config.TextColumn("Potential cause", width="large"),
            "Current Controls": st.column_config.TextColumn("Current controls", width="large"),
            "Severity (1-10)": st.column_config.NumberColumn("Severity", min_value=1, max_value=10, step=1, format="%d", required=True),
            "Occurrence (1-10)": st.column_config.NumberColumn("Occurrence", min_value=1, max_value=10, step=1, format="%d", required=True),
            "Detection (1-10)": st.column_config.NumberColumn("Detection", min_value=1, max_value=10, step=1, format="%d", required=True),
            "Recommended Action": st.column_config.TextColumn("Recommended action", width="large"),
            "Owner": st.column_config.TextColumn("Owner", width="medium"),
            "Status": st.column_config.SelectboxColumn("Action status", options=STATUS_OPTIONS, required=True, width="medium"),
        },
    )
    st.session_state.fmea_df_v3 = edited.copy()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("＋ Add another failure row", type="primary", use_container_width=True):
            st.session_state.fmea_df_v3 = pd.concat([edited, pd.DataFrame([blank_row()], columns=COLUMNS)], ignore_index=True)
            st.session_state.editor_version_v3 += 1
            st.rerun()
    with c2:
        if st.button("Clear all rows", use_container_width=True):
            st.session_state.fmea_df_v3 = pd.DataFrame(columns=COLUMNS)
            st.session_state.editor_version_v3 += 1
            st.rerun()

raw = st.session_state.fmea_df_v3.copy()
for col in COLUMNS:
    if col not in raw.columns:
        raw[col] = ""
raw = raw[COLUMNS]
for col in RATING_COLS:
    raw[col] = pd.to_numeric(raw[col], errors="coerce")
valid_ratings = raw[RATING_COLS].notna().all(axis=1)
valid_ratings &= raw[RATING_COLS].apply(lambda s: s.between(1, 10)).all(axis=1)
has_failure_name = raw["Failure Mode"].fillna("").astype(str).str.strip().ne("")
analysis = raw.loc[valid_ratings & has_failure_name].copy()
analysis["RPN"] = (
    analysis["Severity (1-10)"] * analysis["Occurrence (1-10)"] * analysis["Detection (1-10)"]
).astype(int)
analysis["Priority"] = analysis["RPN"].apply(lambda value: "Review first" if value >= high_rpn else "Review")
analysis = analysis.sort_values("RPN", ascending=False).reset_index(drop=True)

with tab_dashboard:
    st.subheader("Risk overview")
    total_rows = len(raw)
    valid_count = len(analysis)
    high_count = int((analysis["RPN"] >= high_rpn).sum()) if valid_count else 0
    open_count = int(raw["Status"].fillna("Open").isin(["Open", "In progress", "Action defined"]).sum())
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Analyzed failure modes", f"{valid_count}", f"{total_rows} register rows")
    m2.metric("Highest RPN", f"{int(analysis['RPN'].max()) if valid_count else '—'}")
    m3.metric("Above review threshold", f"{high_count}", f"Threshold: {high_rpn}")
    m4.metric("Actions not closed", f"{open_count}")

    if not valid_count:
        st.info("Add a failure mode with valid Severity, Occurrence, and Detection ratings to populate the dashboard.")
    else:
        left, right = st.columns([1.4, 1])
        with left:
            st.markdown("#### Highest RPN items")
            chart_data = analysis.head(10).copy()
            chart_data["Failure Mode"] = chart_data["Failure Mode"].astype(str).str.slice(0, 52)
            fig = px.bar(
                chart_data.sort_values("RPN", ascending=True),
                x="RPN", y="Failure Mode", orientation="h",
                color="RPN", color_continuous_scale=["#3d7edb", "#69e0c0", "#ffb86b"],
                hover_data=["Severity (1-10)", "Occurrence (1-10)", "Detection (1-10)", "Priority"],
            )
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=max(340, 48 * len(chart_data)), margin=dict(l=5, r=10, t=15, b=10),
                coloraxis_showscale=False, xaxis_title="Risk Priority Number (RPN)", yaxis_title="",
                font=dict(family="DM Sans", color="#dce7f8"),
            )
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            st.markdown("#### Rating profile")
            profile = pd.DataFrame({
                "Rating": ["Severity", "Occurrence", "Detection"],
                "Average": [
                    analysis["Severity (1-10)"].mean(),
                    analysis["Occurrence (1-10)"].mean(),
                    analysis["Detection (1-10)"].mean(),
                ]
            })
            fig2 = go.Figure(go.Bar(
                x=profile["Rating"], y=profile["Average"],
                marker_color=["#ffb86b", "#72a7ff", "#69e0c0"],
                text=[f"{v:.1f}/10" for v in profile["Average"]], textposition="outside",
            ))
            fig2.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=340, margin=dict(l=5, r=5, t=20, b=10),
                yaxis=dict(range=[0, 11], title="Average rating"),
                font=dict(family="DM Sans", color="#dce7f8"),
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("#### Ranked action list")
        show_all = st.checkbox("Show all analyzed failure modes", value=True)
        view = analysis if show_all else analysis.head(5)
        display_cols = ["System", "Failure Mode", "Severity (1-10)", "Occurrence (1-10)", "Detection (1-10)", "RPN", "Priority", "Owner", "Status"]
        st.dataframe(view[display_cols], use_container_width=True, hide_index=True, height=310)
        csv_bytes = analysis.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Export analyzed FMEA (CSV)", data=csv_bytes,
            file_name="fmea_analysis_export.csv", mime="text/csv", type="primary",
        )

with tab_method:
    st.subheader("Method & workflow")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### RPN calculation")
        st.latex(r"\mathrm{RPN} = S \times O \times D")
        st.markdown("""
- **Severity (S):** consequence seriousness.
- **Occurrence (O):** estimated likelihood/frequency.
- **Detection (D):** difficulty of detecting the cause or failure before its effect.
- Each rating uses a 1–10 scale; follow your organization's rating guide.
""")
    with c2:
        st.markdown("#### Suggested workflow")
        st.markdown("""
1. Replace starter entries with reviewed failure modes.
2. Record effects, causes, and existing controls.
3. Agree ratings using the team's rating criteria.
4. Review high-severity cases separately from RPN ranking.
5. Assign an owner and action; update status after verification.
6. Export a CSV for review or further analysis.
""")
    st.divider()
    st.markdown("#### Engineering considerations")
    st.markdown("""
- RPN is a prioritization aid and should not be the sole basis for accepting risk.
- Review high-severity failure modes independently of their RPN.
- Keep assumptions, rating rationale, and evidence in the project records.
- Use applicable organizational procedures and safety-analysis methods for formal engineering decisions.
""")
