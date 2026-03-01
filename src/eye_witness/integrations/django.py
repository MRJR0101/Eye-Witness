"""Django integration helpers."""

from __future__ import annotations

import uuid

from eye_witness._context import bind_context, clear_context


class EyeWitnessDjangoMiddleware:
    """
    Django middleware that binds request context for logs/traces/errors.

    Add to settings:
        MIDDLEWARE = [
            ...,
            "eye_witness.integrations.django.EyeWitnessDjangoMiddleware",
        ]
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        clear_context()
        request_id = request.headers.get("X-Request-ID") if hasattr(request, "headers") else None
        bind_context(request_id=request_id or str(uuid.uuid4()))
        try:
            response = self.get_response(request)
            return response
        finally:
            clear_context()
