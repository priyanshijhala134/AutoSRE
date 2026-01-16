import streamlit as st
import os
import json
import pandas as pd

# -----------------------------
# Page config (must be first)
# -----------------------------
st.set_page_config(
    page_title="Autonomous Ops Agent Console",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
LOG_FILE = os.path.join(PROJECT_ROOT, "incidents.log")

st.markdown("""
### Autonomous Ops Agent Dashboard

This dashboard visualizes an **Agentic AI system** that detects infrastructure failures,
reasons about corrective actions using an LLM under safety constraints,
and executes self-healing workflows to reduce MTTR.

**Demo Mode** shows recorded incidents.
**Live Mode** connects to real metrics when the backend is running.
""")


st.sidebar.title("System Mode")

mode = st.sidebar.radio(
    "Select Mode",
    ["Demo Mode (Default)", "Live Mode"]
)

# -----------------------------
# Theme selector
# -----------------------------
st.sidebar.title(" UI Settings")

theme = st.sidebar.selectbox(
    "Theme Mode",
    ["Dark (Default)", "Light"]
)

accent = st.sidebar.selectbox(
    "Accent Color",
    ["Blue", "Green", "Purple", "Orange"]
)

# -----------------------------
# Theme definitions
# -----------------------------
THEMES = {
    "Dark (Default)": {
        "bg": "#0e1117",
        "card": "#161b22",
        "text": "#e6edf3",
        "muted": "#9ba3b4",
    },
    "Light": {
        "bg": "#f6f8fa",
        "card": "#ffffff",
        "text": "#24292f",
        "muted": "#57606a",
    }
}

ACCENTS = {
    "Blue": "#2f81f7",
    "Green": "#3fb950",
    "Purple": "#a371f7",
    "Orange": "#f78166",
}

colors = THEMES[theme]
accent_color = ACCENTS[accent]

# -----------------------------
# CSS Injection
# -----------------------------
st.markdown(
    f"""
    <style>
    html, body, [data-testid="stApp"] {{
        background-color: {colors['bg']};
        color: {colors['text']};
    }}

    .card {{
        background-color: {colors['card']};
        padding: 1.5rem;
        border-radius: 14px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    }}

    .metric-title {{
        color: {colors['muted']};
        font-size: 0.9rem;
    }}

    .metric-value {{
        font-size: 2.2rem;
        font-weight: 700;
        color: {accent_color};
    }}

    .section-title {{
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}

    table {{
        color: {colors['text']} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Load incidents
# -----------------------------
import json

def load_demo_data():
    with open("demo_incidents.json") as f:
        return json.load(f)

def load_live_data():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE) as f:
        return [json.loads(line) for line in f]

if mode.startswith("Demo"):
    incidents = load_demo_data()
    st.info("Running in Demo Mode — showing sample incidents.")
else:
    incidents = load_live_data()
    if not incidents:
        st.warning("Live mode enabled, but no incidents detected yet.")



if not os.path.exists(LOG_FILE):
    st.error("No incident logs found.")
    st.stop()

with open(LOG_FILE) as f:
    incidents = [json.loads(line) for line in f]

df = pd.DataFrame(incidents)

# -----------------------------
# Header
# -----------------------------
st.markdown("## Autonomous Ops Agent Console")
st.markdown(
    f"<span style='color:{colors['muted']}'>Real-time observability & self-healing insights</span>",
    unsafe_allow_html=True,
)

st.markdown("---")

# -----------------------------
# Current State
# -----------------------------
latest = df.iloc[-1]

st.markdown("### Current System State")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f"""
        <div class="card">
            <div class="metric-title">CPU Before</div>
            <div class="metric-value">{latest['cpu_before']:.3f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""
        <div class="card">
            <div class="metric-title">CPU After</div>
            <div class="metric-value">{latest['cpu_after']:.3f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f"""
        <div class="card">
            <div class="metric-title">Action Taken</div>
            <div class="metric-value">{latest['action_taken']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# Incident History
# -----------------------------
st.markdown("### Incident History")
st.dataframe(df, use_container_width=True)

# -----------------------------
# Agent Performance
# -----------------------------
st.markdown("### Agent Performance")

if len(df) > 0:
    success_rate = round((df["success"].sum() / len(df)) * 100, 1)
else:
    success_rate = 0.0

avg_reduction = (df["cpu_before"] - df["cpu_after"]).mean()

p1, p2 = st.columns(2)

with p1:
    st.markdown(
        f"""
        <div class="card">
            <div class="metric-title">Success Rate (%)</div>
            <div class="metric-value">{success_rate:.1f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with p2:
    st.markdown(
        f"""
        <div class="card">
            <div class="metric-title">Avg CPU Reduction</div>
            <div class="metric-value">{avg_reduction:.3f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
