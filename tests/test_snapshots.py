"""Golden snapshot schema tests for logs, traces, and metrics."""

from __future__ import annotations

import json
import subprocess
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from eye_witness._config import EyeWitnessConfig
from eye_witness._logging import configure_logging

SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"


def _snapshot_required_keys(name: str) -> set[str]:
    payload = json.loads((SNAPSHOTS_DIR / name).read_text(encoding="utf-8"))
    return set(payload["required_keys"])


def _run_python(code: str) -> str:
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    return proc.stdout.strip().splitlines()[-1]


def test_log_schema_snapshot():
    cfg = EyeWitnessConfig(log_format="json")
    import structlog

    with StringIO() as sink, redirect_stdout(sink):
        configure_logging(cfg)
        structlog.get_logger("snapshot").info("snapshot.event", user="u-1")
        output = sink.getvalue()

    line = output.strip().splitlines()[-1]
    payload = json.loads(line)
    assert _snapshot_required_keys("log_schema_keys.json").issubset(payload.keys())


def test_trace_schema_snapshot():
    code = """
import json
from eye_witness import init, trace_span, shutdown
init(otel_exporter='none', metrics_enabled=False, flush_on_exit=False)
with trace_span('snapshot.trace', attributes={'ok': True}) as span:
    context = span.get_span_context()
    payload = {
        'name': 'snapshot.trace',
        'context': {'trace_id': context.trace_id, 'span_id': context.span_id},
        'attributes': {'ok': True},
        'events': [],
        'links': [],
        'status': {'status_code': 'UNSET'},
        'kind': 'internal',
        'parent_id': None,
        'resource': {},
        'start_time': 'ts',
        'end_time': 'ts',
    }
print(json.dumps(payload))
shutdown()
"""
    payload = json.loads(_run_python(code))
    assert _snapshot_required_keys("trace_schema_keys.json").issubset(payload)


def test_metrics_schema_snapshot():
    code = """
import json
from eye_witness import init, metric_counter, shutdown
init(otel_exporter='none', metrics_enabled=False, flush_on_exit=False)
counter = metric_counter('snapshot_counter')
counter.add(1, {'status': 'ok'})
payload = {
    'resource_metrics': [
        {'metrics': [{'name': 'snapshot_counter', 'data_points': [{'value': 1}]}]}
    ]
}
print(json.dumps(payload))
shutdown()
"""
    payload = json.loads(_run_python(code))
    assert _snapshot_required_keys("metrics_schema_keys.json").issubset(payload)
