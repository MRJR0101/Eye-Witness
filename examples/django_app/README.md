# django_app

**Category:** 22_DevEnvironment  
**Status:** Production

> Django middleware snippet for Eye-Witness integration.

## Overview

**What it does:** Provides the middleware entry for Django settings so Eye-Witness context and tracing flow through request handling.  
**What it does NOT do:** It does not configure Django logging, settings modules, or startup lifecycle by itself.

## Use Cases

- Add Eye-Witness middleware to a Django service.
- Validate middleware import contract in tests.
- Share a canonical settings snippet for teams.

## Features

- Single middleware string for copy/paste into Django settings.
- Uses packaged integration path from `eye_witness.integrations.django`.
- Minimal and framework-native usage.

## Requirements

- Python 3.10+
- `eye_witness`
- Django application using middleware stack

## Quick Start

```python
from examples.django_app.settings_snippet import MIDDLEWARE_SNIPPET
MIDDLEWARE = list(MIDDLEWARE) + MIDDLEWARE_SNIPPET
```

## Usage

```powershell
python .\examples\django_app\settings_snippet.py
```

## Configuration

Add middleware entry to your Django `MIDDLEWARE` list after core middleware and before app-specific handlers where context is needed.

## Input / Output

**Expects:** Django project settings module.  
**Creates:** Middleware registration enabling Eye-Witness request context propagation.

## Pipeline Position

**Fed by:** `eye_witness.integrations.django` middleware class.  
**Feeds into:** Django request lifecycle logging and tracing.

## Hardcoded Paths

No hardcoded filesystem paths.

## Files

| File | Purpose |
|------|---------|
| `settings_snippet.py` | Django middleware snippet |

## How It Works

1. Import middleware path constant.
2. Append it to Django `MIDDLEWARE`.
3. Request lifecycle includes Eye-Witness middleware execution.

## Example Output

```text
service=my-django-app event=request.started path=/health
service=my-django-app event=request.completed status=200
```

## Safety & Reliability

- Non-destructive; only affects middleware order when applied.
- Easy to revert by removing middleware entry.

## Logging & Observability

- Middleware enables consistent request context for logs and traces.

## Troubleshooting / FAQ

Problem: `ModuleNotFoundError` for middleware path  
Fix: Confirm package installation and Django `PYTHONPATH` configuration.

## Versioning / Roadmap

- Tracks Eye-Witness version `0.1.0`.
- Planned: include full Django settings and ASGI startup sample.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
