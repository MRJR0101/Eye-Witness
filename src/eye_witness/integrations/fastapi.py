"""FastAPI integration helpers."""

from __future__ import annotations

import uuid
from collections.abc import Callable

from eye_witness._context import bind_context, clear_context


def install_fastapi(
    app,
    *,
    request_id_header: str = "x-request-id",
    user_id_getter: Callable | None = None,
) -> None:
    """
    Install request context middleware for FastAPI/Starlette apps.

    Usage:
        from eye_witness.integrations import install_fastapi
        install_fastapi(app)
    """

    @app.middleware("http")
    async def eye_witness_middleware(request, call_next):
        clear_context()
        request_id = request.headers.get(request_id_header) or str(uuid.uuid4())
        bound = {"request_id": request_id}
        if user_id_getter is not None:
            user_id = user_id_getter(request)
            if user_id is not None:
                bound["user_id"] = str(user_id)
        bind_context(**bound)
        try:
            return await call_next(request)
        finally:
            clear_context()
