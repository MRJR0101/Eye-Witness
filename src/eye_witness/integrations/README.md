# integrations

**Category:** 23_Monitoring  
**Status:** Production

> Framework integration adapters for FastAPI, Flask, Celery, and Django.

## Overview

**What it does:** Exposes adapter functions/classes that hook Eye-Witness observability into framework lifecycle events.  
**What it does NOT do:** It does not manage framework app configuration, dependency injection, or domain logic.

## Use Cases

- Add tracing/logging hooks to FastAPI and Flask apps.
- Connect Celery worker lifecycle signals.
- Install Django middleware for request context propagation.

## Features

- `install_fastapi(app)` adapter.
- `install_flask(app)` adapter.
- `install_celery(...)` signal integration helper.
- `EyeWitnessDjangoMiddleware` class for Django stacks.

## Requirements

- Python 3.10+
- Eye-Witness core package
- Corresponding framework runtime in target project

## Quick Start

```python
from eye_witness.integrations import install_fastapi
install_fastapi(app)
```

## Usage

```python
from eye_witness.integrations import install_flask, install_celery

install_flask(app)
install_celery()
```

## Configuration

Adapters rely on core `init(...)` configuration; call `init` before installing adapters.

## Input / Output

**Expects:** Framework app objects or worker signal modules.  
**Creates:** Instrumentation hooks and middleware behavior in host framework lifecycle.

## Pipeline Position

**Fed by:** `eye_witness.init(...)` and host framework bootstrap.  
**Feeds into:** framework-level telemetry emission.

## Hardcoded Paths

No hardcoded filesystem paths.

## Files

| File | Purpose |
|------|---------|
| `fastapi.py` | FastAPI install helper |
| `flask.py` | Flask install helper |
| `celery.py` | Celery install helper |
| `django.py` | Django middleware class |
| `__init__.py` | Public integration exports |

## How It Works

1. Import desired integration helper.
2. Initialize Eye-Witness core.
3. Install adapter into framework startup path.
4. Framework emits telemetry through core pipeline.

## Example Output

```text
event=request.started framework=fastapi
event=request.completed framework=fastapi
```

## Safety & Reliability

- Integration logic is additive and isolated.
- Easy rollback by removing adapter call/middleware entry.

## Logging & Observability

- Adapters standardize framework telemetry shape and context propagation.

## Troubleshooting / FAQ

Problem: adapter has no visible effect  
Fix: verify `init(...)` is called before adapter install and requests/tasks are actually executed.

## Versioning / Roadmap

- Aligned with Eye-Witness `0.1.0`.
- Planned: additional adapters for ASGI/WSGI ecosystems.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
