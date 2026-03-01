# Docker Matrix Harness

Run a containerized matrix across Python `3.10` to `3.13` using the pinned lockfile.

## Prerequisites
- Docker installed and running.

## Run

```powershell
./scripts/run_docker_matrix.ps1
```

## What it does
1. Builds a wheel inside each Python-version container.
2. Installs dependencies from `requirements.lock.txt`.
3. Installs the built wheel.
4. Runs:
   - `ruff check src tests examples scripts`
   - `mypy src`
   - `pytest -q`
