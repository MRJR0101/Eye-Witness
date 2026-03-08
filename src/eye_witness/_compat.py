"""
Backward-compatibility shims for legacy helper names.
"""

from __future__ import annotations

import warnings
from typing import Any

from eye_witness._init import init
from eye_witness._logging import get_logger


def init_observability(**kwargs: Any) -> None:
    warnings.warn(
        "`init_observability()` is deprecated; use `init()`.",
        DeprecationWarning,
        stacklevel=2,
    )
    return init(**kwargs)


def get_structured_logger(name: str | None = None, **initial_context: Any) -> Any:
    warnings.warn(
        "`get_structured_logger()` is deprecated; use `get_logger()`.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_logger(name, **initial_context)
