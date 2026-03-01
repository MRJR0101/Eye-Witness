"""
Examples for framework integrations.

These snippets are intentionally minimal and can be copied into app setup.
"""

from eye_witness import (
    EyeWitnessDjangoMiddleware,
    install_celery,
    install_fastapi,
    install_flask,
)


def fastapi_example(app):
    install_fastapi(app)


def flask_example(app):
    install_flask(app)


def celery_example():
    install_celery()


def django_example():
    return "eye_witness.integrations.django.EyeWitnessDjangoMiddleware"


__all__ = [
    "fastapi_example",
    "flask_example",
    "celery_example",
    "django_example",
    "EyeWitnessDjangoMiddleware",
]
