"""
Sampling — Control Trace Volume.

Built-in samplers from the Path 3 reference:
  - ALWAYS_ON: Sample every trace (default)
  - ALWAYS_OFF: Drop every trace
  - TraceIdRatioBased(rate): Sample a fraction of traces (0.0-1.0)
  - ParentBased(root=...): Respect parent's sampling decision
"""

from opentelemetry.sdk.trace.sampling import (
    ALWAYS_OFF,
    ALWAYS_ON,
    ParentBased,
    Sampler,
    TraceIdRatioBased,
)


def get_sampler(
    mode: str = "always_on",
    rate: float = 1.0,
) -> Sampler:
    """
    Get a sampler by mode name.

    Args:
        mode: One of "always_on", "always_off", "ratio", "parent_based"
        rate: Sampling rate for "ratio" and "parent_based" modes (0.0-1.0)
    """
    if mode == "always_on":
        return ALWAYS_ON
    elif mode == "always_off":
        return ALWAYS_OFF
    elif mode == "ratio":
        return TraceIdRatioBased(rate)
    elif mode == "parent_based":
        return ParentBased(root=TraceIdRatioBased(rate))
    else:
        raise ValueError(f"Unknown sampler mode: {mode!r}")
