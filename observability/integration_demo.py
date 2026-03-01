"""
Integration Demo — All Three Paths Working Together

Demonstrates the full observability stack:
  - Path 1 (structlog): structured JSON logging with context variables
  - Path 2 (Sentry SDK): breadcrumbs, tags, context, exception capture
  - Path 3 (OpenTelemetry): spans, trace correlation in logs

Run:  python -m observability.integration_demo
"""

import os
import sys
import logging

import sentry_sdk
import structlog
from sentry_sdk.integrations.logging import LoggingIntegration
from structlog.contextvars import bind_contextvars, clear_contextvars

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

# Import our modules
from observability.tracing.log_correlation import add_trace_context


def separator(title: str) -> None:
    bar = "=" * 70
    print(f"\n{bar}")
    print(f"  {title}")
    print(f"{bar}\n")


def main() -> None:
    print("\n  Full Observability Stack — Integration Demo")
    print("  Path 1 (structlog) + Path 2 (Sentry) + Path 3 (OTel)\n")

    # ── Step 1: Initialize OpenTelemetry (Path 3) ────────────────────────
    separator("Step 1: Initialize OpenTelemetry")

    resource = Resource(attributes={
        "service.name": "integration-demo",
        "service.version": "1.0.0",
        "deployment.environment": "development",
    })
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    tracer = trace.get_tracer("integration.demo")
    print("  OTel TracerProvider ready (ConsoleSpanExporter)")

    # ── Step 2: Initialize Sentry (Path 2) ───────────────────────────────
    separator("Step 2: Initialize Sentry SDK")

    sentry_logging = LoggingIntegration(level=None, event_level=None)
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", ""),  # Empty = no-op
        release="integration-demo@1.0.0",
        environment="local",
        traces_sample_rate=0.0,
        integrations=[sentry_logging],
        attach_stacktrace=True,
    )
    print("  Sentry SDK initialized (no-DSN = no-op mode)")

    # ── Step 3: Configure structlog (Path 1) with OTel bridge ────────────
    separator("Step 3: Configure structlog with OTel log correlation")

    structlog.configure(
        processors=[
            # 1. Context first
            structlog.contextvars.merge_contextvars,
            # 2. Custom processor: trace context injection (Path 3 bridge)
            add_trace_context,
            # 3-4. Logger + level metadata
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            # 5. Timestamp
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            # 6-7. Stack + exception formatting
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # 8. JSON output
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=False,
    )

    # Add stdlib handler so output is visible
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)

    print("  structlog configured with recommended pipeline + OTel bridge")

    # ── Step 4: Simulate a request with full instrumentation ─────────────
    separator("Step 4: Simulated Request (all three paths active)")

    log = structlog.get_logger("integration.demo")

    with tracer.start_as_current_span("handle_request") as span:
        span.set_attribute("http.method", "POST")
        span.set_attribute("http.url", "/api/orders")

        # Path 1: contextvars
        clear_contextvars()
        bind_contextvars(request_id="req-integration-001")

        # Path 2: Sentry breadcrumbs + tags
        sentry_sdk.set_tag("request_id", "req-integration-001")
        sentry_sdk.add_breadcrumb(
            category="http",
            message="POST /api/orders",
            level="info",
            data={"method": "POST", "url": "/api/orders"},
        )

        # Log line has: structlog fields + contextvars + trace_id + span_id
        log.info("request.received", method="POST", path="/api/orders")

        # Nested span
        with tracer.start_as_current_span("validate_order") as child_span:
            child_span.set_attribute("validation.type", "schema")
            sentry_sdk.add_breadcrumb(
                category="validation",
                message="Order validated",
                level="info",
            )
            log.info("order.validated", order_id="ORD-42")

        # Simulate an error
        with tracer.start_as_current_span("process_payment") as child_span:
            try:
                raise ValueError("Insufficient funds")
            except Exception as e:
                # Path 3: record on span
                child_span.set_status(
                    trace.Status(trace.StatusCode.ERROR)
                )
                child_span.record_exception(e)

                # Path 2: capture in Sentry
                sentry_sdk.capture_exception(e)

                # Path 1: structured log
                log.exception("payment.failed", order_id="ORD-42")

    # ── Summary ──────────────────────────────────────────────────────────
    separator("Integration Summary")
    print("  Every log line contains:")
    print("    - structlog fields (event, level, timestamp)")
    print("    - contextvars (request_id)")
    print("    - OTel correlation (trace_id, span_id)")
    print()
    print("  Every error is:")
    print("    - Logged locally (structlog JSON)")
    print("    - Sent to Sentry (capture_exception) with breadcrumb trail")
    print("    - Recorded on OTel span (record_exception + ERROR status)")
    print()
    print("  All three paths work together with zero conflict.\n")

    # Cleanup
    for h in root.handlers[:]:
        root.removeHandler(h)
    provider.shutdown()


if __name__ == "__main__":
    main()
