import subprocess


def restart_service(service_name: str) -> bool:
    """Restart a Docker container and return True if successful."""
    try:
        subprocess.run(
            ["docker", "restart", service_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except subprocess.CalledProcessError as e:
        print("restart failed: ", e)
        return False


def get_container_logs(service_name: str, tail: int = 20) -> str:
    """Fetch recent container logs for diagnostician context."""
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", str(tail), service_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return result.stdout.strip() or "(no logs)"
    except subprocess.CalledProcessError as e:
        return f"(logs unavailable: {e})"
