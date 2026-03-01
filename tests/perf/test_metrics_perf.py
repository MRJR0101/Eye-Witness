from eye_witness import init, metric_counter, shutdown


def test_metrics_perf_smoke():
    init(
        otel_exporter="none",
        metrics_enabled=True,
        metrics_exporter="none",
        flush_on_exit=False,
        force=True,
    )
    c = metric_counter("perf.counter")
    for _ in range(100):
        c.add(1)
    shutdown()
