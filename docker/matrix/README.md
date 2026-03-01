# matrix

**Category:** 22_DevEnvironment  
**Status:** Production

> Docker-based Python version matrix for Eye-Witness quality gates.

## Overview

**What it does:** Builds and runs the Eye-Witness test/lint/type-check pipeline across multiple Python versions using `docker/matrix/Dockerfile` and `scripts/run_docker_matrix.ps1`.  
**What it does NOT do:** It does not publish images, deploy services, or replace native CI workflows.

## Use Cases

- Validate compatibility against Python 3.10-3.13.
- Reproduce CI failures locally with the same container build path.
- Smoke-test release candidates before publishing wheels.

## Features

- Parameterized Python version build arg in Dockerfile.
- Full quality run (`ruff`, `mypy`, `pytest`) inside container.
- PowerShell runner for multi-version matrix execution.

## Requirements

- Docker Desktop or Docker Engine
- PowerShell 7+
- Eye-Witness repository root as build context

## Quick Start

```powershell
cd C:\Dev\PROJECTS\Eye-Witness
powershell -File .\scripts\run_docker_matrix.ps1
```

## Usage

```powershell
# Single version build/run
docker build --build-arg PYTHON_VERSION=3.12 -f docker/matrix/Dockerfile -t eye-witness:py312 .
docker run --rm eye-witness:py312

# Matrix run
powershell -File .\scripts\run_docker_matrix.ps1 -Versions 3.10,3.11,3.12,3.13
```

## Configuration

- `PYTHON_VERSION` build arg controls base image tag.
- `scripts/run_docker_matrix.ps1` controls the version set.

## Input / Output

**Expects:** Eye-Witness source tree and dependency files in repository root.  
**Creates:** Built container images and console output for lint/type/test results.

## Pipeline Position

**Fed by:** source changes in `src`, `tests`, `examples`, `scripts`.  
**Feeds into:** release readiness decisions and CI parity checks.

## Hardcoded Paths

Uses repository-relative paths (`docker/matrix/Dockerfile`, `src`, `tests`, `examples`, `scripts`).

## Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Matrix test image definition |
| `README.md` | This documentation |

## How It Works

1. Build image for each requested Python version.
2. Install wheel and lockfile dependencies in container.
3. Run lint, typing, and test commands.
4. Return success/failure via container exit code.

## Example Output

```text
== Building and testing Python 3.12 ==
... ruff check src tests examples scripts
... mypy src
... pytest -q
Matrix run completed.
```

## Safety & Reliability

- Non-destructive to host source tree.
- Isolated dependency resolution per container build.
- Repeatable checks with pinned base image version.

## Logging & Observability

- Primary output is Docker build/run console logs.
- CI systems can capture the same stdout/stderr stream.

## Troubleshooting / FAQ

Problem: `docker: command not found`  
Fix: Install Docker and ensure CLI is in `PATH`.

Problem: Build fails on dependency install  
Fix: Refresh lock/dependency files and rebuild without cache.

## Versioning / Roadmap

- Versioning follows Eye-Witness project version (`0.1.0`).
- Planned: add image cache optimization and optional matrix parallelization.

## License & Contact

- License: MIT (inherits from project root).
- Maintainer: Eye-Witness contributors.
