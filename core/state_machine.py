# flow controller
from agents.monitoring_agent import get_avg_cpu

def monitor_state():
    cpu=get_avg_cpu
    
    if cpu>0.8:
        return "HIGH CPU"
    return "NORMAL CPU"
# FAKE METRICS
# from agents.monitoring_agent import MonitoringAgent
# from agents.monitoring_agent import MonitoringAgent
# from agents.diagnosis_agent import DiagnosisAgent
# from agents.audit_agent import AuditAgent
# from agents.action_agent import ActionAgent

# class NetOpsStateMachine:
#     def __init__(self):
#         self.monitor=MonitoringAgent()
#         self.diagnose=DiagnosisAgent()
#         self.act=ActionAgent()
#         self.audit=AuditAgent()
        
        
#     def run(self,metrics,post_action_metrics):
#         incident=self.monitor.detect(metrics)
#         if not incident:
#             return None
#         incident=self.diagnose.diagnose(incident)
#         incident=self.act.act(incident)
#         incident=self.audit.audit(incident)
        
#         return incident