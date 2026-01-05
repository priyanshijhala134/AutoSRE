# flow controller
import sys
import os

# Add the parent directory (netops-sentinel) to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.monitoring_agent import MonitoringAgent
from agents.monitoring_agent import MonitoringAgent
from agents.diagnosis_agent import DiagnosisAgent
from agents.audit_agent import AuditAgent
from agents.action_agent import ActionAgent

class NetOpsStateMachine:
    def __init__(self):
        self.monitor=MonitoringAgent()
        self.diagnose=DiagnosisAgent()
        self.act=ActionAgent()
        self.audit=AuditAgent()
        
        
    def run(self,metrics,post_action_metrics):
        incident=self.monitor.detect(metrics)
        if not incident:
            return None
        incident=self.diagnose.diagnose(incident)
        incident=self.act.act(incident)
        incident=self.audit.audit(incident)
        
        return incident