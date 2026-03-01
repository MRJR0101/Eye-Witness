"""
Eye-Witness initialization — the single entry point that wires up
structlog, Sentry, and OpenTelemetry in one call.
"""

from __future__ import annotations

import atexit
import threading
from typing import Any

from opentelemetry import metrics, trace

from eye_witness._config import EyeWitnessConfig
from eye_witness._logging import configure_logging
from eye_witness._metrics import configure_metrics
from eye_witness._sentry import configure_sentry
from eye_witness._tracing import configure_tracing

# Module-level state
_initialized: bool = False
_config: EyeWitnessConfig | None = None
_atexit_registered: bool = False
_state_lock = threading.RLock()


def init(
    *,
    config: EyeWitnessConfig | None = None,
    force: bool = False,
    **kwargs: Any,
) -> EyeWitnessConfig:
    """
    Initialize the entire Eye-Witness observability stack.

    You can either pass a pre-built EyeWitnessConfig, or pass keyword
    arguments that get forwarded to EyeWitnessConfig (with env-var
    fallbacks via from_env).

    Usage — keyword style (simplest):
        from eye_witness import init

        init(
            service_name="my-app",
            service_version="1.0.0",
            environment="production",
            sentry_dsn=os.getenv("SENTRY_DSN", ""),
            otel_exporter="otlp-http",
        )

    Usage — config object (full control):
        from eye_witness import init, EyeWitnessConfig

        cfg = EyeWitnessConfig(
            service_name="my-app",
            log_format="json",
            otel_exporter="otlp-grpc",
            otel_endpoint="http://collector:4317",
        )
        init(config=cfg)

    Usage — env vars only:
        # Set EW_SERVICE_NAME, EW_SENTRY_DSN, etc. in your environment
        init()
    """
    global _initialized, _config, _atexit_registered

    with _state_lock:
        if _initialized:
            import structlog

            log = structlog.get_logger()
            if not force:
                log.warning(
                    "eye_witness.already_initialized",
                    hint="init() called more than once — ignoring",
                )
                if _config is None:
                    raise RuntimeError("Eye-Witness init state is inconsistent")
                return _config

            log.info("eye_witness.reinitializing", hint="force=True")
            shutdown()

        # Build config
        if config is not None:
            cfg = config
        else:
            cfg = EyeWitnessConfig.from_env(**kwargs)

        # 1. Logging first (everything else may want to log)
        configure_logging(cfg)

        # 2. Sentry (error tracking + breadcrumbs)
        configure_sentry(cfg)

        # 3. OpenTelemetry tracing
        configure_tracing(cfg)

        # 4. OpenTelemetry metrics
        configure_metrics(cfg)

        _initialized = True
        _config = cfg

        if cfg.flush_on_exit and not _atexit_registered:
            atexit.register(shutdown)
            _atexit_registered = True

        # Emit a startup log line so you can verify the stack is wired up
        import structlog

        log = structlog.get_logger("eye_witness")
        log.info(
            "eye_witness.initialized",
            service=cfg.service_name,
            version=cfg.service_version,
            env=cfg.environment,
            log_format=cfg.log_format,
            otel_exporter=cfg.otel_exporter,
            metrics_exporter=cfg.metrics_exporter,
            sentry_enabled=bool(cfg.sentry_dsn),
        )

        return cfg


def shutdown() -> None:
    """
    Gracefully shut down all observability subsystems.

    Flushes pending Sentry events and shuts down the OTel TracerProvider.
    Call this at the end of your CLI main() or in an atexit handler.
    """
    global _initialized, _config, _atexit_registered

    with _state_lock:
        if not _initialized:
            return

        import sentry_sdk

        sentry_sdk.flush(timeout=2)

        provider = trace.get_tracer_provider()
        if hasattr(provider, "shutdown"):
            try:
                provider.shutdown()
            except Exception:
                pass

        meter_provider = metrics.get_meter_provider()
        if hasattr(meter_provider, "shutdown"):
            try:
                meter_provider.shutdown()
            except Exception:
                pass

        _initialized = False
        _config = None
        if _atexit_registered:
            try:
                atexit.unregister(shutdown)
            except Exception:
                pass
            _atexit_registered = False
