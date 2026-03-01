"""Wheel contract tests against a clean virtual environment."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.mark.contract
def test_wheel_contract_smoke():
    if os.getenv("EW_RUN_CONTRACT", "0") != "1":
        pytest.skip("Set EW_RUN_CONTRACT=1 to run wheel contract tests")

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(__file__).resolve().parents[1]
        dist_dir = Path(tmpdir) / "dist"
        dist_dir.mkdir(parents=True, exist_ok=True)

        subprocess.run(
            [sys.executable, "-m", "build", "--wheel", "--outdir", str(dist_dir)],
            cwd=root,
            check=True,
        )
        wheel = sorted(dist_dir.glob("*.whl"))[-1]

        venv_dir = Path(tmpdir) / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

        venv_py = venv_dir / "Scripts" / "python.exe"
        subprocess.run([str(venv_py), "-m", "ensurepip", "--upgrade"], check=True)
        subprocess.run([str(venv_py), "-m", "pip", "install", str(wheel)], check=True)

        script = (
            "import warnings\n"
            "from eye_witness.v1 import init, get_logger, shutdown\n"
            "from eye_witness import init_observability, get_structured_logger\n"
            "warnings.simplefilter('always', DeprecationWarning)\n"
            "init(otel_exporter='none', metrics_enabled=False, flush_on_exit=False)\n"
            "get_logger('contract').info('contract.ok')\n"
            "init_observability("
            "otel_exporter='none', "
            "metrics_enabled=False, "
            "flush_on_exit=False, "
            "force=True"
            ")\n"
            "get_structured_logger('contract').info('contract.compat.ok')\n"
            "shutdown()\n"
        )
        subprocess.run([str(venv_py), "-c", script], check=True)
