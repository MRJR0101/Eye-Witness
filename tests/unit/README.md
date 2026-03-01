# unit

**Category:** 05_Validators  
**Status:** Production

> Focused unit tests for API parity and internal helper behavior.

## Overview

**What it does:** Verifies small-scope behavior including top-level vs v1 export parity and internal utility function correctness.  
**What it does NOT do:** It does not exercise full integration paths or packaging contracts.

## Use Cases

- Fast feedback during active development.
- Validate stable API shape and helper semantics.
- Catch low-level regression before broader suites run.

## Features

- API parity assertion coverage.
- Internal helper deterministic behavior checks.
- Fast execution suitable for pre-commit loops.

## Requirements

- Python 3.10+
- `pytest`

## Quick Start

```powershell
cd <project-root>
python -m pytest tests\unit -v
```

## Usage

```powershell
python -m pytest tests\unit\test_api_parity.py tests\unit\test_internal.py -v
```

## Configuration

No special env vars required for this suite.

## Input / Output

**Expects:** Installed/available Eye-Witness module imports.  
**Creates:** Pass/fail result for unit-level API and helper contracts.

## Pipeline Position

**Fed by:** code changes in public exports and internal utilities.  
**Feeds into:** early-stage correctness signal in CI and local runs.

## Hardcoded Paths

No hardcoded absolute paths required.

## Files

| File | Purpose |
|------|---------|
| `test_api_parity.py` | Top-level vs v1 export parity |
| `test_internal.py` | Internal helper function behavior |

## How It Works

1. Import target symbols/functions.
2. Execute deterministic assertions.
3. Fail on contract drift.

## Example Output

```text
tests/unit/test_api_parity.py::test_top_level_and_v1_api_parity PASSED
tests/unit/test_internal.py::test_clamp_rate_bounds PASSED
```

## Safety & Reliability

- Read-only assertions with no external service dependency.

## Logging & Observability

- Pytest output is sufficient for this suite.

## Troubleshooting / FAQ

Problem: parity test fails after export change  
Fix: update top-level and v1 export lists together and adjust tests intentionally.

## Versioning / Roadmap

- Aligned with Eye-Witness `0.1.0`.
- Planned: broaden internal helper edge-case coverage.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
