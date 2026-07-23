# -*- coding: utf-8 -*-
import json
import os
import random
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
LOG_FILE = PROJECT_ROOT / "incidents.log"

AGENT_ORDER = [
    "MonitorAgent",
    "DiagnosticianAgent",
    "PlannerAgent",
    "SafetyCriticAgent",
    "ExecutorAgent",
    "VerifierAgent",
    "ReporterAgent",
]

AGENT_LABELS = {
    "MonitorAgent":       ( "Checked system health",       "Scanned CPU and memory usage"),
    "DiagnosticianAgent": ("Identified root cause",       "Analyzed logs and metrics to find what went wrong"),
    "PlannerAgent":       ("Decided on a response",       "Chose the best course of action"),
    "SafetyCriticAgent":  ("Safety check passed",         "Verified the action is safe before proceeding"),
    "ExecutorAgent":      ("Ran the fix",                 "Restarted the affected service"),
    "VerifierAgent":      ("Confirmed recovery",          "Re-checked system health after the fix"),
    "ReporterAgent":      ("Wrote incident report",       "Saved a full record of this incident"),
}

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AutoSRE — Autonomous Ops Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("Settings")
mode = st.sidebar.radio(
    "Mode",
    ["Demo",  "Live (local)", "Simulate"],
    help=(
        "Demo: view recorded sample incidents\n"
        "Live: reads real incidents.log (local only)\n"
        "Simulate: run an interactive walkthrough right here"
    ),
)
theme   = st.sidebar.selectbox("Theme",  ["Dark", "Light"])
accent  = st.sidebar.selectbox("Accent", ["Blue", "Green", "Purple", "Orange"])

THEMES = {
    "Dark":  {"bg": "#0e1117", "card": "#161b22", "text": "#e6edf3", "muted": "#9ba3b4", "trace_bg": "#1c2128"},
    "Light": {"bg": "#f6f8fa", "card": "#ffffff",  "text": "#24292f", "muted": "#57606a", "trace_bg": "#f0f3f6"},
}
ACCENTS = {"Blue": "#2f81f7", "Green": "#3fb950", "Purple": "#a371f7", "Orange": "#f78166"}

colors       = THEMES[theme]
accent_color = ACCENTS[accent]

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
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
    margin-bottom: 1rem;
}}
.metric-title {{ color: {colors['muted']}; font-size: 0.9rem; }}
.metric-value {{ font-size: 2.2rem; font-weight: 700; color: {accent_color}; }}
.trace-step {{
    background-color: {colors['trace_bg']};
    border-left: 4px solid {accent_color};
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    border-radius: 0 8px 8px 0;
}}
.trace-agent {{ font-weight: 600; color: {accent_color}; }}
.trace-time  {{ color: {colors['muted']}; font-size: 0.8rem; }}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## AutoSRE — Autonomous Ops Dashboard")
st.markdown(
    f"<span style='color:{colors['muted']}'>Multi-agent incident detection & self-healing</span>",
    unsafe_allow_html=True,
)
st.markdown("---")


# ── Data loaders ──────────────────────────────────────────────────────────────
def load_demo_data():
    with open(BASE_DIR / "demo_incidents.json", "r") as f:
        return json.load(f)


def load_live_data():
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE) as f:
        return [json.loads(line) for line in f if line.strip()]


# ── Shared render helpers ─────────────────────────────────────────────────────
def render_metrics(latest: dict):
    c1, c2, c3, c4 = st.columns(4)
    cpu_after = latest.get("cpu_after") or 0

    with c1:
        st.markdown(
            f'<div class="card"><div class="metric-title">CPU Before</div>'
            f'<div class="metric-value">{latest.get("cpu_before", 0):.3f}</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="card"><div class="metric-title">CPU After</div>'
            f'<div class="metric-value">{cpu_after:.3f}</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="card"><div class="metric-title">Action Taken</div>'
            f'<div class="metric-value">{latest.get("action_taken", "N/A")}</div></div>',
            unsafe_allow_html=True,
        )
    with c4:
        success_label = "YES ✅" if latest.get("success") else "NO ❌"
        st.markdown(
            f'<div class="card"><div class="metric-title">Recovered</div>'
            f'<div class="metric-value">{success_label}</div></div>',
            unsafe_allow_html=True,
        )


