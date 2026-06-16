"""Shared pytest fixtures. Forces headless Qt and provides a QApplication."""

from __future__ import annotations

import os

# Must be set before any Qt import creates a platform plugin.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402


@pytest.fixture(scope="session")
def qapp_args() -> list[str]:
    return ["material-qt-tests"]


@pytest.fixture(autouse=True)
def _reset_theme():
    """Reset the ThemeManager singleton between tests for isolation."""
    yield
    try:
        from material_qt.theme.theme_manager import ThemeManager

        ThemeManager._instance = None
    except Exception:
        pass
