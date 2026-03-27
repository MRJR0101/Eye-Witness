"""
Simple benchmark harness for logging overhead.

Run:
    python scripts/benchmark_logging.py
"""

from __future__ import annotations

import os
import time
from contextlib import redirect_stderr, redirect_stdout

from eye_witness import get_logger, init, shutdown


def run_once(iterations: int = 10000) -> float:
    init(
        service_name="bench",
        log_format="json",
        otel_exporter="none",
        metrics_enabled=False,
        flush_on_exit=False,
        force=True,
    )
    log = get_logger("bench")
    started = time.perf_counter()
    with open(os.devnull, "w", encoding="utf-8") as sink, redirect_stdout(sink), redirect_stderr(
        sink
    ):
        for idx in range(iterations):
            log.info(
                "bench.event",
                iteration=idx,
                sample_field="masked-value",
                sample_token="bench-token",
            )
    elapsed = time.perf_counter() - started
    shutdown()
    return elapsed


def main() -> None:
    iterations = 2000
    elapsed = run_once(iterations)
    per_sec = iterations / elapsed
    print(f"iterations={iterations}")
    print(f"elapsed_sec={elapsed:.4f}")
    print(f"events_per_sec={per_sec:.2f}")


if __name__ == "__main__":
    main()
