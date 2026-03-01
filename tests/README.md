# tests

**Category:** 05_Validators  
**Status:** Production

> Full Eye-Witness test suite including unit, integration, contract, perf, stress, and snapshot checks.

## Overview

**What it does:** Validates package behavior, API compatibility, framework integration presence, snapshot schemas, and resilience characteristics.  
**What it does NOT do:** It does not perform production deployment validation or backend observability SLA checks.

## Use Cases

- Run quality gates before merge/release.
- Validate compatibility after dependency upgrades.
- Catch regressions in configuration and lifecycle logic.

## Features

- Namespace/API parity tests.
- Contract/wheel smoke tests.
- Snapshot schema checks for logs/traces/metrics.
- Stress and performance-smoke scenarios.

## Requirements

- Python 3.10+
- `pytest` and test dependencies from project `pyproject.toml`

## Quick Start

```powershell
cd <project-root>
python -m pytest tests\ -v
```

## Usage

```powershell
# Run core suite
python -m pytest tests\ -v

# Run only fast unit/integration paths
python -m pytest tests\unit tests\integration -v

# Run contract tests (opt-in)
set EW_RUN_CONTRACT=1
python -m pytest tests\test_contract_wheel.py -v
```

## Configuration

Key toggles:
- `EW_RUN_CONTRACT=1` enables wheel contract test.
- Standard pytest flags control verbosity/filtering.

## Input / Output

**Expects:** Source package, tests, and development dependencies installed.  
**Creates:** Pytest pass/fail output and optional coverage/report artifacts depending on invocation flags.

## Pipeline Position

**Fed by:** changes in `src`, `examples`, and integration helpers.  
**Feeds into:** merge/release quality decision points.

## Hardcoded Paths

Uses repository-relative test paths; no required absolute paths.

## Files

| File | Purpose |
|------|---------|
| `test_eye_witness.py` | Core behavior tests |
| `test_api_versioning.py` | Versioned API parity checks |
| `test_contract_wheel.py` | Built-wheel contract smoke test |
| `test_snapshots.py` | Golden schema snapshot validation |
| `test_stress.py` | Concurrency/high-volume stress checks |
| `test_migration_tool.py` | Migration helper checks |

## How It Works

1. Pytest discovers test modules.
2. Fixtures and isolated config paths initialize package state.
3. Assertions validate behavior and contract expectations.
4. Exit code communicates suite status.

## Example Output

```text
============================= test session starts =============================
collected 45 items
...
============================== 45 passed =====================================
```

## Safety & Reliability

- Tests are designed for local/repo execution with controlled state resets.
- Stress tests focus on runtime stability, not destructive system mutation.

## Logging & Observability

- Test output is console-native; use `-vv` for extra detail.

## Troubleshooting / FAQ

Problem: contract test is skipped  
Fix: set `EW_RUN_CONTRACT=1`.

Problem: import errors in tests  
Fix: run from repository root and ensure editable install/dependencies are present.

## Versioning / Roadmap

- Aligned with Eye-Witness `0.1.0`.
- Planned: expand snapshot coverage and benchmark threshold gating.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
