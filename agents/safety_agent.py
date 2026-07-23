from core.memory import count_recent_fails
from core.safety import can_act

MAX_FAILED_ATTEMPTS = 2


def evaluate_safety(
    proposed_action: str,
    incident_type: str,
) -> dict:
    recent_failures = count_recent_fails(incident_type)

    if recent_failures >= MAX_FAILED_ATTEMPTS:
        return {
            "safety_verdict": "escalate",
            "decision": "escalate",
            "reasoning": [
                f"{recent_failures} recent failed recoveries — forcing escalation",
            ],
        }

    if proposed_action == "heal":
        if not can_act():
            return {
                "safety_verdict": "rejected",
                "decision": "do_nothing",
                "reasoning": ["Cooldown active — blocking heal to prevent action loop"],
            }
        return {
            "safety_verdict": "approved",
            "decision": "heal",
            "reasoning": ["Heal action passed safety checks"],
        }

    if proposed_action == "escalate":
        return {
            "safety_verdict": "approved",
            "decision": "escalate",
            "reasoning": ["Escalation approved"],
        }

    return {
        "safety_verdict": "approved",
        "decision": "do_nothing",
        "reasoning": ["No action required per planner"],
    }
