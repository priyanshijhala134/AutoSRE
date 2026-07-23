from agents.llm_client import call_gemini, llm_available
from agents.tools import get_container_logs


def diagnose(
    incident_type: str,
    cpu_before: float,
    memory_before: float | None,
) -> dict:
    logs_snippet = get_container_logs("nginx", tail=20)

    if not llm_available():
        rca = (
            f"Rule-based RCA: {incident_type} detected "
            f"(CPU={cpu_before:.3f}, memory={memory_before}). "
            "Likely traffic spike or nginx worker saturation."
        )
        return {
            "rca": rca,
            "hypothesis": ["traffic_spike", "worker_saturation"],
            "confidence": "medium",
        }

    prompt = f"""
You are an SRE diagnostician agent. Analyze the incident and propose root cause.

Incident type: {incident_type}
CPU usage: {cpu_before}
Memory bytes: {memory_before}
Recent nginx logs:
{logs_snippet}

Respond ONLY in JSON:
{{
  "rca": "one paragraph root cause analysis",
  "hypothesis": ["cause1", "cause2"],
  "confidence": "low|medium|high"
}}
"""
    try:
        return call_gemini(prompt)
    except Exception as e:
        return {
            "rca": f"Diagnostician fallback: unable to reach LLM ({e})",
            "hypothesis": ["unknown"],
            "confidence": "low",
        }
