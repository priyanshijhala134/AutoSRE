# CPU threshold in cores/second (Prometheus rate metric, NOT a percentage).
# Baseline nginx CPU: ~0.0001. A curl spike produces ~0.01-0.05.
CPU_HIGH_THRESHOLD = 0.005