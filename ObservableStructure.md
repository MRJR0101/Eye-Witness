# Observability Stack

Complete Python observability implementation covering structured logging,
error tracking, and distributed tracing.

## Structure

```
observability/
├── requirements.txt              # All dependencies
├── integration_demo.py           # Full stack demo (all 3 paths together)
├── README.md
│
├── logging/                      # Path 1 — Structlog
│   ├── config.py                 # 6 configuration patterns
│   ├── processors.py             # Custom processors (trace context bridge)
│   └── demo.py                   # Exercises all structlog patterns
│
├── error_tracking/               # Path 2 — Sentry SDK
│   ├── config.py                 # sentry_sdk.init(), LoggingIntegration
│   ├── breadcrumbs.py            # Breadcrumb helpers (http, query, ui, job)
│   ├── context.py                # Tags, structured context, user
│   ├── cli.py                    # CLI patterns (flush, command wrapping)
│   └── demo.py                   # Exercises all Sentry patterns
│
└── tracing/                      # Path 3 — OpenTelemetry
    ├── provider.py               # TracerProvider (Console, OTLP HTTP, gRPC)
    ├── spans.py                  # Manual instrumentation (decorator, errors)
    ├── propagation.py            # Context propagation (inject / extract)
    ├── sampling.py               # Sampler configurations
    ├── log_correlation.py        # trace_id/span_id injection into structlog
    ├── cli.py                    # CLI patterns (root span, shutdown)
    └── demo.py                   # Exercises all OTel patterns
```

## Quick Start

```powershell
cd observability
pip install -r requirements.txt
```

## Run Individual Path Demos

```powershell
# Path 1 — Structlog
python -m observability.logging.demo

# Path 2 — Sentry SDK
python -m observability.error_tracking.demo

# Path 3 — OpenTelemetry
python -m observability.tracing.demo
```

## Run Integration Demo

```powershell
python -m observability.integration_demo
```

## How the Paths Connect

1. **Path 1 (structlog)** provides the logging layer — JSON output,
   context variables, processor pipelines.

2. **Path 2 (Sentry SDK)** adds error tracking — breadcrumbs record
   what happened before a crash, tags enable searching, context
   provides debugging data.

3. **Path 3 (OpenTelemetry)** adds distributed tracing — spans track
   timing and errors, trace_id/span_id are injected into every
   structlog line via `log_correlation.py`.

The integration point is `tracing/log_correlation.py`, which provides
the `add_trace_context` structlog processor. This processor goes at
position 2 in the recommended pipeline (after `merge_contextvars`,
before `add_logger_name`).

## Environment Variables

| Variable | Purpose |
|---|---|
| `SENTRY_DSN` | Sentry project DSN (empty = SDK disabled) |
| `SENTRY_ENVIRONMENT` | Environment name for Sentry |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTel collector endpoint |
| `OTEL_BSP_SCHEDULE_DELAY` | Batch export interval (ms) |
| `OTEL_BSP_MAX_QUEUE_SIZE` | Max queued spans before dropping |

## GlitchTip Compatibility

GlitchTip is a Sentry-compatible, self-hosted error tracker.
To switch: change `SENTRY_DSN` to point at your GlitchTip instance.
No code changes required.

## Compatible Tracing Backends

Any OTLP-compatible backend works with Path 3:
SigNoz, Jaeger, Grafana Tempo, Datadog, Honeycomb, New Relic.
