"""
Path 3 — OpenTelemetry Log Correlation

Structlog processor that injects trace_id / span_id into every log event.
This is the bridge between Path 1 (structlog) and Path 3 (OpenTelemetry).
"""

from __future__ import annotations
from typing import Any

from opentelemetry import trace


def add_trace_context(
    logger: Any, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """
    Structlog processor: inject trace_id and span_id into log events.

    Place at slot #2 in the processor pipeline (after merge_contextvars).

    Example output:
        {"event": "job.started", "trace_id": "0af765...", "span_id": "b7ad6b..."}
    """
    span = trace.get_current_span()
    ctx = span.get_span_context()

    if ctx and ctx.is_valid:
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")

    return event_dict
