# Eye-Witness Project Handoff Brief

## Purpose

This document provides context for continuing work on or integrating with the Eye-Witness project. Use it to bring a new conversation up to speed.

---

## What Eye-Witness Is

Eye-Witness is a Python observability library that unifies three capabilities into a single cohesive package:

1. **Structured logging** via structlog (6 configuration patterns)
2. **Error tracking** via Sentry SDK (breadcrumb management across 5 categories)
3. **Distributed tracing** via OpenTelemetry (Console, OTLP HTTP, and gRPC exporters)

The critical integration feature is a **log correlation bridge** that injects trace_id and span_id from OpenTelemetry spans into structlog JSON output. This means every log line carries structured fields, contextvars, and trace correlation data simultaneously.

## Design Principles

- **Local-first**: Works without network dependencies. No DSN = Sentry is a no-op. No OTLP endpoint = tracing exports to console only.
- **Infrastructure, not application**: Eye-Witness records what happens. It never decides what happens. It should never contain application-specific logic.
- **Single responsibility**: The library provides observability plumbing. Orchestration, workflow control, and application logic belong in consuming projects.
- **No scope creep**: The project was explicitly scoped to 7 core modules. Proposed additions (context propagation helpers, CLI command decorators, span events helpers) were evaluated and rejected to keep the project focused.
- **Vendor neutral**: OpenTelemetry provides the abstraction layer. Backends (New Relic, SigNoz, Jaeger, Grafana Tempo, Datadog) are swappable by changing environment variables.

## Project Status: COMPLETE

- 7 core source modules implemented
- 26 passing tests
- Full integration demo runs successfully
- All three paths (structlog, Sentry, OpenTelemetry) work independently and together
- Deployed and verified on Windows 11 Pro development environment

## Location

```
C:\Dev\PROJECTS\Eye-Witness\
```

All consolidated projects live under `C:\Dev\PROJECTS\`.

## Package Structure

```
Eye-Witness\
    pyproject.toml
    src\
        eye_witness\
            __init__.py
            _config.py
            _init.py
            _logging.py        # 6 structlog configuration patterns
            _sentry.py         # Sentry SDK + breadcrumb management
            _tracing.py        # OpenTelemetry setup + exporters
            _context.py        # Log correlation bridge (trace_id/span_id injection)
    tests\
        test_eye_witness.py
    examples\
        cli_demo.py
```

## The 7 Core Modules Cover

### Path 1 - Structured Logging (_logging.py)
- Production stdlib integration (JSON output)
- High-performance config with orjson
- Auto-detect TTY (dev = pretty console, prod = JSON)
- Contextvars for thread-safe context binding
- ProcessorFormatter bridge (stdlib logs flow through structlog pipeline)
- Recommended processor pipeline order

### Path 2 - Error Tracking (_sentry.py)
- Sentry SDK init with no-DSN safety (empty DSN = disabled)
- LoggingIntegration with event_level=None (breadcrumbs from logs, manual event control)
- Breadcrumb management across 5 categories (http, query, ui, console, job)
- Context attachment (tags for searchable, context for structured debug data)
- Explicit exception capture pattern
- GlitchTip compatible (change DSN only)

### Path 3 - Distributed Tracing (_tracing.py + _context.py)
- TracerProvider setup with Resource attributes
- Console, OTLP HTTP (port 4318), and gRPC (port 4317) exporters
- BatchSpanProcessor for production, SimpleSpanProcessor for dev
- Manual span creation with attributes and error status
- Log correlation bridge: structlog processor injects trace_id/span_id into every log line
- Provider shutdown for CLI exit (ensures spans flush)

## How Other Projects Consume Eye-Witness

Any project under `C:\Dev\PROJECTS\` can add Eye-Witness as a local editable dependency:

```powershell
uv pip install -e "C:\Dev\PROJECTS\Eye-Witness"
```

Or with all optional dependencies:

```powershell
uv pip install -e "C:\Dev\PROJECTS\Eye-Witness[all]"
```

The consuming project imports eye_witness, initializes it with a service name, and gets structured logging + error tracking + trace correlation without knowing anything about structlog, sentry-sdk, or OpenTelemetry directly.

## What Eye-Witness Should NEVER Include

- Application-specific breadcrumb categories or hardcoded service names
- Orchestration or workflow control logic
- Auto-instrumentation for third-party libraries (requests, httpx, etc.)
- Web framework integrations (FastAPI, Flask) -- this is CLI-focused
- Metrics collection (OpenTelemetry metrics API)
- Session replay or profiling features
- Any UI or dashboard components
- Context propagation helpers, CLI command decorators, or span events helpers

## What Could Still Be Added (If Needed)

- A thin `eye_witness.init(service_name="my-app")` convenience function that wires up all three paths with sensible defaults (one-liner setup for consuming projects)
- A `shutdown()` function that handles both `sentry_sdk.flush()` and `TracerProvider.shutdown()` in one call for CLI exit handlers
- Environment-variable-driven configuration layer for toggling local-only vs remote export modes

## Consolidation Context

MR has multiple projects being consolidated under `C:\Dev\PROJECTS\`. Eye-Witness is the first "finished brick" -- the shared observability infrastructure. There are approximately 4 orchestrator-type projects that need to be evaluated for overlap and potentially consolidated. Eye-Witness should be a dependency of those orchestrators, not embedded in them.

The next major decision is understanding what each orchestrator does, where they overlap, and whether they collapse into one or stay as specialized tools that all share Eye-Witness as their observability layer.

## Development Environment

- Windows 11 Pro, username mike_
- PowerShell 7.5.4 or Python only
- Package management via uv
- Plain UTF-8 encoding only, no Unicode symbols or non-ASCII characters in code or output
- All file operations via Desktop Commander (no bash_tool or Linux container)
- Never delete files without explicit permission
- Present plan and wait for approval before executing multi-step work

## Key Reference Documents

The project was built from three reference documents containing best practices from official documentation:

1. **path1-structlog-reference.md** - structlog configuration patterns, processor pipeline order, contextvars, ProcessorFormatter bridge
2. **path2-sentry-sdk-reference.md** - Sentry SDK init options, breadcrumbs, context/tags/user, CLI patterns, GlitchTip compatibility
3. **path3-opentelemetry-reference.md** - TracerProvider setup, exporters, sampling, manual instrumentation, log correlation, context propagation

These documents are available in the Eye-Witness Claude Project if needed for reference.
