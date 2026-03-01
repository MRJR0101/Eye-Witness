"""
Sentry Context Attachment — Tags, Context, User.

From the reference:
  - Tags: indexed and searchable in Sentry UI. Use for high-cardinality
    identifiers you will filter/search by. Keep values short strings.
  - Context: displayed in event detail but NOT searchable. Use for
    structured metadata that helps debugging. Can include nested objects.
  - User: enables "affected users" counting in Sentry UI.
"""

from typing import Any

import sentry_sdk


# ── Tags (Indexed, Searchable) ───────────────────────────────────────────────

def set_tags(**tags: str) -> None:
    """
    Set one or more Sentry tags (indexed, searchable).

    Usage:
        set_tags(job_id="abc123", api_version="v2")
    """
    for key, value in tags.items():
        sentry_sdk.set_tag(key, value)


# ── Context (Structured, Not Indexed) ────────────────────────────────────────

def set_structured_context(name: str, data: dict[str, Any]) -> None:
    """
    Set structured context (displayed in event detail, NOT searchable).

    Usage:
        set_structured_context("job", {
            "id": "abc123",
            "type": "data_pipeline",
            "input_rows": 50000,
        })
    """
    sentry_sdk.set_context(name, data)


# ── User ─────────────────────────────────────────────────────────────────────

def set_user(
    user_id: str,
    *,
    email: str = "",
    username: str = "",
) -> None:
    """
    Set user context for "affected users" counting.

    Set user_id at minimum; email/username are optional.
    Note: email is only sent if send_default_pii=True in init.

    Usage:
        set_user("user-42", email="user@example.com", username="johndoe")
    """
    user_data: dict[str, str] = {"id": user_id}
    if email:
        user_data["email"] = email
    if username:
        user_data["username"] = username

    sentry_sdk.set_user(user_data)
