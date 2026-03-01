"""
Structlog Configuration — All patterns from Path 1 reference.

Sections:
  1. Production-Ready JSON Configuration (stdlib integration)
  2. High-Performance Configuration (orjson + BytesLoggerFactory)
  3. Dev vs Production Auto-Detection
  4. ProcessorFormatter (Bridge stdlib -> structlog)
  5. Recommended Processor Pipeline Order
"""

import logging
import sys
from typing import Any

import structlog


# ---------------------------------------------------------------------------
# 1. Production-Ready JSON Configuration (stdlib integration)
#
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
#    Uses sys.stderr.isatty() to switch between:
#      - ConsoleRenderer (dev/TTY) — uses `rich` if installed
#      - JSONRenderer (production/containers) — with dict_tracebacks
# ---------------------------------------------------------------------------

def configure_auto_detect() -> None:
    """Auto-detect TTY for dev (pretty) vs production (JSON) formatting."""
    shared_processors: list[structlog.types.Processor] = [
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.add_log_level,
        structlog.contextvars.merge_contextvars,
    ]

    if sys.stderr.isatty():
        # Pretty printing when running in a terminal session.
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(),
        ]
    else:
        # Print JSON when running in a container / non-TTY.
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(processors=processors)


# ---------------------------------------------------------------------------
# 4. ProcessorFormatter (Bridge stdlib -> structlog)
#
#    Third-party library logs (which use stdlib logging) flow through
#    structlog's processor pipeline via this formatter.
# ---------------------------------------------------------------------------

def create_processor_formatter() -> structlog.stdlib.ProcessorFormatter:
    """Create a ProcessorFormatter to bridge stdlib logging -> structlog pipeline."""
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
# 5. Recommended Processor Pipeline Order
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
                                 of JSONRenderer.
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
