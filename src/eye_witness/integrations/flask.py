"""Flask integration helpers."""

from __future__ import annotations

import uuid
from collections.abc import Callable

from eye_witness._context import bind_context, clear_context


def install_flask(
    app,
    *,
    request_id_header: str = "X-Request-ID",
    user_id_getter: Callable | None = None,
) -> None:
    """
    Install request context hooks for Flask apps.

    Usage:
        from eye_witness.integrations import install_flask
        install_flask(app)
    """

    @app.before_request
    def eye_witness_before_request():
        from flask import request

        clear_context()
        request_id = request.headers.get(request_id_header) or str(uuid.uuid4())
        bound = {"request_id": request_id}
        if user_id_getter is not None:
            user_id = user_id_getter(request)
            if user_id is not None:
                bound["user_id"] = str(user_id)
        bind_context(**bound)

    @app.teardown_request
    def eye_witness_teardown_request(exc):
        clear_context()
