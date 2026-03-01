"""Lifecycle inspection helpers."""

from eye_witness import _init as init_module


def state_snapshot() -> dict[str, bool]:
    return {
        "initialized": bool(init_module._initialized),
        "atexit_registered": bool(init_module._atexit_registered),
    }
