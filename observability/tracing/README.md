# tracing

**Category:** 23_Monitoring  
**Status:** Production

> OpenTelemetry tracing components and New Relic OTLP integration helpers.

## Overview

**What it does:** Configures tracers, samplers, processors, exporters, span helpers, and log-correlation bridges for Eye-Witness tracing.  
**What it does NOT do:** It does not replace backend APM setup, collector operations, or trace retention policies.

## Use Cases

- Enable distributed tracing in Python services.
- Export OTLP traces to New Relic or compatible backends.
- Correlate logs with active trace/span IDs.

## Features

- Configurable exporter modes (`none`, `console`, `otlp-http`, `otlp-grpc`).
- Sampler controls including span-name-specific rates.
- Utility helpers for span creation and propagation support.

## Requirements

- Python 3.10+
- `opentelemetry-api`, `opentelemetry-sdk`
- Optional OTLP exporter packages for remote export

## Quick Start

```powershell
cd C:\Dev\PROJECTS\Eye-Witness
python -m observability.tracing.newrelic_demo
```

## Usage

```python
from eye_witness import init, trace_span

init(service_name="svc", otel_exporter="console")
with trace_span("operation.process"):
    pass
```

## Configuration

Main options include `otel_exporter`, `otel_endpoint`, `otel_sample_rate`, and per-span sampling map.

## Input / Output

**Expects:** Instrumented code paths and tracing configuration.  
**Creates:** Span data for console or OTLP exporters.

## Pipeline Position

**Fed by:** business operations wrapped in spans.  
**Feeds into:** tracing backend (New Relic/OTLP-compatible systems).

## Hardcoded Paths

No hardcoded filesystem paths.

## Files

| File | Purpose |
|------|---------|
| `provider.py` | Tracer provider setup |
| `sampling.py` | Sampling logic |
| `spans.py` | Span utility helpers |
| `propagation.py` | Context propagation helpers |
| `log_correlation.py` | Trace context to log bridge |
| `newrelic.py` | New Relic OTLP helper config |
| `newrelic_demo.py` | End-to-end export demo |

## How It Works

1. Build tracer provider and sampler from config.
2. Attach processor/exporter pipeline.
3. Create spans via helper APIs.
4. Inject trace context into logs for correlation.

## Example Output

```text
name=snapshot.trace trace_id=... span_id=... status=UNSET
```

## Safety & Reliability

- `otel_exporter="none"` mode allows safe local runs without network egress.
- Console exporter path is deterministic for debugging.

## Logging & Observability

- Trace IDs are propagated into logs when logging bridge is enabled.

## Troubleshooting / FAQ

Problem: No traces in backend  
Fix: Verify exporter type, endpoint, headers, and network egress.

## Versioning / Roadmap

- Aligned with Eye-Witness `0.1.0`.
- Planned: richer semantic conventions and advanced span attributes.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
