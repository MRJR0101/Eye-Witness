from eye_witness.v1 import get_logger, init, shutdown


def test_v1_import_contract_smoke():
    init(otel_exporter="none", metrics_enabled=False, flush_on_exit=False, force=True)
    get_logger("contract").info("contract.namespace.ok")
    shutdown()
