# flask_app

**Category:** 22_DevEnvironment  
**Status:** Production

> Minimal Flask wiring example for Eye-Witness.

## Overview

**What it does:** Demonstrates how to initialize Eye-Witness and install Flask integration hooks through `configure_app(app)`.  
**What it does NOT do:** It does not include Flask route definitions, config management, or deployment plumbing.

## Use Cases

- Add observability to an existing Flask app with minimal changes.
- Validate Flask adapter behavior in integration tests.
- Use as a baseline for internal service templates.

## Features

- Single setup function for observability bootstrapping.
- Explicit `service_name` assignment.
- `install_flask(app)` adapter installation in one line.

## Requirements

- Python 3.10+
- `eye_witness`
- `flask` for runtime use

## Quick Start

```python
from flask import Flask
from examples.flask_app.app import configure_app

app = configure_app(Flask(__name__))
```

## Usage

```powershell
python .\examples\flask_app\app.py
```

## Configuration

Edit `init(...)` parameters in `app.py` for service naming and exporter behavior.

## Input / Output

**Expects:** A Flask app object.  
**Creates:** Instrumented Flask app emitting Eye-Witness telemetry.

## Pipeline Position

**Fed by:** Eye-Witness core package and Flask integration adapter.  
**Feeds into:** request telemetry and event logs in your configured backend.

## Hardcoded Paths

Fully parameterized; no hardcoded filesystem paths.

## Files

| File | Purpose |
|------|---------|
| `app.py` | Flask integration setup snippet |

## How It Works

1. Initialize Eye-Witness.
2. Attach Flask integration hooks.
3. Return configured app.

## Example Output

```text
service=flask-example event=request.started
service=flask-example event=request.completed
```

## Safety & Reliability

- Uses controlled startup-only initialization path.
- No filesystem writes in example itself.

## Logging & Observability

- Emits logs/traces through standard Eye-Witness exporters.

## Troubleshooting / FAQ

Problem: Flask integration not active  
Fix: Confirm `install_flask(app)` is called after `init(...)`.

## Versioning / Roadmap

- Aligned with Eye-Witness `0.1.0`.
- Planned: add blueprint-aware Flask example.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
