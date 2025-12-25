"""Dependency injection functions for FastAPI."""

from app.dependencies.auth import get_current_user, require_auth  # noqa: F401
