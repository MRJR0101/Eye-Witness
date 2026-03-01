# Migration Guide

## Versioned imports
Prefer explicit versioned imports for long-lived services:

```python
from eye_witness.v1 import init, get_logger
```

## Compatibility shims
Legacy helpers remain available with deprecation warnings:
- `init_observability(...)` -> `init(...)`
- `get_structured_logger(...)` -> `get_logger(...)`

## Auto-rewrite tool
Rewrite safe legacy usage in-place:

```powershell
python scripts/migrate_v1_api.py --path src
```

Dry run:

```powershell
python scripts/migrate_v1_api.py --path src --dry-run
```
