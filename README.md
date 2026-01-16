# AutoSRE
## Autonomous Ops Agent

## Overview

Autonomous Ops Agent is a GenAI-powered, policy-constrained operations system that **detects infrastructure anomalies, reasons about corrective actions, and executes safe self-healing workflows** with full observability and auditability.

The system follows a **deterministic-first, LLM-as-planner** philosophy:

* **Detection** is rule-based and metrics-driven
* **Decision-making** is assisted by an LLM under strict safety policies
* **Execution** is automated but reversible

---
---
## Live Demo: "https://autonomous-sre-agent.streamlit.app/"
---

## Problem Statement

Modern infrastructure failures (e.g., CPU saturation) are detected quickly but often require **manual triage and intervention**, increasing Mean Time To Recovery (MTTR).

This project demonstrates how **agentic AI** can:

* Reduce MTTR
* Enforce safety constraints
* Provide explainable, auditable decisions

---

## Architecture

### High-Level Flow

1. **Monitoring Agent** pulls CPU metrics from Prometheus
2. **State Evaluator** determines NORMAL vs HIGH_CPU
3. **Decision Agent (LLM)** proposes an action under policy constraints
4. **Execution Agent** performs healing (service restart)
5. **Verification Agent** validates recovery
6. **Reporter** logs incident + exposes dashboard

---

## Agent Roles

### Monitoring Agent

* Queries Prometheus
* Computes average CPU usage
* Emits structured signals (cpu_before, is_high)

### Decision Agent (LLM)

* Considers system state + recent failures
* Outputs constrained actions: `heal`, `escalate`, `do_nothing`
* Never executes actions directly

### Healing Agent

* Executes OS-level remediation (nginx restart)
* Implements rollback-safe commands

### Verification Agent

* Re-checks metrics post-action
* Determines success/failure

### Reporter

* Writes structured incident logs (JSONL)
* Feeds Streamlit dashboard

---

## Safety & Guardrails

* Confidence thresholds for actions
* Failure memory to prevent infinite loops
* Escalation after repeated failures
* Deterministic overrides over LLM output

---

## Chaos Scenarios Tested

* Sustained CPU saturation
* Repeated failed recoveries
* LLM decision under partial information

---

## Observability

* Prometheus for metrics
* Incident logs (JSONL)
* Streamlit Ops Dashboard

---

## Dashboard

The dashboard provides:

* Current system state
* Incident history
* Success rate
* Average CPU reduction
* Dark/light theme switching

---

## Tech Stack

* Python
* Docker & Docker Compose
* Prometheus
* LangGraph
* Gemini / LLM API
* Streamlit

---

## Key Design Decisions

* **LLM is advisory, not authoritative**
* **Rules override AI for safety**
* **Explainability over blind automation**

---

## Results

* Demonstrated automated CPU recovery
* Reduced simulated MTTR significantly
* Zero unsafe actions executed

---

## Future Work

* Multi-metric reasoning (memory, disk)
* Horizontal scaling actions
* PagerDuty / Slack escalation
* Kubernetes-native deployment

---

## How to Run

```bash
docker compose up
python -m core.runner
streamlit run frontend/dashboard.py
```
