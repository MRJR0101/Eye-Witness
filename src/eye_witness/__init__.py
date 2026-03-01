"""
Eye-Witness — Unified observability for Python.

Integrates structlog (structured logging), Sentry (error tracking),
and OpenTelemetry (distributed tracing) into a single cohesive setup.

Usage:
    from eye_witness import init, get_logger

    init(
        service_name="my-app",
        service_version="1.0.0",
        environment="production",
        sentry_dsn="https://...",
    )

    log = get_logger()
    log.info("app.started", port=8080)
"""

from eye_witness._compat import get_structured_logger, init_observability
from eye_witness._config import EyeWitnessConfig
from eye_witness._context import bind_context, clear_context
from eye_witness._init import init, shutdown
from eye_witness._logging import get_logger
from eye_witness._metrics import get_meter, metric_counter, metric_histogram
from eye_witness._sentry import (
    add_breadcrumb,
    capture_exception,
    capture_message,
    set_context,
    set_tag,
    set_user,
)
from eye_witness._tracing import get_tracer, trace_span
from eye_witness.integrations import (
    EyeWitnessDjangoMiddleware,
    install_celery,
    install_fastapi,
    install_flask,
)

__all__ = [
    # Setup
    "init",
    "init_observability",
    "shutdown",
    "EyeWitnessConfig",
    # Logging
    "get_logger",
    "get_structured_logger",
    "get_meter",
    "metric_counter",
    "metric_histogram",
    # Tracing
    "get_tracer",
    "trace_span",
    # Sentry
    "capture_exception",
    "capture_message",
    "add_breadcrumb",
    "set_tag",
    "set_context",
    "set_user",
    # Context
    "bind_context",
    "clear_context",
    # Integrations
    "install_fastapi",
    "install_flask",
    "install_celery",
    "EyeWitnessDjangoMiddleware",
]

__version__ = "0.1.0"
