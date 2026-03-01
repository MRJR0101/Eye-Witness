# contract

**Category:** 05_Validators  
**Status:** Production

> Contract tests that verify installed wheel behavior from a clean virtual environment.

## Overview

**What it does:** Builds a wheel, installs it into a fresh temporary venv, and validates that core public APIs run correctly.  
**What it does NOT do:** It does not benchmark performance or run full end-to-end application scenarios.

## Use Cases

- Validate packaging correctness before release.
- Catch missing runtime dependencies in wheel metadata.
- Ensure compatibility namespace imports continue to work.

## Features

- Clean-environment install path.
- API smoke validation against built artifact.
- Opt-in execution to control CI cost.

## Requirements

- Python 3.10+
- `build`, `pytest`
- `EW_RUN_CONTRACT=1` to execute

## Quick Start

```powershell
cd <project-root>
set EW_RUN_CONTRACT=1
python -m pytest tests\contract\test_api_contract.py tests\test_contract_wheel.py -v
```

## Usage

```powershell
python -m pytest tests\contract -v
```

## Configuration

`EW_RUN_CONTRACT` gates execution of expensive wheel contract tests.

## Input / Output

**Expects:** Buildable project and local Python venv creation capability.  
**Creates:** Temporary wheel artifacts and validation process output.

## Pipeline Position

**Fed by:** release-candidate code state.  
**Feeds into:** publish/no-publish decision.

## Hardcoded Paths

Temporary directories are generated at runtime; no fixed absolute path required.

## Files

| File | Purpose |
|------|---------|
| `test_api_contract.py` | v1 import contract smoke check |

## How It Works

1. Build wheel artifact.
2. Install wheel in clean venv.
3. Execute import/use smoke script.
4. Fail if contract behavior diverges.

## Example Output

```text
tests/contract/test_api_contract.py::test_v1_import_contract_smoke PASSED
```

## Safety & Reliability

- Runs in isolated temporary environment.
- Does not modify installed global packages.

## Logging & Observability

- Pytest output provides install and execution status.

## Troubleshooting / FAQ

Problem: test skipped unexpectedly  
Fix: set `EW_RUN_CONTRACT=1` in current shell.

## Versioning / Roadmap

- Aligned with Eye-Witness `0.1.0`.
- Planned: expand wheel contract to cover more top-level APIs.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
