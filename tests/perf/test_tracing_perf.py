from eye_witness import init, shutdown, trace_span


def test_tracing_perf_smoke():
    init(otel_exporter="none", metrics_enabled=False, flush_on_exit=False, force=True)
    for _ in range(100):
        with trace_span("perf.trace"):
            pass
    shutdown()
