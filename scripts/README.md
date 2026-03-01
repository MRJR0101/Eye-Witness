# scripts

**Category:** 22_DevEnvironment  
**Status:** Production

> Project utility scripts for benchmarks, parity checks, docs generation, and release checks.

## Overview

**What it does:** Collects developer workflows that support benchmarking, API drift detection, packaging checks, lockfile refresh, and Docker matrix execution.  
**What it does NOT do:** It does not replace CI policy or package runtime behavior.

## Use Cases

- Run quick local performance sanity checks.
- Validate API parity before releasing.
- Refresh generated docs and lockfiles.

## Features

- Benchmark scripts for logging, metrics, and tracing paths.
- Release and API compatibility helper scripts.
- Docker matrix runner integration.

## Requirements

- Python 3.10+
- PowerShell 7+ for `.ps1` helpers
- Eye-Witness repo root context

## Quick Start

```powershell
cd C:\Dev\PROJECTS\Eye-Witness
python .\scripts\benchmark_logging.py
python .\scripts\release_check.py
```

## Usage

```powershell
python .\scripts\benchmark_metrics.py
python .\scripts\benchmark_tracing.py
python .\scripts\check_api_parity.py
powershell -File .\scripts\run_docker_matrix.ps1
```

## Configuration

Most scripts are parameter-light and rely on repository-relative paths and current environment dependencies.

## Input / Output

**Expects:** Repository source tree and installed toolchain dependencies.  
**Creates:** Console benchmark output and generated documentation artifacts (depending on script).

## Pipeline Position

**Fed by:** contributor quality workflows and release preparation.  
**Feeds into:** CI readiness, release confidence, and docs maintenance.

## Hardcoded Paths

Scripts primarily use repository-relative paths; update constants in specific scripts when relocating project layout.

## Files

| File | Purpose |
|------|---------|
| `benchmark_logging.py` | Logging throughput benchmark |
| `benchmark_metrics.py` | Metrics emission benchmark |
| `benchmark_tracing.py` | Trace span benchmark |
| `check_api_parity.py` | Public API parity validation |
| `generate_api_docs.py` | API docs generation helper |
| `migrate_v1_api.py` | API migration support script |
| `release_check.py` | Release preflight checks |
| `refresh_lockfile.py` | Dependency lock refresh helper |
| `run_docker_matrix.ps1` | Multi-version Docker matrix runner |

## How It Works

1. Execute selected helper script from repo root.
2. Script validates prerequisites and performs targeted task.
3. Results are printed for developer review.

## Example Output

```text
iterations=2000
elapsed_sec=0.2451
events_per_sec=8158.30
```

## Safety & Reliability

- Scripts are designed for local developer workflows.
- Review scripts that modify files (`generate_api_docs.py`, lock refresh) before automation.

## Logging & Observability

- Script output is plain console by default.
- Benchmark scripts report throughput metrics directly.

## Troubleshooting / FAQ

Problem: script cannot find project files  
Fix: run from repository root (`C:\Dev\PROJECTS\Eye-Witness`).

Problem: benchmark numbers vary widely  
Fix: run on quiet machine and average multiple runs.

## Versioning / Roadmap

- Aligned with Eye-Witness `0.1.0`.
- Planned: consolidated CLI wrapper for script operations.

## License & Contact

- License: MIT.
- Maintainer: Eye-Witness contributors.
