"""
Ensure top-level API and v1 API stay in parity.

Run:
    python scripts/check_api_parity.py
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"

TOPLEVEL_EXTRAS = {"init_observability", "get_structured_logger"}


def _read_all_symbols(module_file: Path) -> set[str]:
    """Read __all__ list from a module using AST, without importing runtime deps."""
    source = module_file.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(module_file))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        symbols: list[str] = []
                        for element in node.value.elts:
                            if isinstance(element, ast.Constant) and isinstance(element.value, str):
                                symbols.append(element.value)
                        return set(symbols)
    raise ValueError(f"Could not locate static __all__ in {module_file}")


def main() -> int:
    top_file = SRC_PATH / "eye_witness" / "__init__.py"
    v1_file = SRC_PATH / "eye_witness" / "v1" / "__init__.py"

    top = _read_all_symbols(top_file) - TOPLEVEL_EXTRAS
    v1 = _read_all_symbols(v1_file)

    missing_in_v1 = sorted(top - v1)
    extra_in_v1 = sorted(v1 - top)

    if missing_in_v1 or extra_in_v1:
        if missing_in_v1:
            print("Missing in v1:", ", ".join(missing_in_v1))
        if extra_in_v1:
            print("Extra in v1:", ", ".join(extra_in_v1))
        return 1

    print("API parity OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
