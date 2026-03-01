# fastapi_app

**Category:** 22_DevEnvironment  
**Status:** Production

> Minimal FastAPI wiring example for Eye-Witness.

## Overview

**What it does:** Shows how to initialize Eye-Witness and attach FastAPI integration hooks in one function (`create_app`).  
**What it does NOT do:** It does not define routes, persistence, or production deployment settings.

## Use Cases

- Bootstrap observability in a new FastAPI service.
- Validate FastAPI middleware/trace instrumentation during upgrades.
- Provide a copy-ready pattern for team services.

## Features

- Centralized `init(...)` call for logging/tracing/error tracking.
- `install_fastapi(app)` adapter install in a single place.
- Minimal function suitable for app factory patterns.

## Requirements

- Python 3.10+
- `eye_witness`
- `fastapi` for real app runtime

## Quick Start

```python
from fastapi import FastAPI
from examples.fastapi_app.main import create_app

app = create_app(FastAPI())
```

## Usage

```powershell
# From repository root, inspect/execute module
python .\examples\fastapi_app\main.py
```

## Configuration

Adjust `service_name` and initialization options in `main.py` to match your service.

## Input / Output

**Expects:** A FastAPI app instance passed to `create_app(app)`.  
**Creates:** Configured app with Eye-Witness instrumentation and structured telemetry output.

## Pipeline Position

**Fed by:** `src/eye_witness` core and FastAPI adapter.  
**Feeds into:** FastAPI runtime observability data stream.

## Hardcoded Paths

Fully parameterized; no absolute paths.

## Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI integration entry snippet |

## How It Works

1. Call `init(...)` with service metadata.
2. Install FastAPI integration hooks.
3. Return the instrumented app object.

## Example Output

```text
service=fastapi-example level=info event=request.started
service=fastapi-example level=info event=request.completed
```

## Safety & Reliability

- Initialization is explicit and local to app startup path.
- Uses same safety behavior as core Eye-Witness (`flush_on_exit=False` in example).

## Logging & Observability

- Logs, traces, and optional Sentry events are emitted through Eye-Witness pipeline.

## Troubleshooting / FAQ

Problem: `install_fastapi` import fails  
Fix: Ensure `eye_witness` package is installed and import path is correct.

## Versioning / Roadmap

- Tracks Eye-Witness package version `0.1.0`.
- Future: include request/response enrichment example.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
