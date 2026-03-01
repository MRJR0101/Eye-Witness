# v1

**Category:** 23_Monitoring  
**Status:** Production

> Stable API namespace for Eye-Witness compatibility pinning.

## Overview

**What it does:** Re-exports Eye-Witness public API under `eye_witness.v1` so consumers can pin to a versioned namespace intentionally.  
**What it does NOT do:** It does not provide an independent implementation separate from top-level package behavior.

## Use Cases

- Use explicit versioned imports in long-lived services.
- Validate API parity between top-level and v1 namespaces.
- Prepare for future major-version transitions.

## Features

- Mirrors core public functions/classes.
- Keeps import intent explicit for consumers.
- Covered by parity tests in `tests/test_api_versioning.py`.

## Requirements

- Python 3.10+
- Eye-Witness package installation

## Quick Start

```python
from eye_witness.v1 import init, get_logger, shutdown

init(service_name="my-service")
get_logger("my-service").info("v1.namespace.ok")
shutdown()
```

## Usage

```powershell
python -c "from eye_witness.v1 import init,shutdown; init(otel_exporter='none', metrics_enabled=False, flush_on_exit=False, force=True); shutdown()"
```

## Configuration

Uses the same configuration model as top-level Eye-Witness API.

## Input / Output

**Expects:** Standard Eye-Witness initialization and telemetry calls.  
**Creates:** Identical behavior/output as top-level API.

## Pipeline Position

**Fed by:** top-level package exports.  
**Feeds into:** compatibility-sensitive consumer codebases.

## Hardcoded Paths

No hardcoded filesystem paths.

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Versioned API re-export namespace |

## How It Works

1. Import symbols from top-level package.
2. Re-export them via `__all__`.
3. Consumers import from `eye_witness.v1`.

## Example Output

```text
event=v1.namespace.ok
```

## Safety & Reliability

- Reduces accidental API drift exposure by encouraging explicit versioned imports.

## Logging & Observability

- Uses identical observability pipeline as top-level package.

## Troubleshooting / FAQ

Problem: mismatch between top-level and v1 behavior  
Fix: run API parity tests and update re-export list.

## Versioning / Roadmap

- Current package version: `0.1.0`.
- Planned: preserve `v1` while introducing future `v2` namespace when needed.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
