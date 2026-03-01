"""
Structlog Configuration — Path 1 (Official Docs Reference)

Structured logging layer on top of Python's stdlib `logging`.
Provides JSON output, context binding via contextvars, processor pipelines,
and clean integration with stdlib log records from third-party libraries.
"""

import logging
import sys
from typing import Any

import structlog


# ---------------------------------------------------------------------------
# 1. Production-Ready JSON Configuration (stdlib integration)
#
#    Recommended setup when integrating with Python's standard `logging` module.
#    Ensures both structlog loggers AND stdlib loggers (from dependencies like
#    uvicorn, requests, sqlalchemy) output through the same pipeline.
# ---------------------------------------------------------------------------

def configure_production_stdlib() -> None:
    """Full production config with stdlib integration."""
    structlog.configure(
        processors=[
            # If log level is too low, abort pipeline and throw away log entry.
            structlog.stdlib.filter_by_level,
            # Add the name of the logger to event dict.
            structlog.stdlib.add_logger_name,
            # Add log level to event dict.
            structlog.stdlib.add_log_level,
            # Perform %-style formatting.
            structlog.stdlib.PositionalArgumentsFormatter(),
            # Add a timestamp in ISO 8601 format.
            structlog.processors.TimeStamper(fmt="iso"),
            # If the "stack_info" key in the event dict is true, remove it and
            # render the current stack trace in the "stack" key.
            structlog.processors.StackInfoRenderer(),
            # If the "exc_info" key in the event dict is either true or a
            # sys.exc_info() tuple, remove "exc_info" and render the exception
            # with traceback into the "exception" key.
            structlog.processors.format_exc_info,
            # If some value is in bytes, decode it to a Unicode str.
            structlog.processors.UnicodeDecoder(),
            # Add callsite parameters (file, function, line number).
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                }
            ),
            # Render the final event dict as JSON.
            structlog.processors.JSONRenderer(),
        ],
        # wrapper_class imitates the API of logging.Logger
        wrapper_class=structlog.stdlib.BoundLogger,
        # logger_factory returns a logging.Logger for OUTPUT
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Freeze configuration after creating the first bound logger
        cache_logger_on_first_use=True,
    )


# ---------------------------------------------------------------------------
# 2. High-Performance Configuration (Maximum Speed)
#
#    For performance-critical paths where logging overhead matters.
#    - Filters below `info` very efficiently (debug method = return None)
#    - Uses orjson for JSON serialization (faster than stdlib json)
#    - Uses BytesLoggerFactory because orjson returns bytes
#    - Supports context variables for thread-local / async contexts
#
#    Extra dependency: pip install orjson
# ---------------------------------------------------------------------------

def configure_high_performance() -> None:
    """High-performance config using orjson and BytesLoggerFactory."""
    import orjson

    structlog.configure(
        cache_logger_on_first_use=True,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(serializer=orjson.dumps),
        ],
        logger_factory=structlog.BytesLoggerFactory(),
    )


# ---------------------------------------------------------------------------
# 3. Dev vs Production Auto-Detection
#
#    Automatically switch between pretty console output (dev/TTY) and
#    JSON (production/containers) using sys.stderr.isatty().
# ---------------------------------------------------------------------------

def configure_auto_detect() -> None:
    """Auto-detect TTY for dev (pretty) vs production (JSON) formatting."""
    shared_processors: list[structlog.types.Processor] = [
        # Processors that have nothing to do with output,
        # e.g., add timestamps or log level names.
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.add_log_level,
        structlog.contextvars.merge_contextvars,
    ]

    if sys.stderr.isatty():
        # Pretty printing when running in a terminal session.
        # Automatically prints pretty tracebacks when "rich" is installed.
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(),
        ]
    else:
        # Print JSON when running in a container / non-TTY.
        # Also print structured tracebacks.
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(processors=processors)


# ---------------------------------------------------------------------------
# 4. Context Variables (Thread-Safe Context Binding)
#
#    - merge_contextvars must be in your processor chain
#    - clear_contextvars() at the start of each unit of work prevents leaking
#    - Works with both threading and asyncio
#    - Context is inherited by child tasks/threads
# ---------------------------------------------------------------------------

