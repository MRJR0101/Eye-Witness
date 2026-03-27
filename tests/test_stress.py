"""Stress tests for Eye-Witness lifecycle and logging."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import eye_witness._init as init_module
from eye_witness import get_logger, init, shutdown


def _reset_state() -> None:
    init_module._initialized = False
    init_module._config = None
    init_module._atexit_registered = False


def test_concurrent_init_shutdown_no_exceptions():
    _reset_state()
    errors: list[Exception] = []
    errors_lock = Lock()

    def worker(_: int) -> None:
        try:
            init(
                service_name="stress",
                force=True,
                flush_on_exit=False,
                otel_exporter="none",
                metrics_exporter="none",
                log_format="json",
            )
            shutdown()
        except Exception as exc:  # pragma: no cover - validated by assertion
            with errors_lock:
                errors.append(exc)

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(worker, range(64)))

    assert errors == []


def test_high_volume_threaded_logging_no_exceptions():
    _reset_state()
    init(
        service_name="stress-log",
        force=True,
        flush_on_exit=False,
        otel_exporter="none",
        metrics_enabled=False,
        log_format="json",
    )
    logger = get_logger("stress")
    errors: list[Exception] = []
    errors_lock = Lock()

    def worker(offset: int) -> None:
        try:
            for idx in range(500):
                logger.info(
                    "stress.event",
                    iteration=offset + idx,
                    sample_field="masked-value",
                )
        except Exception as exc:  # pragma: no cover
            with errors_lock:
                errors.append(exc)

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(worker, range(0, 4000, 500)))

    shutdown()
    assert errors == []
