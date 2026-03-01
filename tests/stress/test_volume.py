from eye_witness import get_logger, init, shutdown


def test_log_volume_smoke():
    init(otel_exporter="none", metrics_enabled=False, flush_on_exit=False, force=True)
    log = get_logger("stress.volume")
    for i in range(1000):
        log.info("stress.volume.event", i=i)
    shutdown()
