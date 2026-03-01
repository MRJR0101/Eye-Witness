"""
Path 3 — OpenTelemetry Context Propagation

Inject/extract trace context across service boundaries.
"""

from __future__ import annotations
from typing import Any

from opentelemetry import trace
from opentelemetry.trace import NonRecordingSpan, SpanContext, TraceFlags
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

_propagator = TraceContextTextMapPropagator()


def inject_context(carrier: dict[str, str] | None = None) -> dict[str, str]:
    """Inject current trace context into carrier dict."""
    if carrier is None:
        carrier = {}
    _propagator.inject(carrier)
    return carrier


def extract_context(carrier: dict[str, str]) -> Any:
    """Extract trace context from carrier (e.g. HTTP headers)."""
    return _propagator.extract(carrier=carrier)


def create_span_context(
    trace_id: int, span_id: int, is_remote: bool = True, trace_flags: int = 0x01,
) -> Any:
    """Manually construct a SpanContext for external trace/span IDs."""
    span_context = SpanContext(
        trace_id=trace_id, span_id=span_id,
        is_remote=is_remote, trace_flags=TraceFlags(trace_flags),
    )
    return trace.set_span_in_context(NonRecordingSpan(span_context))


def propagation_round_trip_example() -> None:
    """Full inject -> extract round-trip demo."""
    tracer = trace.get_tracer("example.propagation")

    with tracer.start_as_current_span("service-a-outgoing"):
        carrier = inject_context()
        print(f"  Service A injected: {carrier}")

    ctx = extract_context(carrier)
    with tracer.start_as_current_span("service-b-incoming", context=ctx):
        print("  Service B: child of Service A trace")
