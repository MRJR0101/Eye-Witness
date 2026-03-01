# Contributing

## Setup
1. Create/activate virtual environment.
2. Install dev dependencies:
   - `python -m pip install -e .[dev]`

## Quality Gates
- Lint: `python -m ruff check src tests examples scripts`
- Type check: `python -m mypy src`
- Tests: `python -m pytest -q`

## Release Readiness
- Run: `python scripts/release_check.py`

## Contract Tests
- Wheel contract tests are opt-in:
  - PowerShell: `$env:EW_RUN_CONTRACT="1"; python -m pytest -m contract -q`

## Docker Matrix
- Run full containerized matrix:
  - `./scripts/run_docker_matrix.ps1`

## Local Commands
- Demo: `python -m examples.cli_demo`
- Benchmark: `python scripts/benchmark_logging.py`
- Tracing benchmark: `python scripts/benchmark_tracing.py`
- Metrics benchmark: `python scripts/benchmark_metrics.py`
- Generate API doc index: `python scripts/generate_api_docs.py`
