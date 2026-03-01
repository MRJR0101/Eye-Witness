"""
Rewrite deprecated Eye-Witness API usage to the current API.

Supported rewrites:
- init_observability(...) -> init(...)
- get_structured_logger(...) -> get_logger(...)
- from eye_witness import init_observability -> from eye_witness import init
- from eye_witness import get_structured_logger -> from eye_witness import get_logger

Run:
    python scripts/migrate_v1_api.py --path src
"""

from __future__ import annotations

import argparse
from pathlib import Path

REWRITES = {
    "init_observability(": "init(",
    "get_structured_logger(": "get_logger(",
    "init_observability": "init",
    "get_structured_logger": "get_logger",
}


def migrate_file(path: Path, dry_run: bool) -> tuple[bool, int]:
    original = path.read_text(encoding="utf-8")
    updated = original
    replacements = 0

    if "from eye_witness import" in updated:
        updated = updated.replace(
            "from eye_witness import init_observability",
            "from eye_witness import init",
        )
        updated = updated.replace(
            "from eye_witness import get_structured_logger",
            "from eye_witness import get_logger",
        )

    for old, new in REWRITES.items():
        before = updated
        updated = updated.replace(old, new)
        if updated != before:
            replacements += 1

    if updated != original:
        if not dry_run:
            path.write_text(updated, encoding="utf-8")
        return True, replacements
    return False, 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=".", help="Directory to scan")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    base = Path(args.path)
    changed_files = 0
    total_replacements = 0

    for file_path in base.rglob("*.py"):
        changed, replacements = migrate_file(file_path, dry_run=args.dry_run)
        if changed:
            changed_files += 1
            total_replacements += replacements
            print(f"updated: {file_path}")

    print(f"files_changed={changed_files}")
    print(f"replacement_groups={total_replacements}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
