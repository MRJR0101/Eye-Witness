"""
Structlog Demo — Path 1 Complete Walkthrough

Exercises every configuration and pattern from the Path 1 reference:
  1. Production-Ready JSON Configuration (stdlib integration)
  2. High-Performance Configuration (orjson + BytesLoggerFactory)
  3. Dev vs Production Auto-Detection
  4. Context Variables (Thread-Safe Context Binding)
  5. ProcessorFormatter (Bridge stdlib → structlog)
  6. Recommended Processor Pipeline Order

Run:  python structlog_demo.py
"""

import logging
import sys

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars


# ── Helpers ──────────────────────────────────────────────────────────────────

def separator(title: str) -> None:
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def reset_structlog() -> None:
    """Reset structlog between demos so each config starts clean."""
    structlog.reset_defaults()
    clear_contextvars()


def reset_stdlib_logging() -> None:
    """Remove all handlers from the root logger between demos."""
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)


# ── Demo 1: Production-Ready JSON (stdlib integration) ───────────────────────

def demo_production_stdlib() -> None:
    separator("1. Production-Ready JSON Configuration (stdlib integration)")
    reset_structlog()
    reset_stdlib_logging()

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                }
            ),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=False,  # False for demo (allow reconfigure)
    )

    # stdlib LoggerFactory needs a handler configured
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)

    log = structlog.get_logger("demo.production")
    log.info("production_config_active", feature="CallsiteParameterAdder")
    log.warning("example_warning", user_id="u-42", action="checkout")

    try:
        1 / 0
    except ZeroDivisionError:
        log.exception("caught_exception")

    reset_stdlib_logging()


# ── Demo 2: High-Performance Configuration ───────────────────────────────────

def demo_high_performance() -> None:
    separator("2. High-Performance Configuration (orjson + BytesLoggerFactory)")
    reset_structlog()

    try:
        import orjson
    except ImportError:
        print("  [SKIP] orjson not installed — run: pip install orjson")
        return

    structlog.configure(
        cache_logger_on_first_use=False,
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

    log = structlog.get_logger()

    # debug is filtered — method literally returns None
    log.debug("this_is_filtered_out")

    log.info("high_perf_active", serializer="orjson")
    log.warning("example_event", rows_processed=50_000)


# ── Demo 3: Dev vs Production Auto-Detection ─────────────────────────────────

def demo_auto_detect() -> None:
    separator("3. Dev vs Production Auto-Detection")
    reset_structlog()

    is_tty = sys.stderr.isatty()
    print(f"  sys.stderr.isatty() = {is_tty}")

    shared_processors = [
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.add_log_level,
        structlog.contextvars.merge_contextvars,
    ]

    if is_tty:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(),
        ]
    else:
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        cache_logger_on_first_use=False,
    )

    log = structlog.get_logger()
    log.info("auto_detect_active", mode="tty" if is_tty else "json")

    try:
        raise ValueError("simulated error for traceback demo")
    except ValueError:
        log.exception("traceback_demo")


# ── Demo 4: Context Variables ─────────────────────────────────────────────────

def demo_contextvars() -> None:
    separator("4. Context Variables (Thread-Safe Context Binding)")
    reset_structlog()

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        cache_logger_on_first_use=False,
    )

    log = structlog.get_logger()

    def handle_request(request_id: str) -> None:
        clear_contextvars()
        bind_contextvars(request_id=request_id)

        log.info("request.start")
        # Simulate work — context follows automatically
        log.info("request.processing", step="validate")
        log.info("request.processing", step="transform")
        log.info("request.done")

    handle_request("req-abc-001")
    handle_request("req-def-002")


# ── Demo 5: ProcessorFormatter (Bridge stdlib → structlog) ────────────────────

def demo_processor_formatter() -> None:
    separator("5. ProcessorFormatter (Bridge stdlib → structlog)")
    reset_structlog()
    reset_stdlib_logging()

    # Create formatter that bridges stdlib → structlog pipeline
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=[
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ],
    )

    # Attach to a stdlib handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    # Now stdlib loggers (like those from third-party libraries) go through
    # structlog's processor pipeline
    stdlib_logger = logging.getLogger("third_party.library")
    stdlib_logger.info("This stdlib log goes through structlog processors")
    stdlib_logger.warning("So does this warning from a 'third-party' library")

    # Clean up
    reset_stdlib_logging()


# ── Demo 6: Recommended Pipeline Order ────────────────────────────────────────

def demo_recommended_pipeline() -> None:
    separator("6. Recommended Processor Pipeline Order")
    reset_structlog()
    reset_stdlib_logging()

    # The recommended order, with a custom processor slot for trace context
    def add_custom_context(logger, method_name, event_dict):
        """Custom processor — slot 2 in the recommended pipeline."""
        event_dict["app_version"] = "1.0.0"
        return event_dict

    structlog.configure(
        processors=[
            # 1. Context first
            structlog.contextvars.merge_contextvars,
            # 2. Custom processors
            add_custom_context,
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
            # 8. Final renderer (JSONRenderer for direct output)
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=False,
    )

    # stdlib LoggerFactory needs a handler to emit output
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)

    clear_contextvars()
    bind_contextvars(request_id="req-pipeline-demo")

    log = structlog.get_logger("demo.pipeline")
    log.info("recommended_pipeline_active", note="all 8 slots populated")

    # Clean up
    reset_stdlib_logging()


# ── Best Practices Recap ─────────────────────────────────────────────────────

def print_best_practices() -> None:
    separator("Best Practices Summary (Path 1)")
    practices = [
        "Always use cache_logger_on_first_use=True",
        "Use contextvars for request/job context — not function parameters",
        "Use ProcessorFormatter to bridge stdlib logs — unifies all output",
        "Use orjson in performance-critical paths — measurably faster",
        "Auto-detect TTY for dev vs prod formatting — one config, both envs",
        "Add CallsiteParameterAdder in development — invaluable for debugging",
        "Clear contextvars at the start of each unit of work — prevents leaking",
    ]
    for i, p in enumerate(practices, 1):
        print(f"  {i}. {p}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("\n  Structlog Path 1 — Complete Demo")
    print("  Running all 6 configuration patterns...\n")

    demo_production_stdlib()
    demo_high_performance()
    demo_auto_detect()
    demo_contextvars()
    demo_processor_formatter()
    demo_recommended_pipeline()
    print_best_practices()

    print("  Done. All Path 1 patterns exercised.\n")


if __name__ == "__main__":
    main()
