"""
New Relic OTLP Integration — Pure OTel → New Relic (recommended path).

From the New Relic guide:
  - Use OTel Python SDK and auto-instrumentation
  - Export traces/metrics/logs with OTLP to https://otlp.nr-data.net
  - New Relic ingests OTLP natively, maps OTel semantic conventions
  - api-key header required on every OTLP request
  - TLS 1.2 required (HTTPS handles this)
  - Prefer OTLP/HTTP binary protobuf over gRPC

Two usage modes:
  1. Env-var-only (opentelemetry-instrument wrapper) — no code needed
  2. Explicit Python setup (this module) — full code control
"""

import os
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


# ── New Relic OTLP Endpoints ────────────────────────────────────────────────

NR_OTLP_ENDPOINT_US = "https://otlp.nr-data.net"
NR_OTLP_ENDPOINT_EU = "https://otlp.eu01.nr-data.net"

# Trace-specific path (appended to endpoint for HTTP/protobuf)
NR_TRACES_PATH = "/v1/traces"


def setup_newrelic_otlp_provider(
    *,
    service_name: str = "",
    service_version: str = "0.1.0",
    environment: str = "",
    license_key: str = "",
    endpoint: str = "",
    extra_resource_attrs: dict[str, Any] | None = None,
) -> TracerProvider:
    """
    Configure TracerProvider to export via OTLP HTTP to New Relic.

    Reads from environment if args are empty:
      - NEW_RELIC_LICENSE_KEY or license_key
      - OTEL_SERVICE_NAME or service_name
      - OTEL_EXPORTER_OTLP_ENDPOINT or endpoint
      - SENTRY_ENVIRONMENT / deployment.environment or environment

    Returns the configured TracerProvider (also registered globally).

    Example:
        provider = setup_newrelic_otlp_provider(
            service_name="my-app",
            license_key="NRJS-...",
        )
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("hello"):
            ...
        provider.shutdown()
    """
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    # Resolve configuration from args or environment
    _license_key = license_key or os.getenv("NEW_RELIC_LICENSE_KEY", "")
    _service_name = service_name or os.getenv("OTEL_SERVICE_NAME", "eye-witness")
    _environment = environment or os.getenv("SENTRY_ENVIRONMENT", os.getenv("OTEL_ENVIRONMENT", "development"))
    _endpoint = endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", NR_OTLP_ENDPOINT_US)

    if not _license_key:
        import warnings
        warnings.warn(
            "NEW_RELIC_LICENSE_KEY not set — traces will export but New Relic "
            "will reject them. Set the env var or pass license_key=.",
            stacklevel=2,
        )

    # Resource identifies the service (OTel semantic conventions)
    resource_attrs: dict[str, Any] = {
        "service.name": _service_name,
        "service.version": service_version,
        "deployment.environment": _environment,
    }
    if extra_resource_attrs:
        resource_attrs.update(extra_resource_attrs)

    resource = Resource.create(resource_attrs)

    # Create and register provider
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # OTLP HTTP exporter pointed at New Relic
    # New Relic requires: api-key header, HTTPS (TLS 1.2), http/protobuf
    otlp_exporter = OTLPSpanExporter(
        endpoint=f"{_endpoint.rstrip('/')}{NR_TRACES_PATH}",
        headers={"api-key": _license_key},
    )

    # BatchSpanProcessor for production (async, batched export)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    return provider


def setup_newrelic_with_console_fallback(
    *,
    service_name: str = "",
    service_version: str = "0.1.0",
    environment: str = "",
    license_key: str = "",
) -> TracerProvider:
    """
    New Relic OTLP + ConsoleSpanExporter for development visibility.

    Sends spans to both New Relic AND stdout so you can see them locally
    while also verifying they arrive in NR.
    """
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

    _license_key = license_key or os.getenv("NEW_RELIC_LICENSE_KEY", "")
    _service_name = service_name or os.getenv("OTEL_SERVICE_NAME", "eye-witness")
    _environment = environment or os.getenv("SENTRY_ENVIRONMENT", "development")
    _endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", NR_OTLP_ENDPOINT_US)

    resource = Resource.create({
        "service.name": _service_name,
        "service.version": service_version,
        "deployment.environment": _environment,
    })

    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Console for local visibility
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    # OTLP to New Relic (if key is present)
    if _license_key:
        otlp_exporter = OTLPSpanExporter(
            endpoint=f"{_endpoint.rstrip('/')}{NR_TRACES_PATH}",
            headers={"api-key": _license_key},
        )
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    return provider
