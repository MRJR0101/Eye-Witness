"""
Eye-Witness context management.

Provides unified context binding that flows into BOTH:
  - structlog (via contextvars → merge_contextvars)
  - Sentry (via set_tag / set_context)

Call bind_context() once and the data appears in your logs AND your Sentry events.
"""

from __future__ import annotations

import logging
from typing import Any

import sentry_sdk
from structlog.contextvars import bind_contextvars, clear_contextvars

logger = logging.getLogger(__name__)


def bind_context(**kwargs: Any) -> None:
    """
    Bind key-value pairs to the current execution context.

    The values appear in:
      - Every subsequent structlog log line (via merge_contextvars)
      - Sentry tags (for short string values) and context (for all values)

    Usage:
        bind_context(request_id="req-abc", user_id="usr-42")
    """
    # structlog context (appears in every log line)
    bind_contextvars(**kwargs)

    # Sentry tags (searchable) — only short strings
    for key, value in kwargs.items():
        str_val = str(value)
        if len(str_val) <= 200:
            sentry_sdk.set_tag(key, str_val)

    # Sentry context (structured, displayed in event detail)
    sentry_sdk.set_context("eye_witness", kwargs)


def clear_context() -> None:
    """
    Clear all bound context.

    Call this at the start of each request / job / CLI command
    to prevent context from leaking across units of work.
    """
    clear_contextvars()

    # Also reset Sentry scope data to avoid cross-request leakage.
    try:
        sentry_sdk.get_current_scope().clear()
    except Exception:
        logger.debug("Failed to clear Sentry scope", exc_info=True)
