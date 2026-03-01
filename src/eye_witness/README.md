# eye_witness

**Category:** 23_Monitoring  
**Status:** Production

> Core Eye-Witness package integrating logging, error tracking, tracing, and metrics.

## Overview

**What it does:** Exposes the public API for initializing observability, emitting structured logs, tracing spans, capturing errors, and integrating framework hooks.  
**What it does NOT do:** It does not enforce backend-specific dashboards, alerting policy, or deployment setup.

## Use Cases

- Initialize full observability stack in one call.
- Emit correlated logs and traces from service code.
- Integrate Flask/FastAPI/Celery/Django observability hooks.

## Features

- Unified `init(...)` and `shutdown()` lifecycle.
- Public APIs for logging, metrics, tracing, and Sentry operations.
- Compatibility surface via `v1` namespace and legacy helpers.

## Requirements

- Python 3.10+
- Core dependencies from project `pyproject.toml` (`structlog`, `sentry-sdk`, OpenTelemetry)

## Quick Start

```python
from eye_witness import init, get_logger, shutdown

init(service_name="my-service", otel_exporter="console")
get_logger("my-service").info("startup.ok")
shutdown()
```

## Usage

```powershell
python -c "from eye_witness import init,shutdown; init(service_name='demo', otel_exporter='none', metrics_enabled=False, flush_on_exit=False, force=True); shutdown()"
```

## Configuration

Use `EyeWitnessConfig` fields or `EW_*` environment variables for service metadata, logging mode, exporter type, and sampling behavior.

## Input / Output

**Expects:** Application lifecycle calls and observability events.  
**Creates:** Structured telemetry streams (logs, spans, metrics, error events).

## Pipeline Position

**Fed by:** application code and framework integrations.  
**Feeds into:** logging backends, APM systems, and incident tooling.

## Hardcoded Paths

No hardcoded absolute paths in this package layer.

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public exports and package version |
| `_init.py` | Lifecycle orchestration |
| `_config.py` | Config model and env parsing |
| `_logging.py` | Structlog configuration |
| `_sentry.py` | Error tracking helpers |
| `_tracing.py` | Tracing provider/exporter setup |
| `_metrics.py` | Metrics provider/helpers |
| `_context.py` | Context binding/clearing |
| `integrations/` | Framework adapters |
| `internal/` | Internal helper utilities |
| `v1/` | Versioned API namespace |

## How It Works

1. Parse configuration from args/env.
2. Configure logging, tracing, metrics, and Sentry components.
3. Expose high-level helper APIs to application code.
4. Flush/shutdown providers during teardown.

## Example Output

```text
{"event":"startup.ok","service":"my-service","level":"info","trace_id":"..."}
```

## Safety & Reliability

- Explicit lifecycle controls reduce implicit global state drift.
- `force=True` supports deterministic reconfiguration in tests.

## Logging & Observability

- Package is the observability control plane for Eye-Witness consumers.

## Troubleshooting / FAQ

Problem: duplicate handlers or repeated init effects  
Fix: use `force=True` when re-initializing in tests/repl workflows.

## Versioning / Roadmap

- Current package version: `0.1.0`.
- Planned: broader integration adapters and stricter telemetry contracts.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