from structlog.contextvars import (
    bind_contextvars,
    clear_contextvars,
    merge_contextvars,
)

log = structlog.get_logger()


def handle_request(request_id: str) -> None:
    """Example: bind request context for the lifetime of a request."""
    clear_contextvars()
    bind_contextvars(request_id=request_id)

    log.info("request.start")
    # All subsequent log calls in this execution context include request_id
    # do_work()
    log.info("request.done")


# ---------------------------------------------------------------------------
# 5. ProcessorFormatter (Bridge stdlib → structlog)
#
#    When you want third-party library logs (which use stdlib `logging`) to
#    flow through structlog's processor pipeline.
#
#    - foreign_pre_chain processes log records from stdlib loggers (not structlog)
#    - Attach this formatter to your stdlib handlers (file, console, etc.)
#    - This ensures ALL logs (structlog + stdlib) go through the same pipeline
# ---------------------------------------------------------------------------

def create_processor_formatter() -> structlog.stdlib.ProcessorFormatter:
    """Create a ProcessorFormatter to bridge stdlib logging → structlog pipeline."""
    return structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=[
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ],
    )


def setup_stdlib_handler_with_formatter() -> None:
    """Attach the ProcessorFormatter to stdlib's root logger handler."""
    formatter = create_processor_formatter()
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# 6. Processor Pipeline Order (Recommended)
#
#    1. structlog.contextvars.merge_contextvars     — Context first
#    2. [custom processors, e.g., trace context]    — Your additions
#    3. structlog.stdlib.add_logger_name            — Logger metadata
#    4. structlog.stdlib.add_log_level              — Level metadata
#    5. structlog.processors.TimeStamper(...)       — Timestamp
#    6. structlog.processors.StackInfoRenderer()    — Stack traces
#    7. structlog.processors.format_exc_info        — Exception formatting
#    8. structlog.stdlib.ProcessorFormatter.wrap_for_formatter  (if using ProcessorFormatter)
#       — OR —
#       structlog.processors.JSONRenderer()         (if direct output)
# ---------------------------------------------------------------------------

def configure_recommended_pipeline(
    *,
    custom_processors: list[structlog.types.Processor] | None = None,
    use_processor_formatter: bool = False,
) -> None:
    """
    Configure structlog with the recommended processor pipeline order.

    Args:
        custom_processors: Extra processors inserted after merge_contextvars
                           (e.g., trace-context injection).
        use_processor_formatter: If True, end with wrap_for_formatter instead
                                 of JSONRenderer (use when bridging via
                                 ProcessorFormatter on stdlib handlers).
    """
    processors: list[structlog.types.Processor] = [
        # 1. Context first
        structlog.contextvars.merge_contextvars,
    ]

    # 2. Custom processors (e.g., trace context)
    if custom_processors:
        processors.extend(custom_processors)

    processors.extend([
        # 3. Logger metadata
        structlog.stdlib.add_logger_name,
        # 4. Level metadata
        structlog.stdlib.add_log_level,
        # 5. Timestamp
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        # 6. Stack traces
        structlog.processors.StackInfoRenderer(),
        # 7. Exception formatting
        structlog.processors.format_exc_info,
    ])

    # 8. Final renderer
    if use_processor_formatter:
        processors.append(structlog.stdlib.ProcessorFormatter.wrap_for_formatter)
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# ---------------------------------------------------------------------------
# Best Practices Summary (from Path 1)
#
#  1. Always use cache_logger_on_first_use=True
#  2. Use contextvars for request/job context — not function parameters
#  3. Use ProcessorFormatter to bridge stdlib logs — unifies all output
#  4. Use orjson in performance-critical paths — measurably faster
#  5. Auto-detect TTY for dev vs prod formatting — one config, both envs
#  6. Add CallsiteParameterAdder in development — invaluable for debugging
#  7. Clear contextvars at the start of each unit of work — prevents leaking
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # Quick demo: auto-detect dev/prod and log a few events
    configure_auto_detect()

    demo_log = structlog.get_logger()
    demo_log.info("structlog.configured", mode="auto-detect")
    demo_log.warning("example.warning", detail="something to note")

    try:
        1 / 0
    except ZeroDivisionError:
        demo_log.exception("example.error")
