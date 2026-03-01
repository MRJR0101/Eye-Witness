"""Versioned API and compatibility shim tests."""

from __future__ import annotations

import warnings

from eye_witness import get_logger as top_get_logger
from eye_witness import init as top_init
from eye_witness import init_observability, shutdown
from eye_witness.v1 import get_logger as v1_get_logger
from eye_witness.v1 import init as v1_init


def test_v1_namespace_parity():
    assert top_init is v1_init
    assert top_get_logger is v1_get_logger


def test_compat_init_emits_deprecation_warning():
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always", DeprecationWarning)
        init_observability(
            otel_exporter="none",
            metrics_enabled=False,
            flush_on_exit=False,
            force=True,
        )
        assert any("deprecated" in str(w.message).lower() for w in captured)
    shutdown()
