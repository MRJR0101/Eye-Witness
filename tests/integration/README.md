# integration

**Category:** 05_Validators  
**Status:** Production

> Integration-level tests for example framework wiring and cross-module behavior.

## Overview

**What it does:** Verifies framework example files and integration paths remain present and usable as part of repository contracts.  
**What it does NOT do:** It does not run full framework servers or production traffic simulations.

## Use Cases

- Guard against accidental removal/rename of integration examples.
- Validate repository structure required by docs/onboarding flows.
- Provide a fast integration sanity signal in CI.

## Features

- Lightweight file-presence and integration checks.
- Fast runtime suitable for frequent CI runs.
- Complements unit tests with cross-folder validation.

## Requirements

- Python 3.10+
- `pytest`

## Quick Start

```powershell
cd <project-root>
python -m pytest tests\integration -v
```

## Usage

```powershell
python -m pytest tests\integration\test_framework_examples.py -v
```

## Configuration

No special config required beyond pytest defaults.

## Input / Output

**Expects:** Repository paths under `examples/` and integration modules.  
**Creates:** Pass/fail output indicating integration asset contract health.

## Pipeline Position

**Fed by:** changes to examples and integration packaging.  
**Feeds into:** CI contract validation for documentation/sample reliability.

## Hardcoded Paths

Uses repository-relative paths referenced in assertions.

## Files

| File | Purpose |
|------|---------|
| `test_framework_examples.py` | Integration file contract checks |

## How It Works

1. Resolve expected example paths.
2. Assert each expected integration example exists.
3. Fail fast on missing files.

## Example Output

```text
tests/integration/test_framework_examples.py::test_framework_example_files_exist PASSED
```

## Safety & Reliability

- Read-only checks; no mutation of project files.

## Logging & Observability

- Pytest output provides clear failing path names on contract breakage.

## Troubleshooting / FAQ

Problem: test fails after refactor  
Fix: update integration test assertions and related docs together.

## Versioning / Roadmap

- Aligned with Eye-Witness `0.1.0`.
- Planned: add import-execution integration smoke checks.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
