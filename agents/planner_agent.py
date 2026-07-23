from agents.llm_client import call_gemini, llm_available


def plan_action(
    incident_type: str,
    cpu_before: float,
    rca: str,
    recent_failures: int,
) -> dict:
    if not llm_available():
        return {
            "proposed_action": "heal",
            "reasoning": ["Rule-based fallback (no LLM key): restart nginx"],
        }

    prompt = f"""
You are an SRE planner agent. Given root cause analysis, propose ONE action.

Allowed actions:
- heal (restart affected service)
- escalate (human intervention)
- do_nothing (wait and observe)

Incident type: {incident_type}
CPU before: {cpu_before}
Recent failed recoveries: {recent_failures}
Root cause analysis: {rca}

Respond ONLY in JSON:
{{
  "proposed_action": "heal|escalate|do_nothing",
  "reasoning": ["step1", "step2"]
}}
"""
    try:
        result = call_gemini(prompt)
        action = result.get("proposed_action") or result.get("decision", "escalate")
        return {
            "proposed_action": action,
            "reasoning": result.get("reasoning", []),
        }
    except Exception as e:
        return {
            "proposed_action": "escalate",
            "reasoning": [f"Planner error, failing safe: {e}"],
        }
