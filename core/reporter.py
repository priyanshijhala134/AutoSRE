from datetime import datetime
import json

CPU_RECOVERY_THRESHOLD = 0.65
MIN_CPU_IMPROVEMENT = 0.15


def generate_incident_report(
    incident_type,
    cpu_before,
    cpu_after,
    action_taken,
    agent_trace=None,
    rca=None,
    summary=None,
    memory_before=None,
):
    success = (
        cpu_after < CPU_RECOVERY_THRESHOLD
        and (cpu_before - cpu_after) >= MIN_CPU_IMPROVEMENT
    )

    report = {
        "timestamp": datetime.now().isoformat(),
        "incident_type": incident_type,
        "cpu_before": cpu_before,
        "cpu_after": cpu_after,
        "memory_before": memory_before,
        "action_taken": action_taken,
        "success": success,
        "rca": rca,
        "summary": summary,
        "agent_trace": agent_trace or [],
    }

    save_report(report)
    return report


def save_report(report, path="incidents.log"):
    with open(path, "a") as f:
        f.write(json.dumps(report) + "\n")
