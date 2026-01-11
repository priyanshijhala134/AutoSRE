import json
# agent memory
def load_incidents(path="incidents.log"):
    incidents=[]
    try:
        with open(path,"r") as f:
            for line in f:
                incidents.append(json.loads(line))
    except FileNotFoundError:
        pass
    return incidents

def count_recent_fails(incident_type,limit=5):
    incidents=load_incidents()
    recent=incidents[-limit:]
    failures=[
        i for i in recent
        if i["incident_type"]== incident_type and not i["success"]
    ]
    return len(failures)

def reset_memory():
    with open("incidents.log", "w") as f:
        pass
