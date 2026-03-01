"""
Manual Instrumentation — Creating Spans.

From the Path 3 reference:
  - Basic spans with attributes
  - Nested spans (parent-child)
  - Span events (point-in-time annotations)
  - Error status on spans
"""

from functools import wraps
from typing import Any, Callable, TypeVar

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

T = TypeVar("T")


def traced(
    name: str = "",
    *,
    op: str = "",
    attributes: dict[str, Any] | None = None,
) -> Callable:
    """Decorator to wrap a function in an OTel span."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        span_name = name or func.__qualname__

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            tracer = trace.get_tracer(func.__module__)
            with tracer.start_as_current_span(span_name) as span:
                if op:
                    span.set_attribute("operation", op)
                if attributes:
                    for k, v in attributes.items():
                        span.set_attribute(k, v)
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator


def record_error(span: trace.Span, exception: Exception) -> None:
    """Record an exception on a span with ERROR status."""
    span.set_status(Status(StatusCode.ERROR))
    span.record_exception(exception)
