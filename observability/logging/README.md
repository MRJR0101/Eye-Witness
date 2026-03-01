# logging

**Category:** 23_Monitoring  
**Status:** Production

> Structured logging pipeline implementation for Eye-Witness.

## Overview

**What it does:** Implements logging configuration, processors, redaction, service metadata injection, stdlib bridge integration, and trace-context enrichment.  
**What it does NOT do:** It does not provide external log shipping infrastructure or storage retention policy.

## Use Cases

- Enable JSON structured logs for services and workers.
- Bridge stdlib logging and structlog in mixed codebases.
- Enforce sensitive-field redaction in emitted events.

## Features

- Configurable renderer selection (`json`, `console`, `auto`).
- Processor pipeline with trace context and service metadata.
- Optional `orjson`/bytes logger path for high-throughput scenarios.

## Requirements

- Python 3.10+
- `structlog`
- Eye-Witness config object

## Quick Start

```powershell
cd C:\Dev\PROJECTS\Eye-Witness
python -m observability.logging.demo
```

## Usage

```python
from eye_witness import init, get_logger

init(service_name="svc", log_format="json")
get_logger("svc.main").info("app.started")
```

## Configuration

Key options include `log_level`, `log_format`, `log_redact_keys`, `log_use_orjson`, and stdlib bridge behavior.

## Input / Output

**Expects:** Eye-Witness config and application logging calls.  
**Creates:** Structured log events to stdout/stderr with optional trace correlation fields.

## Pipeline Position

**Fed by:** application events and library log records.  
**Feeds into:** console output, container log drivers, and external log ingestion stacks.

## Hardcoded Paths

No hardcoded filesystem paths.

## Files

| File | Purpose |
|------|---------|
| `config.py` | Logging configuration helpers |
| `processors.py` | Custom processors including trace context |
| `demo.py` | Logging behavior demonstration |

## How It Works

1. Build processor pipeline from config.
2. Configure structlog and optional stdlib bridge.
3. Redact sensitive keys before rendering.
4. Emit structured event payloads.

## Example Output

```text
{"event":"app.started","service":"svc","level":"info","trace_id":"..."}
```

## Safety & Reliability

- Redaction prevents accidental secret leakage in configured fields.
- Logging setup is deterministic and idempotent with explicit init path.

## Logging & Observability

- This module is the core logging observability layer for the project.

## Troubleshooting / FAQ

Problem: Logs are not JSON in production  
Fix: Set `log_format="json"` or verify auto-detection behavior for non-TTY runtime.

## Versioning / Roadmap

- Aligned with Eye-Witness `0.1.0`.
- Planned: additional processor hooks and schema contract tests.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
