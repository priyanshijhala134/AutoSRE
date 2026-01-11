# flow controller
import sys
import os
import time

# ---------- Path setup ----------
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# ---------- Imports ----------
from agents.reasoning_agents import decide_action
from core.memory import count_recent_fails
from agents.monitoring_agent import get_avg_cpu
from agents.healing_agent import heal
from core.reporter import generate_incident_report, save_report

# ---------- Config ----------
MAX_FAILED_ATTEMPTS = 2
CPU_THRESHOLD = 0.75


def monitor_state():
    print("agent started")

    # Allow Prometheus window to stabilise
    time.sleep(20)

    # ----- Observe -----
    cpu = get_avg_cpu()
    cpu_before = cpu

    print("DEBUG: avg_cpu=", cpu_before)

    if cpu_before > CPU_THRESHOLD:
        state = "HIGH_CPU"
    else:
        state = "NORMAL"

    print("Current State: ", state)

    # ----- Decide & Act -----
    if state == "HIGH_CPU":

        fails = count_recent_fails("HIGH_CPU")

        decision_payload = decide_action(
            state=state,
            cpu_before=cpu_before,
            cpu_after=None,
            recent_failures=fails
        )

        for step in decision_payload["reasoning"]:
            print("REASON:", step)

        decision = decision_payload["decision"]

        if decision == "do_nothing":
            print("System stable. No action taken.")
            return

        elif decision == "heal" or decision == "retry_heal":
            print("Attempting auto-heal: Restarting nginx...")
            healed = heal(state)
            time.sleep(5)
            cpu_after = get_avg_cpu()

        elif decision == "escalate":
            print("Escalation triggered: Too many failed recoveries")
            cpu_after = cpu_before


        # ----- Report -----
        report = generate_incident_report(
            incident_type="HIGH_CPU",
            cpu_before=cpu_before,
            cpu_after=cpu_after,
            action_taken=decision,
            success=cpu_after < cpu_before
        )

        save_report(report)
        print("Incident report saved")

    else:
        print("System is healthy. No report needed.")


if __name__ == "__main__":
    monitor_state()
