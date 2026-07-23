from langgraph.graph import END

from core.agent_state import IncidentState


def route_after_monitor(state: IncidentState) -> str:
    if state.get("anomaly_detected"):
        return "diagnose"
    return END


def route_after_safety(state: IncidentState) -> str:
    decision = state.get("decision")
    if decision == "heal":
        return "execute"
    if decision == "escalate":
        return "report"
    return END
