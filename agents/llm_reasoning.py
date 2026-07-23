"""Deprecated: use diagnostician_agent and planner_agent instead."""

from agents.diagnostician_agent import diagnose
from agents.planner_agent import plan_action
from core.memory import count_recent_fails


def decide_action_llm(
    state: str,
    cpu_before: float,
    cpu_after: float | None,
    recent_failures: int,
    safe_threshold: float = 0.6,
):
    if state == "NORMAL":
        return {
            "decision": "do_nothing",
            "reasoning": ["CPU below safe threshold"],
        }

    if recent_failures >= 2:
        return {
            "decision": "escalate",
            "reasoning": ["Multiple failed recoveries detected"],
        }

    diag = diagnose("HIGH_CPU", cpu_before, None)
    plan = plan_action("HIGH_CPU", cpu_before, diag["rca"], recent_failures)
    return {
        "decision": plan["proposed_action"],
        "reasoning": plan.get("reasoning", []),
    }
