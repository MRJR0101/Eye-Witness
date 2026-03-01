"""Migration command tests."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def test_migration_tool_rewrites_deprecated_symbols():
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "legacy.py"
        target.write_text(
            "from eye_witness import init_observability, get_structured_logger\n"
            "init_observability(service_name='legacy')\n"
            "log = get_structured_logger('legacy')\n",
            encoding="utf-8",
        )

        subprocess.run(
            [
                sys.executable,
                "scripts/migrate_v1_api.py",
                "--path",
                str(Path(tmp)),
            ],
            check=True,
        )

        updated = target.read_text(encoding="utf-8")
        assert "init_observability" not in updated
        assert "get_structured_logger" not in updated
        assert "from eye_witness import init, get_logger" in updated
