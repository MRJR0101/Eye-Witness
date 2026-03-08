"""
Eye-Witness configuration dataclass.

All settings flow through EyeWitnessConfig so there's one place to
understand what's tunable and what the defaults are.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class EyeWitnessConfig:
    """Immutable configuration for the Eye-Witness observability stack."""

    # ── Identity ────────────────────────────────────────────────────────
    service_name: str = "unknown-service"
    service_version: str = "0.0.0"
    environment: str = "local"

    # ── Logging ─────────────────────────────────────────────────────────
    log_level: str = "INFO"
    log_format: Literal["auto", "json", "console"] = "auto"
    log_add_callsite: bool = True
    log_use_orjson: bool = False  # set True + install orjson for speed
    log_clear_root_handlers: bool = True  # disable if host app manages handlers
    log_redact_keys: tuple[str, ...] = (
        "password",
        "passwd",
        "secret",
        "token",
        "api_key",
        "authorization",
    )
    log_redact_value: str = "[REDACTED]"

    # ── Sentry / GlitchTip ──────────────────────────────────────────────
    sentry_dsn: str = ""  # empty → SDK is no-op (safe everywhere)
    sentry_traces_sample_rate: float = 0.0
    sentry_max_breadcrumbs: int = 100
    sentry_attach_stacktrace: bool = True
    sentry_send_default_pii: bool = False
    sentry_server_name: str | None = None

    # ── OpenTelemetry ───────────────────────────────────────────────────
    otel_enabled: bool = True
    otel_exporter: Literal["console", "otlp-http", "otlp-grpc", "none"] = "console"
    otel_endpoint: str = ""  # empty → use OTEL_EXPORTER_OTLP_ENDPOINT env or defaults
    otel_insecure: bool = True  # for local dev; set False in prod with TLS

    # ── Sampling ────────────────────────────────────────────────────────
    otel_sample_rate: float = 1.0  # 1.0 = always, 0.001 = 1-in-1000
    otel_span_name_sample_rates: dict[str, float] = field(default_factory=dict)

    # ── Metrics ─────────────────────────────────────────────────────────
    metrics_enabled: bool = True
    metrics_exporter: Literal["none", "console", "otlp-http"] = "none"
    metrics_endpoint: str = ""
    metrics_export_interval_millis: int = 60000

    # ── CLI helpers ─────────────────────────────────────────────────────
    flush_on_exit: bool = True  # register atexit handlers for CLI apps

    def __post_init__(self) -> None:
        valid_log_formats = {"auto", "json", "console"}
        if self.log_format not in valid_log_formats:
            expected_formats = sorted(valid_log_formats)
            raise ValueError(
                f"Invalid log_format {self.log_format!r}; expected one of {expected_formats}"
            )

        valid_exporters = {"console", "otlp-http", "otlp-grpc", "none"}
        if self.otel_exporter.lower() not in valid_exporters:
            expected_exporters = sorted(valid_exporters)
            raise ValueError(
                f"Invalid otel_exporter {self.otel_exporter!r}; "
                f"expected one of {expected_exporters}"
            )

        if not 0.0 <= self.otel_sample_rate <= 1.0:
            raise ValueError("otel_sample_rate must be between 0.0 and 1.0")

        if not 0.0 <= self.sentry_traces_sample_rate <= 1.0:
            raise ValueError("sentry_traces_sample_rate must be between 0.0 and 1.0")

        if self.metrics_exporter.lower() not in {"none", "console", "otlp-http"}:
            raise ValueError(
                "metrics_exporter must be one of 'none', 'console', or 'otlp-http'"
            )

        if self.metrics_export_interval_millis <= 0:
            raise ValueError("metrics_export_interval_millis must be > 0")

        for span_name, rate in self.otel_span_name_sample_rates.items():
            if not span_name:
                raise ValueError("otel_span_name_sample_rates keys must be non-empty")
            if not 0.0 <= rate <= 1.0:
                raise ValueError(
                    "otel_span_name_sample_rates values must be between 0.0 and 1.0"
                )

    @classmethod
    def from_env(cls, **overrides: Any) -> EyeWitnessConfig:
        """
        Build config from environment variables, with keyword overrides
        taking precedence.

        Env vars follow the pattern EW_<FIELD_NAME> in uppercase.
        Examples:
            EW_SERVICE_NAME=my-app
            EW_LOG_LEVEL=DEBUG
            EW_SENTRY_DSN=https://...
            EW_OTEL_EXPORTER=otlp-http
        """
        env_map: dict = {}
        prefix = "EW_"

        for f in cls.__dataclass_fields__:
            env_key = f"{prefix}{f.upper()}"
            env_val = os.environ.get(env_key)
            if env_val is not None:
                field_obj = cls.__dataclass_fields__[f]
                env_map[f] = _coerce(env_val, field_obj.type)

        # Overrides beat env vars
        env_map.update(overrides)
        return cls(**env_map)


def _coerce(raw: str, type_hint: Any) -> object:
    """Best-effort coercion of env-var strings to Python types."""
    hint = str(type_hint).lower()
    if hint == "bool":
        return raw.strip().lower() in ("1", "true", "yes")
    if hint == "int":
        return int(raw)
    if hint == "float":
        return float(raw)
    if "tuple" in hint:
        return tuple(part.strip() for part in raw.split(",") if part.strip())
    if "dict" in hint:
        return json.loads(raw)
    return raw
