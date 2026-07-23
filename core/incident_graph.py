import time
from datetime import datetime

from langgraph.graph import END, StateGraph

from agents.diagnostician_agent import diagnose
from agents.executor_agent import execute
from agents.monitoring_agent import get_avg_cpu, get_memory_usage
from agents.planner_agent import plan_action
from agents.reporter_agent import build_summary
from agents.safety_agent import evaluate_safety
from agents.supervisor import route_after_monitor, route_after_safety
from agents.verifier_agent import verify
from config.threshold import CPU_HIGH_THRESHOLD
from core.agent_state import IncidentState, trace_update
from core.memory import count_recent_fails
from core.reporter import save_report


def monitor_node(state: IncidentState) -> dict:
    cpu = get_avg_cpu()
    memory = get_memory_usage()
    anomaly = cpu >= CPU_HIGH_THRESHOLD
    incident_type = "HIGH_CPU" if anomaly else None
    system_state = "HIGH_CPU" if anomaly else "NORMAL"

    output = {
        "cpu_before": cpu,
        "memory_before": memory,
        "anomaly_detected": anomaly,
        "incident_type": incident_type,
        "state": system_state,
    }

    if not anomaly:
        print("SYSTEM: CPU within safe limits, no action required")

    trace = trace_update(
        state,
        "MonitorAgent",
        f"cpu={cpu:.3f}, memory={memory:.0f}",
        output,
    )
    return {**output, **trace}


def diagnostician_node(state: IncidentState) -> dict:
    result = diagnose(
        incident_type=state["incident_type"],
        cpu_before=state["cpu_before"],
        memory_before=state.get("memory_before"),
    )
    for line in result.get("hypothesis", []):
        print("DIAG_HYPOTHESIS:", line)

    trace = trace_update(
        state,
        "DiagnosticianAgent",
        f"incident={state['incident_type']}",
        result,
    )
    return {"rca": result["rca"], **trace}


def planner_node(state: IncidentState) -> dict:
    fails = count_recent_fails(state["incident_type"])
    result = plan_action(
        incident_type=state["incident_type"],
        cpu_before=state["cpu_before"],
        rca=state.get("rca", ""),
        recent_failures=fails,
    )
    for r in result.get("reasoning", []):
        print("PLANNER:", r)

    trace = trace_update(
        state,
        "PlannerAgent",
        f"rca={state.get('rca', '')[:80]}",
        result,
    )
    return {"proposed_action": result["proposed_action"], **trace}


def safety_node(state: IncidentState) -> dict:
    result = evaluate_safety(
        proposed_action=state["proposed_action"],
        incident_type=state["incident_type"],
    )
    for r in result.get("reasoning", []):
        print("SAFETY:", r)

    trace = trace_update(
        state,
        "SafetyCriticAgent",
        f"proposed={state['proposed_action']}",
        result,
    )
    return {
        "safety_verdict": result["safety_verdict"],
        "decision": result["decision"],
        **trace,
    }


def execute_node(state: IncidentState) -> dict:
    print("Executing approved heal action...")
    result = execute(state["decision"], state["incident_type"])
    print(result["detail"])

    trace = trace_update(
        state,
        "ExecutorAgent",
        f"decision={state['decision']}",
        result,
    )
    return trace


def verify_node(state: IncidentState) -> dict:
    print("Waiting for system stabilization...")
    time.sleep(10)

    result = verify(state["cpu_before"], state["decision"])
    print(result["detail"])

    trace = trace_update(
        state,
        "VerifierAgent",
        f"decision={state['decision']}",
        result,
    )
    return {"cpu_after": result["cpu_after"], **trace}


def report_node(state: IncidentState) -> dict:
    cpu_after = state.get("cpu_after")
    if cpu_after is None:
        cpu_after = get_avg_cpu()

    decision = state.get("decision", "do_nothing")
    success = (
        decision == "heal"
        and cpu_after < CPU_HIGH_THRESHOLD
        and (state["cpu_before"] - cpu_after) >= 0.05
    )
    if decision == "escalate":
        success = False

    summary = build_summary(
        incident_type=state["incident_type"],
        cpu_before=state["cpu_before"],
        cpu_after=cpu_after,
        decision=decision,
        success=success,
        rca=state.get("rca"),
        agent_trace=state.get("agent_trace") or [],
    )
    print("REPORT:", summary)

    report = {
        "timestamp": datetime.now().isoformat(),
        "incident_type": state["incident_type"],
        "cpu_before": state["cpu_before"],
        "cpu_after": cpu_after,
        "memory_before": state.get("memory_before"),
        "action_taken": decision,
        "success": success,
        "rca": state.get("rca"),
        "summary": summary,
        "agent_trace": state.get("agent_trace") or [],
    }
    save_report(report)
    print("Incident report saved")

    trace = trace_update(state, "ReporterAgent", "final summary", summary)
    return {"cpu_after": cpu_after, "success": success, "summary": summary, **trace}


graph = StateGraph(IncidentState)

graph.add_node("monitor", monitor_node)
graph.add_node("diagnose", diagnostician_node)
graph.add_node("plan", planner_node)
graph.add_node("safety", safety_node)
graph.add_node("execute", execute_node)
graph.add_node("verify", verify_node)
graph.add_node("report", report_node)

graph.set_entry_point("monitor")

graph.add_conditional_edges("monitor", route_after_monitor, {
    "diagnose": "diagnose",
    END: END,
})

graph.add_edge("diagnose", "plan")
graph.add_edge("plan", "safety")

graph.add_conditional_edges("safety", route_after_safety, {
    "execute": "execute",
    "report": "report",
    END: END,
})

graph.add_edge("execute", "verify")
graph.add_edge("verify", "report")
graph.add_edge("report", END)

incident_graph = graph.compile()
