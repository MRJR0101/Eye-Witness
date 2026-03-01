"""Internal serialization helpers."""

from __future__ import annotations

import json
from typing import Any


def safe_json_dumps(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, default=str)
