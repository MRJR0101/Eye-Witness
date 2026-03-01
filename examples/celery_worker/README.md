# celery_worker

**Category:** 22_DevEnvironment  
**Status:** Production

> Celery worker bootstrap example for Eye-Witness integration.

## Overview

**What it does:** Shows how to initialize Eye-Witness and install Celery integration hooks in worker startup code.  
**What it does NOT do:** It does not define Celery tasks, broker settings, or production worker process configs.

## Use Cases

- Add observability hooks to Celery worker lifecycle.
- Validate event and trace propagation in async task execution.
- Provide a minimal worker setup reference.

## Features

- Startup-level `init(...)` with explicit service naming.
- `install_celery()` integration for Celery signal hooks.
- Small reusable function (`configure_worker`) for worker entrypoints.

## Requirements

- Python 3.10+
- `eye_witness`
- Celery runtime in target service

## Quick Start

```python
from examples.celery_worker.worker import configure_worker
configure_worker()
```

## Usage

```powershell
python .\examples\celery_worker\worker.py
```

## Configuration

Tune `init(...)` parameters (service name, exporters, Sentry DSN) to match your worker environment.

## Input / Output

**Expects:** Celery app runtime and worker startup path.  
**Creates:** Worker-level observability hooks for logs/traces/errors.

## Pipeline Position

**Fed by:** Eye-Witness core + Celery integration module.  
**Feeds into:** asynchronous task observability stream.

## Hardcoded Paths

No hardcoded filesystem paths.

## Files

| File | Purpose |
|------|---------|
| `worker.py` | Celery integration bootstrap snippet |

## How It Works

1. Initialize Eye-Witness for worker process.
2. Register Celery integration callbacks.
3. Continue normal Celery task execution with telemetry enabled.

## Example Output

```text
service=celery-example event=task.started task=send_email
service=celery-example event=task.completed task=send_email
```

## Safety & Reliability

- Setup is additive and reversible.
- Keeps integration code localized to worker bootstrap path.

## Logging & Observability

- Captures worker events through Eye-Witness logging/tracing/error stack.

## Troubleshooting / FAQ

Problem: No Celery events appear in telemetry  
Fix: Ensure `configure_worker()` runs in worker startup path before task execution.

## Versioning / Roadmap

- Aligned with Eye-Witness `0.1.0`.
- Planned: add task context propagation and retry diagnostics example.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
