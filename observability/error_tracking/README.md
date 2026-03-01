# error_tracking

**Category:** 23_Monitoring  
**Status:** Production

> Sentry-focused error tracking components for Eye-Witness.

## Overview

**What it does:** Provides Sentry initialization, exception/message capture, breadcrumbs, tags, and context helpers used by Eye-Witness.  
**What it does NOT do:** It does not replace application-specific alert routing, issue triage, or backend incident policy.

## Use Cases

- Enable centralized exception reporting in CLI/services.
- Record breadcrumb trails before failures.
- Attach structured context and user metadata to events.

## Features

- Configurable Sentry startup and no-DSN safety behavior.
- Helper APIs for `capture_exception`, `capture_message`, and breadcrumbs.
- Context/tag/user enrichment for searchable incidents.

## Requirements

- Python 3.10+
- `sentry-sdk`
- Eye-Witness config values for DSN and environment

## Quick Start

```powershell
cd C:\Dev\PROJECTS\Eye-Witness
python -m observability.error_tracking.demo
```

## Usage

```python
from eye_witness import init, add_breadcrumb, capture_exception

init(service_name="svc", sentry_dsn="https://...", otel_exporter="none")
add_breadcrumb(category="query", message="SELECT ...")
```

## Configuration

Primary settings include `sentry_dsn`, `environment`, and trace sample options from Eye-Witness config.

## Input / Output

**Expects:** Runtime exceptions/events and optional DSN configuration.  
**Creates:** Sentry events with tags, breadcrumbs, and contextual payload.

## Pipeline Position

**Fed by:** app errors and breadcrumb-producing code paths.  
**Feeds into:** Sentry/GlitchTip incident visibility and debugging workflows.

## Hardcoded Paths

No hardcoded filesystem paths.

## Files

| File | Purpose |
|------|---------|
| `config.py` | Error tracking initialization settings |
| `breadcrumbs.py` | Breadcrumb helper functions |
| `context.py` | Tag/context/user helper functions |
| `cli.py` | CLI lifecycle safety helpers |
| `demo.py` | Demonstration entrypoint |

## How It Works

1. Initialize Sentry early in process startup.
2. Add breadcrumbs/context during important events.
3. Capture exceptions/messages with rich metadata.
4. Flush and shutdown cleanly on exit.

## Example Output

```text
event=caught_exception sentry_event_id=...
event=breadcrumb.added category=query
```

## Safety & Reliability

- Empty DSN path is handled safely (no hard failure).
- Explicit flush path minimizes dropped events on shutdown.

## Logging & Observability

- Error tracking complements logs and traces; it is not a substitute for either.

## Troubleshooting / FAQ

Problem: No events arrive in Sentry  
Fix: Verify DSN, network egress, and environment-level filtering.

## Versioning / Roadmap

- Aligned with Eye-Witness `0.1.0`.
- Planned: expanded event sampling controls and richer CLI wrappers.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
