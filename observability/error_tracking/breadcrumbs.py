"""
Sentry Breadcrumbs — Context before the crash.

Breadcrumbs record events leading up to an error. They are attached
to the next captured exception.

Common categories: http, query, ui.click, console, job

Best practices from the reference:
  - Use consistent category values for grouping
  - Include timing data in the data dict where possible
  - Keep message concise but descriptive
  - Breadcrumbs are a circular buffer — oldest dropped at max_breadcrumbs
"""

from typing import Any

import sentry_sdk


def add_http_breadcrumb(
    method: str,
    url: str,
    status_code: int,
    *,
    response_time_ms: float | None = None,
    level: str = "info",
    extra: dict[str, Any] | None = None,
) -> None:
    """Record an HTTP request breadcrumb."""
    data: dict[str, Any] = {"status_code": status_code}
    if response_time_ms is not None:
        data["response_time_ms"] = response_time_ms
    if extra:
        data.update(extra)

    sentry_sdk.add_breadcrumb(
        category="http",
        message=f"{method} {url}",
        level=level,
        data=data,
    )


def add_query_breadcrumb(
    query: str,
    *,
    duration_ms: float | None = None,
    rows_returned: int | None = None,
    level: str = "info",
) -> None:
    """Record a database query breadcrumb."""
    data: dict[str, Any] = {"query": query}
    if duration_ms is not None:
        data["duration_ms"] = duration_ms
    if rows_returned is not None:
        data["rows_returned"] = rows_returned

    sentry_sdk.add_breadcrumb(
        category="query",
        message="Database query executed",
        level=level,
        data=data,
    )


def add_ui_breadcrumb(
    action: str,
    *,
    element: str = "",
    level: str = "info",
    extra: dict[str, Any] | None = None,
) -> None:
    """Record a user interaction breadcrumb."""
    data: dict[str, Any] = {}
    if extra:
        data.update(extra)

    sentry_sdk.add_breadcrumb(
        category="ui.click",
        message=f"User {action}" + (f" '{element}'" if element else ""),
        level=level,
        data=data,
    )


def add_console_breadcrumb(
    message: str,
    *,
    level: str = "info",
) -> None:
    """Record a console/log breadcrumb."""
    sentry_sdk.add_breadcrumb(
        category="console",
        message=message,
        level=level,
    )


def add_job_breadcrumb(
    message: str,
    *,
    job_id: str = "",
    level: str = "info",
    extra: dict[str, Any] | None = None,
) -> None:
    """Record a background job breadcrumb."""
    data: dict[str, Any] = {}
    if job_id:
        data["job_id"] = job_id
    if extra:
        data.update(extra)

    sentry_sdk.add_breadcrumb(
        category="job",
        message=message,
        level=level,
        data=data,
    )
