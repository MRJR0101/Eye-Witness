# Eye-Witness

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Python observability library that unifies structured logging, error tracking, and
distributed tracing into a single package. One `init()` call wires up structlog,
Sentry SDK, and OpenTelemetry with sensible defaults. Every log line carries trace
context. No network dependencies required.

---

## Why Eye-Witness

Most observability setups require you to configure three separate systems that
don't talk to each other. Eye-Witness connects them at the source:

- **Structured logging** (structlog) produces JSON logs with context variables
- **Error tracking** (Sentry SDK) captures exceptions with breadcrumb trails
- **Distributed tracing** (OpenTelemetry) tracks timing, spans, and causality

The critical integration is the **log correlation bridge**: every structlog log
line automatically carries `trace_id` and `span_id` from the active
OpenTelemetry span. This means you can search your logs by trace ID and see
exactly what happened during any traced operation.

### Design Principles

- **Local-first** -- works with zero config, no DSN, no collector, no network
- **Vendor-neutral** -- OpenTelemetry exports to any backend (Jaeger, Grafana
  Tempo, Datadog, New Relic, SigNoz)
- **No-op safe** -- empty Sentry DSN disables error tracking with zero side
  effects; no OTLP endpoint falls back to console export
- **Focused** -- observability infrastructure only; never decides what your
  application does, only records what happened

---

## Quick Start

### Install

```bash
# With uv (recommended)
uv pip install -e ".[all]"

# With pip
pip install -e ".[all]"
```

### Basic Usage

```python
from eye_witness import init, shutdown
import structlog

# Wire up all three paths with one call
init(service_name="my-app")

log = structlog.get_logger()
log.info("app.started", version="1.0.0")

# Your application code here...
# Every log line now carries trace_id and span_id if a span is active

# Clean shutdown (flushes Sentry events and OpenTelemetry spans)
shutdown()
```

### With OpenTelemetry Tracing

```python
from eye_witness import init, shutdown
from opentelemetry import trace
import structlog

init(
    service_name="my-app",
    otel_exporter="console",  # or "otlp-http", "otlp-grpc"
)

log = structlog.get_logger()
tracer = trace.get_tracer("my-app")

with tracer.start_as_current_span("process_order") as span:
    span.set_attribute("order.id", "ORD-123")
    log.info("order.processing", order_id="ORD-123")
    # This log line automatically includes trace_id and span_id

    with tracer.start_as_current_span("validate"):
        log.info("order.validating")
        # Nested span -- trace_id stays the same, span_id updates

shutdown()
```

### With Sentry Error Tracking

```python
from eye_witness import init, shutdown
import sentry_sdk
import structlog

init(
    service_name="my-app",
    sentry_dsn="https://key@sentry.io/project",  # or empty string to disable
)

log = structlog.get_logger()

# Breadcrumbs record context before a crash
sentry_sdk.add_breadcrumb(
    category="db",
    message="Queried user table",
    level="info",
    data={"query_ms": 45, "rows": 10},
)

try:
    risky_operation()
except Exception as e:
    log.exception("operation.failed")       # Structured log with traceback
    sentry_sdk.capture_exception(e)         # Sends to Sentry with breadcrumbs
```

### CLI Application Pattern

```python
import atexit
from eye_witness import init, shutdown

init(service_name="my-cli-tool")
atexit.register(shutdown)  # Ensures spans and events flush before exit

# ... rest of your CLI application
```

---

## Architecture

Eye-Witness is built on three paths that integrate through a shared log
correlation bridge.

```
                    eye_witness.init()
                         |
            +------------+------------+
            |            |            |
        Path 1       Path 2       Path 3
       structlog    Sentry SDK   OpenTelemetry
            |            |            |
    JSON logging   breadcrumbs    spans + traces
    context vars   error capture  OTLP export
    6 patterns     5 categories   3 exporters
            |            |            |
            +-----+------+-----+-----+
                  |            |
          log correlation    shutdown()
          bridge injects     flushes both
          trace_id/span_id   Sentry + OTel
```

### Path 1: Structured Logging (structlog)

Six configuration patterns, automatically selected or manually chosen:

| Pattern | When To Use |
|---------|------------|
| Production stdlib JSON | Default for production; integrates with stdlib loggers |
| High-performance orjson | Maximum speed; uses orjson + BytesLoggerFactory |
| Auto-detect TTY | Pretty console in dev, JSON in production |
| Contextvars binding | Thread-safe context (request_id, job_id) |
| ProcessorFormatter bridge | Routes stdlib logs through structlog pipeline |
| Recommended pipeline | Opinionated "best of all" configuration |

### Path 2: Error Tracking (Sentry SDK)

- Five breadcrumb categories: `http`, `query`, `ui.click`, `console`, `job`
- `LoggingIntegration` with `event_level=None` -- breadcrumbs from all log
  levels, but exceptions sent manually via `capture_exception()`
- No-DSN pattern: empty string disables the SDK entirely (no network, no
  side effects)
- GlitchTip compatible: change DSN only, keep all code

### Path 3: Distributed Tracing (OpenTelemetry)

- Three exporter options: Console (dev), OTLP HTTP (port 4318), OTLP gRPC
  (port 4317)
- `BatchSpanProcessor` for production, `SimpleSpanProcessor` for dev
- Resource attributes: `service.name`, `service.version`,
  `deployment.environment`
- Vendor-neutral: works with any OTLP-compatible backend

### The Bridge: Log Correlation

The `_context.py` module provides a structlog processor that reads the current
OpenTelemetry span context and injects `trace_id` and `span_id` into every log
event:

