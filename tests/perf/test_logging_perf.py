from eye_witness import get_logger, init, shutdown


def test_logging_perf_smoke():
    init(otel_exporter="none", metrics_enabled=False, flush_on_exit=False, force=True)
    log = get_logger("perf.logging")
    for i in range(100):
        log.info("perf.log", i=i, token="x")
    shutdown()
