from concurrent.futures import ThreadPoolExecutor

from eye_witness import init, shutdown


def test_concurrent_force_reinit_smoke():
    def work(i: int):
        init(
            service_name=f"svc-{i}",
            force=True,
            otel_exporter="none",
            metrics_enabled=False,
            flush_on_exit=False,
        )
        shutdown()

    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(work, range(24)))
