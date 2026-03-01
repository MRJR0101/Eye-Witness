"""
Eye-Witness Sentry / GlitchTip integration.

Sets up:
  - Optional DSN (no-DSN = SDK is a no-op, safe everywhere)
  - LoggingIntegration with event_level=None (breadcrumbs only, no auto-events)
  - Release + environment tagging
  - atexit flush for CLI apps
  - Convenience wrappers for capture_exception / capture_message / add_breadcrumb
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

if TYPE_CHECKING:
    from eye_witness._config import EyeWitnessConfig


def configure_sentry(cfg: EyeWitnessConfig) -> None:
    """Initialize Sentry SDK with Eye-Witness config values."""

    # Build the logging integration — breadcrumbs from all levels,
    # but we control event creation manually via capture_exception().
    sentry_logging = LoggingIntegration(
        level=None,        # breadcrumbs from all log levels
        event_level=None,  # don't auto-send log records as events
    )

    init_kwargs: dict[str, Any] = {
        "dsn": cfg.sentry_dsn,  # empty string → SDK does nothing
        "release": f"{cfg.service_name}@{cfg.service_version}",
        "environment": cfg.environment,
        "traces_sample_rate": cfg.sentry_traces_sample_rate,
        "max_breadcrumbs": cfg.sentry_max_breadcrumbs,
        "attach_stacktrace": cfg.sentry_attach_stacktrace,
        "send_default_pii": cfg.sentry_send_default_pii,
        "integrations": [sentry_logging],
    }

    if cfg.sentry_server_name:
        init_kwargs["server_name"] = cfg.sentry_server_name

    sentry_sdk.init(**init_kwargs)

# ── Convenience wrappers ────────────────────────────────────────────
# These re-export sentry_sdk functions so callers only import eye_witness.


def capture_exception(error: BaseException | None = None) -> str | None:
    """
    Send an exception event to Sentry (if DSN is configured).

    Returns the Sentry event ID, or None if the SDK is disabled.

    Usage:
        try:
            risky_operation()
        except Exception as e:
            log.exception("operation_failed")
            capture_exception(e)
    """
    return sentry_sdk.capture_exception(error)


def capture_message(
    message: str,
    level: Literal["fatal", "critical", "error", "warning", "info", "debug"] = "info",
) -> str | None:
    """
    Send a message event to Sentry (not an exception, just a notable condition).

    Returns the Sentry event ID, or None if the SDK is disabled.
    """
    return sentry_sdk.capture_message(message, level=level)


def add_breadcrumb(
    *,
    category: str,
    message: str,
    level: str = "info",
    data: dict[str, Any] | None = None,
) -> None:
    """
    Record a breadcrumb that will be attached to the next captured exception.

    Breadcrumbs tell the story of "what happened before the crash."

    Usage:
        add_breadcrumb(
            category="query",
            message="SELECT * FROM orders",
            data={"duration_ms": 45},
        )
    """
    sentry_sdk.add_breadcrumb(
        category=category,
        message=message,
        level=level,
        data=data or {},
    )


def set_tag(key: str, value: str) -> None:
    """Set a searchable Sentry tag (indexed, filterable in the UI)."""
    sentry_sdk.set_tag(key, value)


def set_context(name: str, data: dict[str, Any]) -> None:
    """Attach structured context to the current Sentry scope (not indexed)."""
    sentry_sdk.set_context(name, data)


def set_user(
    user_id: str,
    email: str | None = None,
    username: str | None = None,
) -> None:
    """Identify the affected user for Sentry's user-impact tracking."""
    user_data: dict[str, str] = {"id": user_id}
    if email:
        user_data["email"] = email
    if username:
        user_data["username"] = username
    sentry_sdk.set_user(user_data)
