"""Celery integration helpers."""

from __future__ import annotations

from typing import Any

from eye_witness._context import bind_context, clear_context


def install_celery(signals_module: Any = None) -> None:
    """
    Install task lifecycle hooks for Celery.

    Usage:
        from eye_witness.integrations import install_celery
        install_celery()
    """
    if signals_module is None:
        from celery import signals as celery_signals

        signals_module = celery_signals

    @signals_module.task_prerun.connect
    def eye_witness_task_prerun(task_id=None, task=None, **kwargs):
        clear_context()
        context = {"task_id": str(task_id or "")}
        if task is not None:
            context["task_name"] = getattr(task, "name", "unknown-task")
        bind_context(**context)

    @signals_module.task_postrun.connect
    def eye_witness_task_postrun(**kwargs):
        clear_context()
