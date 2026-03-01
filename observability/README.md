# Eye-Witness — Observability Stack

Complete Python observability implementation covering structured logging,
error tracking, and distributed tracing with New Relic OTLP export.

## Structure

```
observability/
├── pyproject.toml                # Package definition + all dependencies
├── .env.example                  # Environment variables template (New Relic)
├── requirements.txt              # Flat dependency list (pip fallback)
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
├── tracing/                      # Path 3 — OpenTelemetry
│   ├── provider.py               # TracerProvider (Console, OTLP HTTP, gRPC)
│   ├── newrelic.py               # New Relic OTLP provider (pure OTel → NR)
│   ├── spans.py                  # Manual instrumentation (decorator, errors)
│   ├── propagation.py            # Context propagation (inject / extract)
│   ├── sampling.py               # Sampler configurations
│   ├── log_correlation.py        # trace_id/span_id injection into structlog
│   ├── cli.py                    # CLI patterns (root span, shutdown)
│   ├── demo.py                   # Exercises all OTel patterns
│   └── newrelic_demo.py          # New Relic OTLP export demo
│
└── scripts/
    └── bootstrap-telemetry.ps1   # Auto-instrumentation discovery (uv flow)
```

## Quick Start (pip)

```powershell
cd <project-root>\observability
pip install -r requirements.txt
```

## Quick Start (uv + pyproject.toml)

```powershell
cd <project-root>\observability
uv sync --extra all
```

## New Relic OTLP Setup

1. Copy the environment template and add your license key:

```powershell
Copy-Item .env.example .env
# Edit .env → set NEW_RELIC_LICENSE_KEY
```

2. (Optional) Run auto-instrumentation bootstrap:

```powershell
.\scripts\bootstrap-telemetry.ps1
```

3. Run with auto-instrumentation (env-var-only, no custom code):

```powershell
uv run --extra telemetry opentelemetry-instrument python app.py
```

Or use explicit Python setup (code control):

```python
from observability.tracing.newrelic import setup_newrelic_otlp_provider

provider = setup_newrelic_otlp_provider(
    service_name="my-app",
    license_key="NRJS-...",
)
# ... your app code with tracer.start_as_current_span() ...
provider.shutdown()
```

## Run Individual Path Demos

```powershell
# Path 1 — Structlog
python -m observability.logging.demo

# Path 2 — Sentry SDK
python -m observability.error_tracking.demo

# Path 3 — OpenTelemetry
python -m observability.tracing.demo

# New Relic OTLP
python -m observability.tracing.newrelic_demo
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

4. **New Relic** receives all OTel data via OTLP HTTP. No vendor SDK
   needed — pure OTel → New Relic OTLP endpoint. This is New Relic's
   recommended, most future-proof integration path.

The integration point is `tracing/log_correlation.py`, which provides
the `add_trace_context` structlog processor. This processor goes at
position 2 in the recommended pipeline (after `merge_contextvars`,
before `add_logger_name`).

## New Relic Architecture

```
Your Python App
    │
    ├─ structlog (JSON logs + trace_id/span_id)
    ├─ sentry-sdk (breadcrumbs, error capture)
    └─ opentelemetry-sdk
         │
         ├─ BatchSpanProcessor
         │   └─ OTLPSpanExporter (http/protobuf)
         │       └─ https://otlp.nr-data.net/v1/traces
         │           Header: api-key=<NEW_RELIC_LICENSE_KEY>
         │
         └─ (Optional) ConsoleSpanExporter (dev visibility)
```

## Environment Variables

| Variable | Purpose |
|---|---|
| `NEW_RELIC_LICENSE_KEY` | New Relic ingest license key |
| `SENTRY_DSN` | Sentry project DSN (empty = SDK disabled) |
| `SENTRY_ENVIRONMENT` | Environment name for Sentry |
| `OTEL_SERVICE_NAME` | Service name in traces |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP endpoint (default: New Relic US) |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | Protocol (http/protobuf recommended) |
| `OTEL_EXPORTER_OTLP_HEADERS` | api-key header for New Relic |
| `OTEL_TRACES_EXPORTER` | Exporter type (otlp, console, none) |
| `OTEL_TRACES_SAMPLER` | Sampling strategy (always_on, traceidratio) |
| `OTEL_BSP_SCHEDULE_DELAY` | Batch export interval (ms) |
| `OTEL_BSP_MAX_QUEUE_SIZE` | Max queued spans before dropping |

## GlitchTip Compatibility

GlitchTip is a Sentry-compatible, self-hosted error tracker.
To switch: change `SENTRY_DSN` to point at your GlitchTip instance.
No code changes required.

## Compatible Tracing Backends

Any OTLP-compatible backend works with Path 3:
SigNoz, Jaeger, Grafana Tempo, Datadog, Honeycomb, **New Relic** (recommended).

To switch backends: change `OTEL_EXPORTER_OTLP_ENDPOINT` and headers.
No code changes needed — that's the power of vendor-neutral OTel.

## Overview (What & Why)

The `observability` package provides a practical reference implementation for running logging, error tracking, and distributed tracing together with consistent context propagation.

It is intended for teams building Python services that need a copyable baseline and validation path for observability stack integration.

It is not a full production platform by itself; backend provisioning, dashboard design, and alert policy remain external responsibilities.

## Features / Capabilities

- Structured logging path with configurable processors and renderer modes.
- Sentry/GlitchTip-compatible error tracking helpers.
- OpenTelemetry tracing with OTLP export and New Relic-ready defaults.
- Integration demo covering all three pillars in one run.
- Vendor-neutral tracing architecture (OTLP-compatible backends).

## Input / Output

**Expects:** Python runtime, configured dependencies, and optional environment variables (`SENTRY_DSN`, `NEW_RELIC_LICENSE_KEY`, OTEL settings).  
**Creates:** structured logs, captured error events, and trace spans exported to console or configured OTLP endpoints.

## Hardcoded Paths

This stack is mostly parameterized via environment variables and config values; repository-relative module paths are used for local examples and demos.

## Safety & Reliability

- Degrades gracefully when optional integrations are unset (for example, empty DSN).
- Local console exporters allow safe dry-run style validation before remote export.
- Components are separated by concern (`logging`, `error_tracking`, `tracing`) for easier fault isolation.

## Troubleshooting / FAQ

Problem: No trace data in New Relic  
Fix: verify `NEW_RELIC_LICENSE_KEY`, OTLP endpoint, and OTLP headers.

Problem: No Sentry events appear  
Fix: confirm DSN format, environment, and egress connectivity.

Problem: Logs missing trace context  
Fix: ensure tracing is initialized and log-correlation processor is in the logging pipeline.

## Versioning / Roadmap

- Current project version: `0.1.0`.
- Near-term roadmap:
- tighten schema contract tests across observability artifacts,
- add richer integration demos and backend-specific setup guidance,
- expand benchmarking and failure-mode documentation.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
