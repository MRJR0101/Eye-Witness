"""
Generate a simple API symbol listing from eye_witness.__all__.
"""

from __future__ import annotations

from pathlib import Path

import eye_witness


def main() -> None:
    out = Path("docs/api/auto-generated.md")
    symbols = sorted(getattr(eye_witness, "__all__", []))
    lines = ["# Auto Generated API", ""] + [f"- `{name}`" for name in symbols]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
