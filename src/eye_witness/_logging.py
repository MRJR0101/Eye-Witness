"""
Eye-Witness structured logging via structlog.

Sets up:
  - JSON output for production (containers / non-TTY)
  - Pretty console output for development (TTY detected)
  - Context variable merging for request/job context
  - OpenTelemetry trace_id / span_id injection
  - stdlib logging bridge so third-party library logs flow through structlog
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from eye_witness._config import EyeWitnessConfig


def _add_otel_trace_context(logger, method_name, event_dict):
    """
    Structlog processor: inject trace_id and span_id from the active
    OpenTelemetry span into every log event.

    This is the single highest-value OTel integration — it lets you
    click a trace_id in your log viewer and jump straight to the
    distributed trace.
    """
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        ctx = span.get_span_context()

        if ctx and ctx.is_valid:
            event_dict["trace_id"] = format(ctx.trace_id, "032x")
            event_dict["span_id"] = format(ctx.span_id, "016x")
    except Exception:
        # OTel not installed or not configured — skip silently
        pass

    return event_dict


def _add_service_info(service_name: str, service_version: str, environment: str):
    """Return a structlog processor that stamps service metadata on every event."""

    def processor(logger, method_name, event_dict):
        event_dict["service"] = service_name
        event_dict["version"] = service_version
        event_dict["env"] = environment
        return event_dict

    return processor


def _redact_sensitive_fields(redact_keys: tuple[str, ...], replacement: str):
    """Return a processor that redacts sensitive fields in log payloads."""
    redact_set = {key.lower() for key in redact_keys}

    def _redact(value):
        if isinstance(value, dict):
            redacted = {}
            for k, v in value.items():
                if str(k).lower() in redact_set:
                    redacted[k] = replacement
                else:
                    redacted[k] = _redact(v)
            return redacted
        if isinstance(value, list):
            return [_redact(item) for item in value]
        if isinstance(value, tuple):
            return tuple(_redact(item) for item in value)
        return value

    def processor(logger, method_name, event_dict):
        return _redact(event_dict)

    return processor


def configure_logging(cfg: EyeWitnessConfig) -> None:
    """Wire up structlog with processors determined by the config."""

    log_level = getattr(logging, cfg.log_level.upper(), logging.INFO)

    # ── Shared processors (independent of output format) ────────────
    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        _add_otel_trace_context,
        _add_service_info(cfg.service_name, cfg.service_version, cfg.environment),
        _redact_sensitive_fields(cfg.log_redact_keys, cfg.log_redact_value),
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if cfg.log_add_callsite:
        shared_processors.append(
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                }
            )
        )

    # ── Output format ───────────────────────────────────────────────
    use_json = _should_use_json(cfg.log_format)

    if use_json:
        renderer = _build_json_renderer(cfg)
        shared_processors.append(structlog.processors.dict_tracebacks)
        shared_processors.append(renderer)
    else:
        shared_processors.append(structlog.dev.ConsoleRenderer())

    # ── Configure structlog ─────────────────────────────────────────
    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=_build_logger_factory(cfg, use_json),
        cache_logger_on_first_use=True,
    )

    # ── Bridge stdlib logging → structlog ───────────────────────────
    _configure_stdlib_bridge(cfg, log_level, use_json)


def _should_use_json(log_format: str) -> bool:
    """Determine whether to emit JSON based on config or TTY detection."""
    if log_format == "json":
        return True
    if log_format == "console":
        return False
    # "auto" — detect TTY
    return not sys.stderr.isatty()


def _build_json_renderer(cfg: EyeWitnessConfig):
    """Return a JSONRenderer, optionally using orjson for speed."""
    if cfg.log_use_orjson:
        try:
            import orjson

            return structlog.processors.JSONRenderer(serializer=orjson.dumps)
        except ImportError:
            pass  # fall back to stdlib json
    return structlog.processors.JSONRenderer()


def _build_logger_factory(cfg: EyeWitnessConfig, use_json: bool):
    """Pick a logger factory matching the serializer output type."""
    if use_json and cfg.log_use_orjson:
        try:
            import orjson  # noqa: F401

            return structlog.BytesLoggerFactory()
        except ImportError:
            pass
    return structlog.WriteLoggerFactory()


def _configure_stdlib_bridge(cfg: EyeWitnessConfig, log_level: int, use_json: bool) -> None:
    """
    Set up a ProcessorFormatter so that logs from third-party libraries
    (uvicorn, requests, sqlalchemy, etc.) flow through structlog too.
    """
    foreign_pre_chain = [
        structlog.contextvars.merge_contextvars,
        _add_otel_trace_context,
        _add_service_info(cfg.service_name, cfg.service_version, cfg.environment),
        _redact_sensitive_fields(cfg.log_redact_keys, cfg.log_redact_value),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if use_json:
        final_processor = _build_json_renderer(cfg)
    else:
        final_processor = structlog.dev.ConsoleRenderer()

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=final_processor,
        foreign_pre_chain=foreign_pre_chain,
    )

    # Apply to root logger
    root = logging.getLogger()
    root.setLevel(log_level)

    # Optionally clear existing handlers to avoid duplicate output.
    if cfg.log_clear_root_handlers:
        root.handlers.clear()

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    root.addHandler(handler)


def get_logger(name: str | None = None, **initial_context) -> structlog.BoundLogger:
    """
    Get a structlog logger, optionally with initial bound context.

    Usage:
        log = get_logger()
        log = get_logger("myapp.orders", customer_id="cust-42")
    """
    logger = structlog.get_logger(name)
    if initial_context:
        logger = logger.bind(**initial_context)
    return logger
