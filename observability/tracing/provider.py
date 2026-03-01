"""
TracerProvider Setup — All patterns from Path 3 reference.

Sections:
  - Resource definition (service.name, service.version, deployment.environment)
  - ConsoleSpanExporter (local development)
  - OTLP HTTP exporter (production, port 4318)
  - OTLP gRPC exporter (high-volume, port 4317)
  - BatchSpanProcessor vs SimpleSpanProcessor
  - Shutdown provider on exit
"""

import atexit

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)


def _create_resource(
    service_name: str = "my-service",
    service_version: str = "1.0.0",
    environment: str = "production",
) -> Resource:
    """Create a Resource with OpenTelemetry semantic conventions."""
    return Resource(attributes={
        "service.name": service_name,
        "service.version": service_version,
        "deployment.environment": environment,
    })


def setup_console_provider(
    *,
    service_name: str = "my-service",
    service_version: str = "1.0.0",
    environment: str = "development",
) -> TracerProvider:
    """
    ConsoleSpanExporter for local development / debugging.

    Uses SimpleSpanProcessor (exports immediately, synchronously).
    """
    resource = _create_resource(service_name, service_version, environment)
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    provider.add_span_processor(
        SimpleSpanProcessor(ConsoleSpanExporter())
    )

    return provider


def setup_otlp_http_provider(
    *,
    service_name: str = "my-service",
    service_version: str = "1.0.0",
    environment: str = "production",
    endpoint: str = "",  # Empty = reads OTEL_EXPORTER_OTLP_ENDPOINT env var
) -> TracerProvider:
    """
    OTLP HTTP exporter (port 4318) with BatchSpanProcessor.

    Default endpoint: http://localhost:4318/v1/traces
    Reads OTEL_EXPORTER_OTLP_ENDPOINT from environment if endpoint is empty.
    """
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    resource = _create_resource(service_name, service_version, environment)
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    exporter_kwargs = {}
    if endpoint:
        exporter_kwargs["endpoint"] = endpoint

    otlp_exporter = OTLPSpanExporter(**exporter_kwargs)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    return provider


def setup_otlp_grpc_provider(
    *,
    service_name: str = "my-service",
    service_version: str = "1.0.0",
    environment: str = "production",
    endpoint: str = "http://localhost:4317",
    insecure: bool = True,
) -> TracerProvider:
    """
    OTLP gRPC exporter (port 4317) with BatchSpanProcessor.

    Lower overhead than HTTP — better for high-volume tracing.
    """
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

    resource = _create_resource(service_name, service_version, environment)
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    otlp_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=insecure)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    return provider


def get_tracer(name: str = __name__) -> trace.Tracer:
    """Get a tracer named by module — per the reference best practice."""
    return trace.get_tracer(name)


def shutdown_provider() -> None:
    """
    Shutdown the tracer provider — flushes all buffered spans.

    Call at end of main() or register with atexit for CLI apps.
    """
    provider = trace.get_tracer_provider()
    if hasattr(provider, "shutdown"):
        provider.shutdown()


def register_shutdown_on_exit() -> None:
    """Register provider shutdown as an atexit handler (CLI pattern)."""
    atexit.register(shutdown_provider)
