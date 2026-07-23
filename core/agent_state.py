from datetime import datetime
from typing import Any, Optional, TypedDict


class AgentTraceEntry(TypedDict):
    agent: str
    input_summary: str
    output: Any
    timestamp: str


class IncidentState(TypedDict, total=False):
    # Metrics
    cpu_before: float
    cpu_after: Optional[float]
    memory_before: Optional[float]
    # Detection
    anomaly_detected: bool
    incident_type: Optional[str]
    state: str
    # Agent outputs
    rca: Optional[str]
    proposed_action: Optional[str]
    safety_verdict: Optional[str]
    decision: Optional[str]
    success: Optional[bool]
    summary: Optional[str]
    # Observability
    agent_trace: list[AgentTraceEntry]
    # Supervisor routing
    next_agent: Optional[str]


def append_trace(
    state: IncidentState,
    agent: str,
    input_summary: str,
    output: Any,
) -> list[AgentTraceEntry]:
    entry: AgentTraceEntry = {
        "agent": agent,
        "input_summary": input_summary,
        "output": output,
        "timestamp": datetime.now().isoformat(),
    }
    existing = list(state.get("agent_trace") or [])
    existing.append(entry)
    return existing


def trace_update(
    state: IncidentState,
    agent: str,
    input_summary: str,
    output: Any,
) -> dict:
    return {"agent_trace": append_trace(state, agent, input_summary, output)}
