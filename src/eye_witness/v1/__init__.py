"""
Eye-Witness v1 stable API namespace.

This module mirrors the public top-level API so users can pin imports to
`eye_witness.v1` for clearer compatibility intent.
"""

from eye_witness import (
    EyeWitnessConfig,
    EyeWitnessDjangoMiddleware,
    add_breadcrumb,
    bind_context,
    capture_exception,
    capture_message,
    clear_context,
    get_logger,
    get_meter,
    get_tracer,
    init,
    install_celery,
    install_fastapi,
    install_flask,
    metric_counter,
    metric_histogram,
    set_context,
    set_tag,
    set_user,
    shutdown,
    trace_span,
)

__all__ = [
    "init",
    "shutdown",
    "EyeWitnessConfig",
    "get_logger",
    "get_meter",
    "metric_counter",
    "metric_histogram",
    "get_tracer",
    "trace_span",
    "capture_exception",
    "capture_message",
    "add_breadcrumb",
    "set_tag",
    "set_context",
    "set_user",
    "bind_context",
    "clear_context",
    "install_fastapi",
    "install_flask",
    "install_celery",
    "EyeWitnessDjangoMiddleware",
]
