"""
Custom structlog processors.

Contains the trace context processor that bridges Path 1 (structlog)
with Path 3 (OpenTelemetry) — injecting trace_id and span_id into
every log event.
"""

from typing import Any


def add_trace_context(
    logger: Any, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """
    Structlog processor: inject trace_id and span_id into log events.

    Requires opentelemetry-api to be installed. If OTel is not available
    or no span is active, the event dict is returned unchanged.

    Add this to the processor chain at position 2 (after merge_contextvars,
    before add_logger_name) per the recommended pipeline order.
    """
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        ctx = span.get_span_context()

        if ctx and ctx.is_valid:
            event_dict["trace_id"] = format(ctx.trace_id, "032x")
            event_dict["span_id"] = format(ctx.span_id, "016x")
    except ImportError:
        pass  # OTel not installed — skip silently

    return event_dict
