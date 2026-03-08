"""
Eye-Witness OpenTelemetry metrics setup.

Provides optional metrics pipeline wiring and convenience helpers for
creating counters and histograms.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource

if TYPE_CHECKING:
    from eye_witness._config import EyeWitnessConfig


def configure_metrics(cfg: EyeWitnessConfig) -> MeterProvider | None:
    """Create and register a MeterProvider based on config."""
    if not cfg.metrics_enabled:
        return None

    resource = Resource.create(
        attributes={
            "service.name": cfg.service_name,
            "service.version": cfg.service_version,
            "deployment.environment": cfg.environment,
        }
    )

    readers = _build_metric_readers(cfg)
    provider = MeterProvider(resource=resource, metric_readers=readers)
    metrics.set_meter_provider(provider)

    return provider


def _build_metric_readers(cfg: EyeWitnessConfig) -> list[Any]:
    exporter_kind = cfg.metrics_exporter.lower()
    if exporter_kind == "none":
        return []

    from opentelemetry.sdk.metrics.export import (
        ConsoleMetricExporter,
        MetricExporter,
        PeriodicExportingMetricReader,
    )
    exporter: MetricExporter

    if exporter_kind == "console":
        exporter = ConsoleMetricExporter()
    elif exporter_kind == "otlp-http":
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
            OTLPMetricExporter,
        )

        if cfg.metrics_endpoint:
            exporter = OTLPMetricExporter(endpoint=cfg.metrics_endpoint)
        else:
            exporter = OTLPMetricExporter()
    else:
        raise ValueError(f"Unknown metrics_exporter: {cfg.metrics_exporter!r}")

    reader = PeriodicExportingMetricReader(
        exporter,
        export_interval_millis=cfg.metrics_export_interval_millis,
    )
    return [reader]


def get_meter(name: str | None = None) -> Any:
    """Get a meter from the global meter provider."""
    return metrics.get_meter(name or __name__)


def metric_counter(name: str, *, description: str = "", unit: str = "1") -> Any:
    """Create and return a counter instrument."""
    return get_meter(__name__).create_counter(name, description=description, unit=unit)


def metric_histogram(name: str, *, description: str = "", unit: str = "1") -> Any:
    """Create and return a histogram instrument."""
    return get_meter(__name__).create_histogram(name, description=description, unit=unit)
