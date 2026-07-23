import requests

PROMETHEUS_URL = "http://localhost:9090/api/v1/query"


def query_prometheus(query: str) -> dict:
    response = requests.get(
        PROMETHEUS_URL,
        params={"query": query},
        timeout=10,
    )
    return response.json()


def _avg_from_query(query: str, default: float = 0.0) -> float:
    data = query_prometheus(query)
    results = data.get("data", {}).get("result", [])
    if not results:
        return default
    values = [float(item["value"][1]) for item in results]
    return sum(values) / len(values)


def get_avg_cpu() -> float:
    avg_cpu = _avg_from_query(
        'rate(container_cpu_usage_seconds_total{name="nginx"}[30s])'
    )
    print("DEBUG: avg_cpu=", avg_cpu)
    return avg_cpu


def get_memory_usage() -> float:
    memory = _avg_from_query(
        'container_memory_usage_bytes{name="nginx"}'
    )
    print("DEBUG: memory_bytes=", memory)
    return memory


if __name__ == "__main__":
    print("CPU: ", get_avg_cpu())
    print("Memory: ", get_memory_usage())
