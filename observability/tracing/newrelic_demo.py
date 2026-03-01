"""
New Relic OTLP Demo — Pure OTel → New Relic

Exercises the explicit Python setup from the New Relic guide:
  1. Resource with service.name, version, environment
  2. OTLPSpanExporter → https://otlp.nr-data.net/v1/traces
  3. api-key header from NEW_RELIC_LICENSE_KEY
  4. BatchSpanProcessor (production) + ConsoleSpanExporter (visibility)
  5. Manual spans with attributes
  6. Error recording on spans
  7. Log correlation (trace_id/span_id in structlog)

Run:  python -m observability.tracing.newrelic_demo

Without NEW_RELIC_LICENSE_KEY set, spans print to console only.
With it set, spans also export to New Relic APM → Traces.
"""

import os
import sys
import logging

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode


def separator(title: str) -> None:
    bar = "=" * 70
    print(f"\n{bar}")
    print(f"  {title}")
    print(f"{bar}\n")


def main() -> None:
    print("\n  New Relic OTLP Demo — Pure OTel → New Relic")

    nr_key = os.getenv("NEW_RELIC_LICENSE_KEY", "")
    if nr_key:
        print(f"  License key: {'*' * 8}...{nr_key[-4:]}")
        print("  Spans will export to New Relic AND console\n")
    else:
        print("  No NEW_RELIC_LICENSE_KEY — console-only mode")
        print("  Set the env var to export to New Relic\n")

    # ── 1. Setup provider ─────────────────────────────────────────────────
    separator("1. Setup New Relic OTLP Provider")

    from observability.tracing.newrelic import (
        setup_newrelic_with_console_fallback,
        setup_newrelic_otlp_provider,
    )

    if nr_key:
        # Dual export: console + New Relic
        provider = setup_newrelic_with_console_fallback(
            service_name="newrelic-demo",
            service_version="1.0.0",
            environment="development",
            license_key=nr_key,
        )
        print("  Provider: ConsoleSpanExporter + OTLP → New Relic")
    else:
        # Console only (no NR key)
        from observability.tracing.provider import setup_console_provider
        provider = setup_console_provider(
            service_name="newrelic-demo",
            service_version="1.0.0",
            environment="development",
        )
        print("  Provider: ConsoleSpanExporter only (no NR key)")

    tracer = trace.get_tracer("newrelic.demo")

    # ── 2. Configure structlog with OTel bridge ──────────────────────────
    separator("2. Structlog + OTel Log Correlation")

    from observability.tracing.log_correlation import add_trace_context

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_trace_context,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        cache_logger_on_first_use=False,
    )
    log = structlog.get_logger("newrelic.demo")
    print("  structlog configured with trace_id/span_id injection")

    # ── 3. Basic span with attributes ────────────────────────────────────
    separator("3. Basic Span → New Relic")

    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", "ORD-NR-001")
        span.set_attribute("order.total", 149.99)
        span.set_attribute("order.items", 3)

        clear_contextvars()
        bind_contextvars(request_id="req-nr-demo-001")

        log.info("order.received", order_id="ORD-NR-001", total=149.99)

        # Nested child span
        with tracer.start_as_current_span("validate_payment") as child:
            child.set_attribute("payment.method", "credit_card")
            child.set_attribute("payment.provider", "stripe")
            log.info("payment.validating", method="credit_card")

        with tracer.start_as_current_span("ship_order") as child:
            child.set_attribute("shipping.carrier", "usps")
            log.info("order.shipped", carrier="usps")

    # ── 4. Error span ────────────────────────────────────────────────────
    separator("4. Error Span → New Relic")

    with tracer.start_as_current_span("risky_operation") as span:
        try:
            raise ConnectionError("Payment gateway timeout")
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR))
            span.record_exception(e)
            log.error("operation.failed", error=str(e))
            print(f"  Recorded error: {e}")

    # ── 5. Summary ───────────────────────────────────────────────────────
    separator("Summary")

    print("  Spans created:")
    print("    - process_order (root)")
    print("      - validate_payment (child)")
    print("      - ship_order (child)")
    print("    - risky_operation (error)")
    print()
    if nr_key:
        print("  Check New Relic APM → Traces for 'newrelic-demo' service")
        print("  Each span has attributes, events, and error status.")
    else:
        print("  Set NEW_RELIC_LICENSE_KEY to see these in New Relic.")
    print()

    print("  Log lines contain trace_id + span_id for correlation:")
    print("    → In New Relic: Logs → filter by trace.id")
    print()

    # Cleanup
    provider.shutdown()


if __name__ == "__main__":
    main()
