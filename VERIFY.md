# Verification: Eye-Witness

## Purpose

Validate that the `eye_witness` package imports, its public API is callable,
and the full test suite passes.

## Prerequisites

- Python 3.10 or newer
- `uv` installed (standard across this project)

## Verification Steps

### Step 1: Install

```powershell
uv sync --extra dev
```

### Step 2: Import smoke check

```powershell
uv run python -c "from eye_witness import init, shutdown, EyeWitnessConfig; print('ok')"
```

Expected output: `ok`

### Step 3: Lint and type check

```powershell
uv run ruff check src tests examples scripts
uv run mypy src
```

### Step 4: Tests

```powershell
uv run pytest -q
```

## Expected Output

- Import smoke prints `ok`
- Ruff and mypy report no errors
- Pytest reports all tests passing

## Notes

- Entrypoint is the importable `eye_witness` package, not a `main.py` script.
- Example usage scripts live in `examples/` and are referenced in `README.md`.

## Status

- Last Verified: 2026-04-22
- Verified By: Manual audit (MR)
- Result: PENDING MANUAL CONFIRMATION
