from datetime import datetime


def build_summary(
    incident_type: str,
    cpu_before: float,
    cpu_after: float,
    decision: str,
    success: bool,
    rca: str | None,
    agent_trace: list,
) -> str:
    agents_involved = " -> ".join(entry["agent"] for entry in agent_trace)
    status = "RESOLVED" if success else "UNRESOLVED"

    return (
        f"[{status}] {incident_type} incident at {datetime.now().isoformat()}. "
        f"CPU {cpu_before:.3f} -> {cpu_after:.3f}. Action: {decision}. "
        f"RCA: {rca or 'N/A'}. Agent pipeline: {agents_involved}."
    )
