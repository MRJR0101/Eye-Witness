"""
Release readiness checks for Eye-Witness.

Run:
    python scripts/release_check.py
"""

from __future__ import annotations

import subprocess
import sys


def run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    output = (proc.stdout + proc.stderr).strip()
    return proc.returncode, output


def main() -> int:
    checks: list[tuple[str, list[str]]] = [
        ("ruff", [sys.executable, "-m", "ruff", "check", "src", "tests", "examples", "scripts"]),
        ("mypy", [sys.executable, "-m", "mypy", "src"]),
        ("api-parity", [sys.executable, "scripts/check_api_parity.py"]),
        ("pytest", [sys.executable, "-m", "pytest", "-q"]),
        ("build", [sys.executable, "-m", "build"]),
    ]

    failed = False
    for name, cmd in checks:
        print(f"== {name} ==")
        code, output = run(cmd)
        if output:
            print(output)
        if code != 0:
            failed = True
            print(f"[FAIL] {name}")
        else:
            print(f"[OK] {name}")
        print()

    if failed:
        print("Release check failed.")
        return 1

    print("Release check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
