# examples

**Category:** 22_DevEnvironment  
**Status:** Production

> Runnable integration examples for Eye-Witness API and framework adapters.

## Overview

**What it does:** Provides minimal examples showing how to initialize Eye-Witness and connect it to CLI, FastAPI, Flask, Django, and Celery workflows.  
**What it does NOT do:** It does not include production app scaffolding, deployment config, or framework business logic.

## Use Cases

- Verify installation quickly with known-good snippets.
- Copy baseline integration code into an existing service.
- Validate framework adapters during upgrade testing.

## Features

- CLI demonstration of logging + tracing + Sentry flow.
- Framework-specific starter files under subfolders.
- Small scripts designed for copy/paste onboarding.

## Requirements

- Python 3.10+
- `eye_witness` installed in environment
- Optional framework packages depending on example target

## Quick Start

```powershell
cd <project-root>
python -m examples.cli_demo
python -m examples.integrations_demo
```

## Usage

```powershell
# FastAPI snippet source
python .\examples\fastapi_app\main.py

# Flask snippet source
python .\examples\flask_app\app.py
```

## Configuration

Examples honor Eye-Witness env vars, including `EW_SERVICE_NAME`, `EW_SENTRY_DSN`, and `EW_OTEL_EXPORTER`.

## Input / Output

**Expects:** Valid Eye-Witness install and optional framework app objects.  
**Creates:** Console logs/traces/events demonstrating integration behavior.

## Pipeline Position

**Fed by:** core `src/eye_witness` package and framework adapter modules.  
**Feeds into:** application integration, onboarding docs, and smoke validation.

## Hardcoded Paths

Repository-relative imports are used; no absolute filesystem paths required.

## Files

| File | Purpose |
|------|---------|
| `cli_demo.py` | End-to-end CLI observability demo |
| `integrations_demo.py` | Framework integration helper demo |
| `fastapi_app/main.py` | FastAPI integration snippet |
| `flask_app/app.py` | Flask integration snippet |
| `django_app/settings_snippet.py` | Django middleware snippet |
| `celery_worker/worker.py` | Celery worker integration snippet |

## How It Works

1. Initialize Eye-Witness with service metadata.
2. Install framework hooks where applicable.
3. Emit logs/spans/errors from example flow.
4. Shut down providers cleanly.

## Example Output

```text
demo.started
order.processing_started
order.completed
demo.finished
```

## Safety & Reliability

- Examples are non-destructive and local-only by default.
- Network exporters can be disabled with `otel_exporter="none"` or `console`.
- Sentry is optional and disabled when DSN is empty.

## Logging & Observability

- Output is designed to be visible in terminal immediately.
- Tracing/log correlation fields appear when tracing is enabled.

## Troubleshooting / FAQ

Problem: Import errors for framework module  
Fix: Install the relevant framework dependency (`fastapi`, `flask`, etc.).

Problem: No Sentry events appear  
Fix: Set a valid DSN and confirm egress connectivity.

## Versioning / Roadmap

- Aligned with Eye-Witness version `0.1.0`.
- Planned: add async worker and WSGI/ASGI production snippets.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
