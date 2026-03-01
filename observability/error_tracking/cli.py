"""
Sentry CLI-Specific Patterns.

For CLI applications (not web frameworks), there are no auto-instrumenting
integrations. The reference prescribes these patterns:

  1. Initialize early, flush on exit
  2. Wrap each command in context
  3. No-DSN safety
"""

import atexit
from typing import Any, Callable, TypeVar

import sentry_sdk

T = TypeVar("T")


def flush_on_exit(timeout: float = 2.0) -> None:
    """
    Register an atexit handler to flush Sentry events before process exit.

    Call this once after sentry_sdk.init() in CLI applications.
    """
    atexit.register(lambda: sentry_sdk.flush(timeout=timeout))


def wrap_command(
    name: str,
    func: Callable[..., T],
    *args: Any,
    **kwargs: Any,
) -> T:
    """
    Wrap a CLI command with Sentry context: tag, breadcrumb, and capture.

    Usage:
        result = wrap_command("sync", run_sync, source="s3", dest="local")
    """
    sentry_sdk.set_tag("cli.command", name)
    sentry_sdk.add_breadcrumb(
        category="cli",
        message=f"Running: {name}",
        level="info",
    )

    try:
        return func(*args, **kwargs)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise
