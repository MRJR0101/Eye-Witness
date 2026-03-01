# functions

**Category:** 09_Loggers  
**Status:** Production

> Structlog demonstration module covering production and performance patterns.

## Overview

**What it does:** Runs `structlog_demo.py`, which walks through six logging patterns: stdlib bridge, high-performance JSON, environment auto-detection, contextvars usage, formatter bridging, and processor ordering.  
**What it does NOT do:** It does not initialize Sentry/OTel end-to-end or replace the packaged `eye_witness` API.

## Use Cases

- Benchmark and compare structlog configuration approaches.
- Validate processor behavior and output format changes.
- Train contributors on supported logging patterns.

## Features

- Multiple runnable demos in one script.
- Includes context-binding and exception-formatting examples.
- Shows TTY vs JSON mode behavior.

## Requirements

- Python 3.10+
- `structlog`
- Optional `orjson` for high-performance mode

## Quick Start

```powershell
cd <project-root>\functions
python .\structlog_demo.py
```

## Usage

```powershell
# Run full walkthrough
python .\structlog_demo.py

# Optional: install fast serializer for perf branch
python -m pip install orjson
```

## Configuration

`structlog_demo.py` configures logging inline for each demo section. No external config file is required.

## Input / Output

**Expects:** Python runtime with structlog installed.  
**Creates:** Console output showing JSON events, formatted logs, and exception traces.

## Pipeline Position

**Fed by:** local developer workflow and logging design changes.  
**Feeds into:** `src/eye_witness/_logging.py` implementation decisions.

## Hardcoded Paths

No hardcoded filesystem paths.

## Files

| File | Purpose |
|------|---------|
| `structlog_demo.py` | Multi-pattern logging demonstration |
| `requirements-structlog.txt` | Optional dependency reference |

## How It Works

1. Reset structlog and stdlib logging between scenarios.
2. Configure processors for each target pattern.
3. Emit representative events and errors.
4. Print output so behavior can be compared quickly.

## Example Output

```text
======================================================================
  1. Production-Ready JSON Configuration (stdlib integration)
======================================================================
{"event":"production_config_active","feature":"CallsiteParameterAdder",...}
```

## Safety & Reliability

- Demo-only behavior; does not mutate project files.
- Failures are local to script execution and easy to reproduce.

## Logging & Observability

- Script output itself is the observability artifact.
- Useful for validating formatting and redaction before production rollout.

## Troubleshooting / FAQ

Problem: `orjson` demo is skipped  
Fix: Install `orjson` in current environment.

Problem: Output format differs from expectations  
Fix: Check terminal TTY mode and selected demo branch.

## Versioning / Roadmap

- Aligned with Eye-Witness `0.1.0`.
- Planned: add side-by-side benchmark timing output per demo path.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
