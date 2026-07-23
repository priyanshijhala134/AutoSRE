from agents.tools import restart_service


def execute(decision: str, incident_type: str) -> dict:
    if decision != "heal":
        return {"executed": False, "detail": f"No execution for decision={decision}"}

    if incident_type == "HIGH_CPU":
        success = restart_service("nginx")
        return {
            "executed": True,
            "detail": "Restarted nginx container",
            "success": success,
        }

    return {"executed": False, "detail": f"Unknown incident type: {incident_type}"}
