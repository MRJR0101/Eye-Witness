"""Schema key helpers used by snapshot tests."""

from __future__ import annotations

from typing import Any


def stable_keys(payload: dict[str, Any]) -> list[str]:
    return sorted(payload.keys())
