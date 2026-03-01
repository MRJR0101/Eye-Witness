"""
Simple tracing benchmark.
"""

from __future__ import annotations

import time

from eye_witness import init, shutdown, trace_span


def main() -> None:
    init(otel_exporter="none", metrics_enabled=False, flush_on_exit=False, force=True)
    n = 20000
    started = time.perf_counter()
    for _ in range(n):
        with trace_span("bench.trace"):
            pass
    elapsed = time.perf_counter() - started
    shutdown()
    print(f"spans={n}")
    print(f"elapsed_sec={elapsed:.4f}")
    print(f"spans_per_sec={n / elapsed:.2f}")


if __name__ == "__main__":
    main()
