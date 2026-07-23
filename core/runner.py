import sys
import os
import io

# Force UTF-8 output so emojis/arrows don't crash on Windows CP1252 terminals
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


from dotenv import load_dotenv
load_dotenv()

from core.incident_graph import incident_graph

if __name__ == "__main__":
    result = incident_graph.invoke({"agent_trace": []})
    print("\n=== Agent Trace ===")
    for entry in result.get("agent_trace", []):
        print(f"  [{entry['agent']}] {entry['output']}")
