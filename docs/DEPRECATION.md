# Deprecation Policy

## Goals
- Keep upgrades predictable.
- Give users enough time to migrate.

## Process
1. Mark feature as deprecated in docs and changelog.
2. Emit a runtime warning for at least one minor release.
3. Remove in the next major release.

## Warning Style
Use `DeprecationWarning` with:
- what is deprecated
- replacement path
- planned removal version (when known)
