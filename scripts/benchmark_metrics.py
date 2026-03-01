"""
Simple metrics benchmark.
"""

from __future__ import annotations

import time

from eye_witness import init, metric_counter, shutdown


def main() -> None:
    init(
        otel_exporter="none",
        metrics_enabled=True,
        metrics_exporter="none",
        flush_on_exit=False,
        force=True,
    )
    counter = metric_counter("bench.metrics.counter")
    n = 50000
    started = time.perf_counter()
    for _ in range(n):
        counter.add(1)
    elapsed = time.perf_counter() - started
    shutdown()
    print(f"points={n}")
    print(f"elapsed_sec={elapsed:.4f}")
    print(f"points_per_sec={n / elapsed:.2f}")


if __name__ == "__main__":
    main()
