from config.threshold import CPU_HIGH_THRESHOLD
from agents.monitoring_agent import get_avg_cpu, get_memory_usage


def verify(cpu_before: float, decision: str) -> dict:
    if decision != "heal":
        return {
            "cpu_after": cpu_before,
            "memory_after": get_memory_usage(),
            "recovered": False,
            "detail": "Verification skipped — no heal executed",
        }

    cpu_after = get_avg_cpu()
    memory_after = get_memory_usage()
    recovered = cpu_after < CPU_HIGH_THRESHOLD

    return {
        "cpu_after": cpu_after,
        "memory_after": memory_after,
        "recovered": recovered,
        "detail": f"CPU after heal: {cpu_after:.3f} (threshold {CPU_HIGH_THRESHOLD})",
    }
