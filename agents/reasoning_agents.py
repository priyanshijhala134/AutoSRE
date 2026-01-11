def decide_action(state,cpu_before,cpu_after,recent_failures):
    
    reasoning=[]
    reasoning.append(f"system state is {state}")
    reasoning.append(f"cpu before action {cpu_before}")
    reasoning.append(f"cpu after last action {cpu_after}")
    reasoning.append(f"recent failed recoveries {recent_failures}")
    
    if state=="NORMAL":
        decision="do_nothing"
        reasoning.append("system is healthy, no actions required")
    
    elif recent_failures>=2:
        decision="escalate"
        reasoning.append("multiple failed recoveries detected. escalation required")
    
    elif cpu_after is not None and cpu_after>cpu_before:
        decision="retry_heal"
        reasoning.append("cpu worsened after healing, retrying once")
    else:
        decision="heal"
        reasoning.append("cpu is high, attempting auto-heal")
    return{
        "decision":decision,
        "reasoning":reasoning
    }