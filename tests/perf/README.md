# perf

**Category:** 05_Validators  
**Status:** Production

> Performance-smoke tests for logging, metrics, and tracing hot paths.

## Overview

**What it does:** Executes lightweight loops over core observability operations to catch catastrophic slowdowns/regressions.  
**What it does NOT do:** It does not provide formal benchmark baselines or SLA-grade throughput guarantees.

## Use Cases

- Fast regression signal after instrumentation changes.
- Ensure core telemetry loops run without runtime errors.
- Sanity-check disabled-exporter performance paths.

## Features

- Separate tests for logging, metrics, and tracing.
- Minimal runtime cost for regular CI usage.
- Uses safe local exporters (`none`) by default.

## Requirements

- Python 3.10+
- `pytest`

## Quick Start

```powershell
cd <project-root>
python -m pytest tests\perf -v
```

## Usage

```powershell
python -m pytest tests\perf\test_logging_perf.py tests\perf\test_metrics_perf.py tests\perf\test_tracing_perf.py -v
```

## Configuration

Tests initialize Eye-Witness with exporters disabled to isolate local code path behavior.

## Input / Output

**Expects:** Eye-Witness package and test environment.  
**Creates:** Pass/fail output for perf-smoke checks.

## Pipeline Position

**Fed by:** changes in logging/metrics/tracing internals.  
**Feeds into:** pre-merge regression gating.

## Hardcoded Paths

No absolute paths required.

## Files

| File | Purpose |
|------|---------|
| `test_logging_perf.py` | Logging throughput smoke |
| `test_metrics_perf.py` | Metrics emission smoke |
| `test_tracing_perf.py` | Span creation smoke |

## How It Works

1. Initialize Eye-Witness with low-overhead test config.
2. Execute repeated telemetry operations in tight loops.
3. Fail on runtime exceptions.

## Example Output

```text
tests/perf/test_logging_perf.py::test_logging_perf_smoke PASSED
tests/perf/test_metrics_perf.py::test_metrics_perf_smoke PASSED
tests/perf/test_tracing_perf.py::test_tracing_perf_smoke PASSED
```

## Safety & Reliability

- Local-only test mode with no external exporter dependency.

## Logging & Observability

- Pytest output is primary signal; pair with `scripts/benchmark_*.py` for deeper metrics.

## Troubleshooting / FAQ

Problem: flaky timing expectations  
Fix: these are smoke tests, not strict benchmarks; avoid adding hard timing thresholds.

## Versioning / Roadmap

- Aligned with Eye-Witness `0.1.0`.
- Planned: optional benchmark marker with tracked performance history.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
