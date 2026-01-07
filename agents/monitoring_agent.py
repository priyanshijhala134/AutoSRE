import requests

PROMETHEUS_URL="http://localhost:9090/api/v1/query"


def get_avg_cpu():
    data = query_prometheus("rate(node_cpu_seconds_total[1m])")
    values = [
        float(item["value"][1])
        for item in data["data"]["result"]
    ]
    return sum(values) / len(values)

def query_prometheus(query:str):
    response=requests.get(
        PROMETHEUS_URL,
        params={"query":query}
    )
    return response.json()

if __name__=="__main__":
    print("CPU: ", get_avg_cpu())
# FAKE METRICS 
# from core.incident import Incident
# # monitoring logic
# CPU_THRESHOLD=85
# LATENCY_THRESHOLD=300
# DB_CONN_THRESHOLD=90

# class MonitoringAgent:
#     def defect(self,metrics:dict)->Incident|None:
#         if metrics["cpu"]>CPU_THRESHOLD:
#             incident=Incident(
#                 incident_type="HIGH_CPU",
#                 metrics_snapshot=metrics
#             )
#             incident.log_event("High cpu detected")
#             return incident
        
#         if metrics["latency"]>LATENCY_THRESHOLD:
#             incident=Incident(
#                 incident_type="HIGH_LATENCY",
#                 metrics_snapshot=metrics
#             )
#             incident.log_event("High latency detected")
#             return incident
        
#         if metrics["db_connections"]>DB_CONN_THRESHOLD:
#             incident=Incident(
#                 incident_type="DBB_CONN_EXHAUSTION",
#                 metrics_snapshot=metrics
#             )
#             incident.log_event("DB connection exhaustion detected")
#             return incident
        
#         return None