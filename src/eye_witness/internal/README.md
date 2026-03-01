# internal

**Category:** 23_Monitoring  
**Status:** Production

> Internal utility helpers used by Eye-Witness implementation.

## Overview

**What it does:** Contains small internal helpers for lifecycle state snapshots, stable schema keys, safe JSON serialization, and numeric clamp behavior.  
**What it does NOT do:** It does not provide stable public API guarantees for external consumers.

## Use Cases

- Support deterministic behavior across package modules.
- Centralize small reusable internal functions.
- Provide testable primitives for internal contracts.

## Features

- `state_snapshot()` for lifecycle inspection.
- `stable_keys()` for deterministic schema key ordering.
- `safe_json_dumps()` for robust JSON serialization.
- `clamp_rate()` utility for bounded sampling values.

## Requirements

- Python 3.10+
- Eye-Witness package source tree

## Quick Start

```python
from eye_witness.internal import clamp_rate, stable_keys
print(clamp_rate(1.5))
print(stable_keys({"b": 1, "a": 2}))
```

## Usage

```powershell
python -c "from eye_witness.internal import safe_json_dumps; print(safe_json_dumps({'ok': True}))"
```

## Configuration

No external configuration; functions are pure or near-pure helpers.

## Input / Output

**Expects:** In-memory Python values.  
**Creates:** Deterministic transformed values used by higher-level modules.

## Pipeline Position

**Fed by:** core modules in `src/eye_witness`.  
**Feeds into:** config validation, logging/tracing schema consistency, and lifecycle diagnostics.

## Hardcoded Paths

No filesystem paths are hardcoded here.

## Files

| File | Purpose |
|------|---------|
| `lifecycle.py` | Initialization state snapshots |
| `schema.py` | Stable key ordering helpers |
| `serializers.py` | Safe JSON serialization |
| `util.py` | General utility helpers |
| `__init__.py` | Internal export surface |

## How It Works

1. Core modules call internal helper functions.
2. Helpers return normalized/validated values.
3. Higher-level modules use outputs for consistent behavior.

## Example Output

```text
0.0
["a", "b"]
```

## Safety & Reliability

- Small helper surface lowers risk and eases testing.
- Used directly by unit tests to guard internal contracts.

## Logging & Observability

- Internal helpers do not emit logs by default; observability happens at caller layer.

## Troubleshooting / FAQ

Problem: importing `eye_witness.internal` fails  
Fix: ensure project is installed or run commands from repository root.

## Versioning / Roadmap

- Follows Eye-Witness package versioning.
- Planned: additional normalization helpers as config surface expands.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
