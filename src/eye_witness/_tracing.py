"""
Eye-Witness OpenTelemetry tracing setup.

Sets up:
  - TracerProvider with Resource attributes (service.name, version, environment)
  - Span exporter (console for dev, OTLP HTTP/gRPC for production)
  - BatchSpanProcessor for production, SimpleSpanProcessor for dev
  - Sampling control
  - atexit shutdown for CLI apps
  - Convenience wrappers: get_tracer(), trace_span()
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.sampling import (
    ALWAYS_OFF,
    ALWAYS_ON,
    Sampler,
    SamplingResult,
    TraceIdRatioBased,
)
from opentelemetry.trace import Status, StatusCode

if TYPE_CHECKING:
    from eye_witness._config import EyeWitnessConfig


def configure_tracing(cfg: EyeWitnessConfig) -> TracerProvider | None:
    """
    Create and register a TracerProvider based on Eye-Witness config.

    Returns the provider (or None if tracing is disabled).
    """
    if not cfg.otel_enabled:
        return None

    # ── Resource (identifies this service) ──────────────────────────
    resource = Resource.create(
        attributes={
            "service.name": cfg.service_name,
            "service.version": cfg.service_version,
            "deployment.environment": cfg.environment,
        }
    )

    # ── Sampler ─────────────────────────────────────────────────────
    sampler = _build_sampler(
        cfg.otel_sample_rate,
        span_name_rates=cfg.otel_span_name_sample_rates,
    )

    # ── Provider ────────────────────────────────────────────────────
    provider = TracerProvider(resource=resource, sampler=sampler)
    trace.set_tracer_provider(provider)

    # ── Exporter + Processor ────────────────────────────────────────
    exporter = _build_exporter(cfg)
    processor = _build_processor(cfg, exporter)
    if processor is not None:
        provider.add_span_processor(processor)

    return provider


def _build_sampler(rate: float, *, span_name_rates: dict[str, float] | None = None) -> Sampler:
    """Pick a sampler based on the configured rate."""
    if span_name_rates:
        return SpanNameRateSampler(rate, span_name_rates)
    if rate >= 1.0:
        return ALWAYS_ON
    if rate <= 0.0:
        return ALWAYS_OFF
    return TraceIdRatioBased(rate)


class SpanNameRateSampler(Sampler):
    """Sampler that applies rate overrides by span-name prefix."""

    def __init__(self, default_rate: float, span_name_rates: dict[str, float]):
        self._default_sampler = _build_sampler(default_rate)
        self._prefix_samplers = sorted(
            ((prefix, _build_sampler(rate)) for prefix, rate in span_name_rates.items()),
            key=lambda item: len(item[0]),
            reverse=True,
        )

    def should_sample(
        self,
        parent_context: Any,
        trace_id: Any,
        name: Any,
        kind: Any = None,
        attributes: Any = None,
        links: Any = None,
        trace_state: Any = None,
    ) -> SamplingResult:
        for prefix, sampler in self._prefix_samplers:
            if name.startswith(prefix):
                return sampler.should_sample(
                    parent_context,
                    trace_id,
                    name,
                    kind=kind,
                    attributes=attributes,
                    links=links,
                    trace_state=trace_state,
                )
        return self._default_sampler.should_sample(
            parent_context,
            trace_id,
            name,
            kind=kind,
            attributes=attributes,
            links=links,
            trace_state=trace_state,
        )

    def get_description(self) -> str:
        return (
            f"SpanNameRateSampler(default={self._default_sampler.get_description()},"
            f" rules={len(self._prefix_samplers)})"
        )


def _build_exporter(cfg: EyeWitnessConfig) -> Any:
    """Instantiate the right span exporter based on config."""
    kind = cfg.otel_exporter.lower()

    if kind == "none":
        return None

    if kind == "console":
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter

        return ConsoleSpanExporter()

    if kind == "otlp-http":
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )

        kwargs: dict[str, Any] = {}
        if cfg.otel_endpoint:
            kwargs["endpoint"] = cfg.otel_endpoint
        return OTLPSpanExporter(**kwargs)

    if kind == "otlp-grpc":
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter as GrpcExporter,
        )

        kwargs = {}
        if cfg.otel_endpoint:
            kwargs["endpoint"] = cfg.otel_endpoint
        kwargs["insecure"] = cfg.otel_insecure
        return GrpcExporter(**kwargs)

    raise ValueError(f"Unknown otel_exporter: {cfg.otel_exporter!r}")


def _build_processor(cfg: EyeWitnessConfig, exporter: Any) -> Any:
    """Pick BatchSpanProcessor (prod) or SimpleSpanProcessor (dev)."""
    if exporter is None:
        # No exporter configured: keep tracing context active, but export nothing.
        return None

    if cfg.otel_exporter.lower() == "console":
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor

        return SimpleSpanProcessor(exporter)

    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    return BatchSpanProcessor(exporter)


# ── Public helpers ──────────────────────────────────────────────────


def get_tracer(name: str | None = None) -> trace.Tracer:
    """
    Get an OpenTelemetry Tracer.

    Usage:
        tracer = get_tracer("myapp.orders")
        with tracer.start_as_current_span("process_order"):
            ...
    """
    return trace.get_tracer(name or __name__)


@contextmanager
def trace_span(
    name: str,
    *,
    attributes: dict[str, Any] | None = None,
    record_exception: bool = True,
    set_status_on_exception: bool = True,
) -> Generator[trace.Span, None, None]:
    """
    Convenience context manager for creating a traced span.

    Automatically:
      - Sets attributes if provided
      - Records exceptions and sets ERROR status on failure
      - Nests under the current active span

    Usage:
        with trace_span("validate_input", attributes={"input_size": 42}) as span:
            result = validate(data)
            span.set_attribute("valid", True)
    """
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span(name) as span:
        if attributes:
            for k, v in attributes.items():
                span.set_attribute(k, v)
        try:
            yield span
        except Exception as exc:
            if record_exception:
                span.record_exception(exc)
            if set_status_on_exception:
                span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise
