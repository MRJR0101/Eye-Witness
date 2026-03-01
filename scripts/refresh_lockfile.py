"""
Refresh requirements.lock.txt from current environment.

Run:
    python scripts/refresh_lockfile.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

LOCKFILE = Path("requirements.lock.txt")


def main() -> int:
    proc = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True)
    proc.check_returncode()
    lines = []
    for line in proc.stdout.splitlines():
        if not line or line.startswith("#"):
            continue
        if line.startswith("-e "):
            continue
        lines.append(line)

    LOCKFILE.write_text(
        "# Reproducible dependency lock for CI/docker matrix harness.\n"
        "# Refresh with: python scripts/refresh_lockfile.py\n"
        + "\n".join(sorted(lines))
        + "\n",
        encoding="utf-8",
    )
    print(f"updated {LOCKFILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
