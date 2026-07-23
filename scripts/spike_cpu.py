#!/usr/bin/env python3
"""Spike nginx container CPU for AutoSRE live demos.

Strategy: run a CPU-burn loop INSIDE the nginx container via `docker exec`.
cAdvisor measures that container's CPU directly, so Prometheus will capture it.
"""

import argparse
import subprocess
import sys
import threading
import time


# Shell one-liner that burns CPU inside the container.
# Uses /bin/sh (always present in nginx:latest).
CPU_BURN_CMD = (
    "sh -c 'i=0; while true; do i=$((i+1)); done'"
)


def _kill_burners(pids_in_container: list[str]) -> None:
    """Kill the CPU burner processes inside the nginx container."""
    for pid in pids_in_container:
        subprocess.run(
            ["docker", "exec", "nginx", "kill", pid],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def spike_cpu(duration: int = 30, workers: int = 4) -> None:
    """Run CPU-burning loops inside the nginx container."""
    print(f"Spiking nginx CPU for {duration}s with {workers} workers inside container...")
    print("Press Ctrl+C to stop early.\n")

    # Launch N background CPU burners inside the container
    burner_procs = []
    for i in range(workers):
        p = subprocess.Popen(
            ["docker", "exec", "nginx"] + CPU_BURN_CMD.split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        burner_procs.append(p)
        print(f"  Started burner {i+1}/{workers} (pid={p.pid})")

    print(f"\nBurning for {duration}s... (Prometheus scrape interval ~15s)\n")

    try:
        time.sleep(duration)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        print("Stopping CPU burners...")
        for p in burner_procs:
            p.terminate()
        # Also kill any leftover shells inside the container
        subprocess.run(
            ["docker", "exec", "nginx", "sh", "-c", "pkill -f 'while true' || true"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("Burners stopped.")


def run_agent_pipeline() -> None:
    """Run the multi-agent pipeline."""
    print("\n>>> [AUTO] Launching agent pipeline mid-spike...\n")
    subprocess.run([sys.executable, "-m", "core.runner"])


def main():
    parser = argparse.ArgumentParser(description="Spike nginx CPU for AutoSRE demo")
    parser.add_argument("--duration", type=int, default=30, help="Seconds to burn CPU (default: 30)")
    parser.add_argument("--workers", type=int, default=4, help="Concurrent CPU burners (default: 4)")
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto-launch agent pipeline 10s into the spike (recommended for demos)",
    )
    args = parser.parse_args()

    # Verify nginx container is running
    try:
        subprocess.run(
            ["docker", "inspect", "nginx"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        print("Error: nginx container not running. Start with: docker compose up -d")
        sys.exit(1)

    if args.auto:
        print("--auto mode: agent pipeline fires 10s into the spike (Prometheus warmup).\n")
        # Fire the runner after 10s so Prometheus has 1+ scrape cycles of data
        timer = threading.Timer(10.0, run_agent_pipeline)
        timer.start()
        try:
            spike_cpu(duration=args.duration, workers=args.workers)
        finally:
            timer.cancel()
        print("\nDone! Check the agent trace above for results.")
        print("Run: streamlit run frontend/dashboard.py  — to see the visual timeline.")
    else:
        spike_cpu(duration=args.duration, workers=args.workers)
        print("\nSpike done. Run the agent NOW (within 30s before Prometheus rate decays):")
        print("  python -m core.runner")


if __name__ == "__main__":
    main()
