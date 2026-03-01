"""
Eye-Witness CLI example — demonstrates the full observability stack.

Run with:
    python -m examples.cli_demo

Or set env vars first:
    set EW_SENTRY_DSN=https://...
    set EW_OTEL_EXPORTER=otlp-http
    python -m examples.cli_demo
"""

import os
import sys
import time

# Add parent to path so we can import eye_witness directly
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from eye_witness import (
    add_breadcrumb,
    bind_context,
    capture_exception,
    clear_context,
    get_logger,
    get_tracer,
    init,
    shutdown,
    trace_span,
)


def simulate_database_query(query: str, rows: int) -> list[dict]:
    """Pretend to run a database query."""
    add_breadcrumb(
        category="query",
        message=query,
        data={"rows_returned": rows, "duration_ms": 23},
    )
    time.sleep(0.05)  # simulate latency
    return [{"id": i, "name": f"item-{i}"} for i in range(rows)]


def process_order(order_id: str) -> dict:
    """Example business logic with nested tracing."""
    tracer = get_tracer("demo.orders")
    log = get_logger("demo.orders")

    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        log.info("order.processing_started", order_id=order_id)

        # Step 1: validate
        with trace_span("validate_order", attributes={"order.id": order_id}):
            log.debug("order.validating", order_id=order_id)
            time.sleep(0.01)

        # Step 2: query inventory
        with trace_span("check_inventory"):
            items = simulate_database_query(
                "SELECT * FROM inventory WHERE order_id = ?", rows=3
            )
            log.info("order.inventory_checked", item_count=len(items))

        # Step 3: charge
        with trace_span("charge_payment", attributes={"amount": 99.99}):
            add_breadcrumb(
                category="payment",
                message="Charging customer",
                data={"amount": 99.99, "currency": "USD"},
            )
            time.sleep(0.02)

        log.info("order.completed", order_id=order_id, items=len(items))
        return {"order_id": order_id, "status": "completed", "items": len(items)}


def simulate_failure():
    """Demonstrate error capture flow."""
    log = get_logger("demo.errors")

    try:
        # This will fail
        _ = 1 / 0
    except ZeroDivisionError as e:
        log.exception("math.division_by_zero")
        capture_exception(e)
        log.warning("math.recovered", fallback_value=0)


def should_simulate_failure() -> bool:
    """Opt-in failure path for demo purposes."""
    return os.getenv("EW_DEMO_SIMULATE_FAILURE", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def main():
    # ── Initialize Eye-Witness ──────────────────────────────────────
    init(
        service_name="eye-witness-demo",
        service_version="0.1.0",
        environment="local",
        log_level="DEBUG",
        log_format="auto",         # auto-detect TTY vs container
        otel_exporter="console",   # print spans to console for demo
        otel_sample_rate=1.0,      # capture every trace for demo
        sentry_dsn=os.getenv("SENTRY_DSN", ""),  # optional
    )

    log = get_logger("demo.main")

    # ── Bind request context ────────────────────────────────────────
    clear_context()
    bind_context(request_id="req-001", user_id="usr-42")

    log.info("demo.started", message="Eye-Witness demo is running")

    # ── Run business logic with tracing ─────────────────────────────
    result = process_order("ORD-12345")
    log.info("demo.order_result", **result)

    # ── Demonstrate error handling (opt-in) ────────────────────────
    if should_simulate_failure():
        simulate_failure()
    else:
        log.info(
            "demo.failure_simulation_skipped",
            hint="Set EW_DEMO_SIMULATE_FAILURE=1 to enable",
        )

    # ── Clean up ────────────────────────────────────────────────────
    log.info("demo.finished")
    shutdown()


if __name__ == "__main__":
    main()
