"""Framework integration helpers for Eye-Witness."""

from eye_witness.integrations.celery import install_celery
from eye_witness.integrations.django import EyeWitnessDjangoMiddleware
from eye_witness.integrations.fastapi import install_fastapi
from eye_witness.integrations.flask import install_flask

__all__ = [
    "install_fastapi",
    "install_flask",
    "install_celery",
    "EyeWitnessDjangoMiddleware",
]