def render_status_card(latest: dict):
    incident_type = latest.get("incident_type", "Unknown")
    action        = latest.get("action_taken", "N/A")
    success       = latest.get("success", False)
    rca_full      = latest.get("rca", "")

    rca_short = rca_full.split(".")[0].strip() + "." if rca_full else "No analysis available."

    status_emoji = "✅" if success else ("⚠️" if action == "escalate" else "🔴")
    action_label = {
        "heal":       "Auto-fixed — service was restarted automatically",
        "escalate":   "Escalated to a human — needs manual review",
        "do_nothing": "Monitoring — no action needed right now",
    }.get(action, action)

    ts = latest.get("timestamp", "")[:19].replace("T", " at ")

    st.markdown(
        f"""
        <div class="card">
            <div style="font-size:1.3rem; font-weight:700; margin-bottom:0.4rem;">
                {status_emoji} {incident_type.replace('_', ' ').title()} Detected
            </div>
            <div style="margin-bottom:0.5rem; color:{colors['muted']}; font-size:0.9rem;">{ts}</div>
            <div style="margin-bottom:0.8rem;"><strong>What happened:</strong> {rca_short}</div>
            <div><strong>Action taken:</strong> {action_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_trace(trace: list):
    if not trace:
        st.info("No agent trace available.")
        return

    ordered = sorted(
        trace,
        key=lambda x: AGENT_ORDER.index(x["agent"]) if x["agent"] in AGENT_ORDER else 99,
    )
    for step in ordered:
        agent = step["agent"]
        title, desc = AGENT_LABELS.get(agent, (agent, ""))
        ts = step.get("timestamp", "")[:19].replace("T", " at ")
        st.markdown(
            f"""
            <div class="trace-step">
                <span class="trace-agent">{title}</span>
                <span class="trace-time"> &nbsp;·&nbsp; {ts}</span><br/>
                <small style="color:{colors['muted']}">{desc}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_history_and_perf(incidents: list):
    df = pd.DataFrame(incidents)

    st.markdown("### Agent Performance")
    avg_reduction = (df["cpu_before"] - df["cpu_after"]).mean() if "cpu_after" in df.columns else 0
    success_rate  = round((df["success"].sum() / len(df)) * 100, 1) if len(df) > 0 else 0.0
    avg_agents    = sum(len(i.get("agent_trace") or []) for i in incidents) / len(incidents) if incidents else 0

    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown(
            f'<div class="card"><div class="metric-title">Success Rate (%)</div>'
            f'<div class="metric-value">{success_rate:.1f}</div></div>',
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown(
            f'<div class="card"><div class="metric-title">Avg CPU Reduction</div>'
            f'<div class="metric-value">{avg_reduction:.3f}</div></div>',
            unsafe_allow_html=True,
        )
    with p3:
        st.markdown(
            f'<div class="card"><div class="metric-title">Avg Agents / Incident</div>'
            f'<div class="metric-value">{avg_agents:.0f}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("### Incident History")
    display_cols = [c for c in ["timestamp", "incident_type", "cpu_before", "cpu_after", "action_taken", "success"] if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# MODE: DEMO
# ═════════════════════════════════════════════════════════════════════════════
if mode == "Demo":
    st.info("Demo Mode — showing sample recorded incidents.")
    incidents = load_demo_data()
    if not incidents:
        st.warning("No demo data found.")
        st.stop()

    latest = incidents[-1]
    render_metrics(latest)
    render_status_card(latest)
    st.markdown("### Agent Trace Timeline")
    render_trace(latest.get("agent_trace") or [])
    render_history_and_perf(incidents)


# ═════════════════════════════════════════════════════════════════════════════
# MODE: LIVE
# ═════════════════════════════════════════════════════════════════════════════
elif mode == "Live (local)":
    incidents = load_live_data()
    if not incidents:
        st.warning(
            "**Live Mode** reads `incidents.log` from your local machine.  \n"
            "No incidents found yet. Run the pipeline with:  \n"
            "```\npython scripts/spike_cpu.py --duration 40 --auto\n```"
        )
        st.stop()

    st.success(f"Loaded {len(incidents)} live incident(s) from `incidents.log`.")
    latest = incidents[-1]
    render_metrics(latest)
    render_status_card(latest)
    st.markdown("### Agent Trace Timeline")
    render_trace(latest.get("agent_trace") or [])
    render_history_and_perf(incidents)


# ═════════════════════════════════════════════════════════════════════════════
# MODE: SIMULATE  (works on deployed Streamlit Cloud — no infra needed)
# ═════════════════════════════════════════════════════════════════════════════
elif mode == "Simulate":
    st.markdown("### Interactive Incident Simulation")
    st.markdown(
        f"<span style='color:{colors['muted']}'>Simulate a real incident and watch the agents respond step by step — no infrastructure needed.</span>",
        unsafe_allow_html=True,
    )

    # Scenario picker
    scenario = st.selectbox(
        "Choose an incident scenario:",
        [
            "Traffic spike — CPU overload",
            "Health-check loop — sustained load",
            "Memory leak — gradual saturation",
        ],
    )

    SCENARIOS = {
        "Traffic spike — CPU overload": {
            "incident_type": "HIGH_CPU",
            "cpu_before": round(random.uniform(0.75, 0.95), 3),
            "cpu_after":  round(random.uniform(0.10, 0.25), 3),
            "memory_before": 52428800,
            "action_taken": "heal",
            "success": True,
            "rca": "A sudden surge in HTTP traffic overwhelmed nginx worker processes, causing CPU saturation.",
            "steps": [
                ("MonitorAgent",       0.8,  "Detected CPU above threshold — anomaly flagged"),
                ("DiagnosticianAgent", 1.5,  "Pulled container logs — identified traffic spike pattern"),
                ("PlannerAgent",       1.2,  "Evaluated options — heal (restart) is safe given no recent failures"),
                ("SafetyCriticAgent",  0.6,  "Cooldown check passed — approved heal action"),
                ("ExecutorAgent",      1.0,  "Restarted nginx container"),
                ("VerifierAgent",      1.5,  "CPU re-checked — back within safe limits"),
                ("ReporterAgent",      0.5,  "Incident report saved"),
            ],
        },
        "Health-check loop — sustained load": {
            "incident_type": "HIGH_CPU",
            "cpu_before": round(random.uniform(0.60, 0.80), 3),
            "cpu_after":  round(random.uniform(0.15, 0.30), 3),
            "memory_before": 48234496,
            "action_taken": "heal",
            "success": True,
            "rca": "A misconfigured health-check was hammering the nginx endpoint every 100ms, creating sustained load.",
            "steps": [
                ("MonitorAgent",       0.8,  "Detected sustained CPU above safe threshold"),
                ("DiagnosticianAgent", 1.5,  "Found repeated requests from internal health-check in logs"),
                ("PlannerAgent",       1.2,  "Restart will reset connection pool — heal proposed"),
                ("SafetyCriticAgent",  0.6,  "No recent failed recoveries — heal approved"),
                ("ExecutorAgent",      1.0,  "Restarted nginx container"),
                ("VerifierAgent",      1.5,  "CPU dropped — service healthy"),
                ("ReporterAgent",      0.5,  "Incident report saved"),
            ],
        },
        " Memory leak — gradual saturation": {
            "incident_type": "HIGH_CPU",
            "cpu_before": round(random.uniform(0.50, 0.70), 3),
            "cpu_after":  round(random.uniform(0.40, 0.55), 3),
            "memory_before": 920000000,
            "action_taken": "escalate",
            "success": False,
            "rca": "Memory usage is abnormally high — a possible leak in a worker process. CPU follows from swap pressure.",
            "steps": [
                ("MonitorAgent",       0.8,  "Detected CPU anomaly with unusually high memory usage"),
                ("DiagnosticianAgent", 1.5,  "Memory at 876 MB — pattern consistent with a memory leak"),
                ("PlannerAgent",       1.2,  "A restart would mask the leak — escalate for investigation"),
                ("SafetyCriticAgent",  0.6,  "Escalation approved — no automated action taken"),
                ("ReporterAgent",      0.5,  "Incident escalated and saved to log"),
            ],
        },
    }

    chosen = SCENARIOS[scenario]

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        run = st.button("▶️Run Simulation", type="primary", use_container_width=True)
    with col_info:
        st.markdown(
            f"<small style='color:{colors['muted']}'>Simulates the full agent pipeline step by step in real time.</small>",
            unsafe_allow_html=True,
        )

    if run or st.session_state.get("sim_done"):
        if run:
            st.session_state["sim_done"] = False
            st.session_state["sim_result"] = None

        if run and not st.session_state.get("sim_done"):
            # ── Animate CPU spike ────────────────────────────────────────────
            st.markdown("#### CPU Spike Detected")
            cpu_bar = st.progress(0, text="CPU: 0%")
            target  = int(chosen["cpu_before"] * 100)
            for v in range(0, target + 1, 5):
                cpu_bar.progress(min(v, 100) / 100, text=f"CPU: {v}% {'🔴' if v > 50 else '🟡'}")
                time.sleep(0.04)
            st.markdown(
                f"<div class='card'>🚨 <strong>Anomaly detected</strong> — CPU at <strong>{chosen['cpu_before']*100:.0f}%</strong></div>",
                unsafe_allow_html=True,
            )

            # ── Stream agent steps ────────────────────────────────────────────
            st.markdown("#### Agent Pipeline Running...")
            trace = []
            steps = chosen["steps"]

            for agent, delay, action_desc in steps:
                title, desc = AGENT_LABELS.get(agent, (agent, ""))
                placeholder = st.empty()
                placeholder.markdown(
                    f"""<div class="trace-step" style="opacity:0.5;">
                        <span class="trace-agent">{title}</span>
                        <span class="trace-time"> &nbsp;·&nbsp; running...</span><br/>
                        <small style="color:{colors['muted']}">{action_desc}</small>
                    </div>""",
                    unsafe_allow_html=True,
                )
                time.sleep(delay)
                ts = datetime.now().isoformat()
                placeholder.markdown(
                    f"""<div class="trace-step">
                        <span class="trace-agent">{title}</span>
                        <span class="trace-time"> &nbsp;·&nbsp; {ts[:19].replace("T", " at ")}</span><br/>
                        <small style="color:{colors['muted']}">{action_desc}</small>
                    </div>""",
                    unsafe_allow_html=True,
                )
                trace.append({
                    "agent": agent,
                    "input_summary": action_desc,
                    "output": {"action": action_desc},
                    "timestamp": ts,
                })

            # ── CPU recovery animation ────────────────────────────────────────
            if chosen["action_taken"] == "heal":
                st.markdown("#### Recovery in progress...")
                cpu_bar2 = st.progress(int(chosen["cpu_before"] * 100) / 100, text="Restarting service...")
                current = int(chosen["cpu_before"] * 100)
                target2 = int(chosen["cpu_after"] * 100)
                for v in range(current, target2 - 1, -5):
                    cpu_bar2.progress(max(v, 0) / 100, text=f"CPU: {v}% {'✅' if v < 30 else '🟡'}")
                    time.sleep(0.05)

            result = {**chosen, "timestamp": datetime.now().isoformat(), "agent_trace": trace}
            st.session_state["sim_result"] = result
            st.session_state["sim_done"]   = True
            st.rerun()

        # ── Show final results ────────────────────────────────────────────────
        result = st.session_state.get("sim_result")
        if result:
            st.markdown("---")
            st.markdown("### Simulation Complete")
            render_metrics(result)
            render_status_card(result)