```json
{
  "event": "order.processing",
  "order_id": "ORD-123",
  "trace_id": "0af7651916cd43dd8448eb211c80319c",
  "span_id": "b7ad6b7169203331",
  "level": "info",
  "timestamp": "2026-02-12T10:30:00.000Z"
}
```

This is the single highest-value integration: you can take any trace ID from
your tracing backend and find every log line that happened during that trace.

---

## Package Structure

```
src/eye_witness/
    __init__.py       Public API: init(), shutdown(), EyeWitnessConfig
    _config.py        EyeWitnessConfig dataclass with from_env() factory
    _init.py          Orchestrator: wires up all three paths in sequence
    _logging.py       Six structlog configuration patterns
    _sentry.py        Sentry SDK setup, LoggingIntegration, breadcrumbs
    _tracing.py       OpenTelemetry TracerProvider, exporters, processors
    _context.py       Log correlation bridge (trace_id/span_id injection)
```

Seven modules. That's it. No application helpers, no CLI decorators, no
framework integrations. Eye-Witness is infrastructure -- it records what your
application does, it never decides what your application does.

---

## Configuration

### Keyword Arguments

```python
from eye_witness import init

init(
    service_name="my-app",
    service_version="1.0.0",
    environment="production",
    log_format="json",              # "json" | "console" | "auto"
    sentry_dsn="",                  # Empty = disabled
    otel_exporter="otlp-http",      # "console" | "otlp-http" | "otlp-grpc" | "none"
    otel_endpoint="",               # Empty = default for exporter type
)
```

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `EW_SERVICE_NAME` | Service name in traces and logs | `"unknown"` |
| `EW_SERVICE_VERSION` | Service version | `"0.0.0"` |
| `EW_ENVIRONMENT` | Deployment environment | `"local"` |
| `EW_LOG_FORMAT` | Log output format | `"auto"` |
| `SENTRY_DSN` | Sentry project DSN | `""` (disabled) |
| `SENTRY_ENVIRONMENT` | Sentry environment name | `"local"` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint | (exporter default) |
| `OTEL_EXPORTER_OTLP_HEADERS` | OTLP headers (e.g., API keys) | `""` |
| `OTEL_TRACES_SAMPLER` | Sampling strategy | `"always_on"` |

### Config Object (Full Control)

```python
from eye_witness import init, EyeWitnessConfig

cfg = EyeWitnessConfig(
    service_name="my-app",
    service_version="2.0.0",
    environment="staging",
    log_format="json",
    sentry_dsn="https://key@sentry.io/1",
    otel_exporter="otlp-grpc",
    otel_endpoint="http://collector:4317",
)
init(config=cfg)
```

### Zero-Config (Env Vars Only)

```bash
export EW_SERVICE_NAME=my-app
export SENTRY_DSN=https://key@sentry.io/1
export OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318
```

```python
from eye_witness import init
init()  # Reads everything from environment
```

---

## Compatible Backends

### Error Tracking

| Backend | How To Connect |
|---------|---------------|
| Sentry | Set `SENTRY_DSN` to your Sentry project DSN |
| GlitchTip | Set `SENTRY_DSN` to your GlitchTip instance DSN |
| Disabled | Leave `SENTRY_DSN` empty |

### Tracing

| Backend | How To Connect |
|---------|---------------|
| Console (dev) | `otel_exporter="console"` |
| New Relic | OTLP HTTP to `https://otlp.nr-data.net`, api-key header |
| Jaeger | OTLP HTTP/gRPC to your Jaeger collector |
| Grafana Tempo | OTLP HTTP/gRPC to your Tempo instance |
| Datadog | OTLP to Datadog agent |
| Honeycomb | OTLP HTTP with API key header |
| SigNoz | OTLP HTTP/gRPC to SigNoz collector |

No vendor SDK needed for any backend. Pure OpenTelemetry OTLP.

---

## Testing

```bash
# Run tests
pytest -q

# With uv
uv run pytest -q
```

26 tests covering all three paths and the integration bridge.

---

## Integration with Other Projects

Eye-Witness is designed as a shared dependency. Other projects consume it
without modification:

```bash
# Install as editable dependency in another project
uv pip install -e "C:\Dev\PROJECTS\Eye-Witness[all]"
```

```python
# In your project's startup
from eye_witness import init
init(service_name="codegraphx")

# All your structlog calls now carry trace context
# All your exceptions can go to Sentry
# All your spans export to your chosen backend
```

---

## What Eye-Witness Does NOT Do

- No application-specific helpers (CLI decorators, web middleware)
- No context propagation utilities (inject/extract across services)
- No metrics collection (traces and logs only)
- No auto-instrumentation (manual instrumentation by design)
- No session replay or profiling
- No framework integrations (FastAPI, Django, Flask)

These belong in the consuming application, not in the shared infrastructure
library.

---

## Dependencies

### Core

| Package | Purpose |
|---------|---------|
| `structlog` | Structured logging with processor pipelines |
| `sentry-sdk` | Error tracking and breadcrumb management |

### Tracing (optional, installed with `[all]`)

| Package | Purpose |
|---------|---------|
| `opentelemetry-api` | Tracing API |
| `opentelemetry-sdk` | TracerProvider, processors, samplers |
| `opentelemetry-exporter-otlp-proto-http` | OTLP over HTTP |
| `opentelemetry-exporter-otlp-proto-grpc` | OTLP over gRPC |

### Performance (optional)

| Package | Purpose |
|---------|---------|
| `orjson` | Fast JSON serialization for high-performance logging |
| `rich` | Pretty console output in development |

---

## License

[MIT](LICENSE)
