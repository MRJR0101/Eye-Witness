"""Minimal smoke test entrypoint for local and CI sanity checks."""

from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    init_file = repo_root / "src" / "eye_witness" / "__init__.py"
    readme = repo_root / "README.md"

    if not init_file.exists():
        print(f"Missing package entrypoint: {init_file}")
        return 1
    if not readme.exists():
        print(f"Missing README: {readme}")
        return 1

    print("Eye-Witness smoke check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

