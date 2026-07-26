"""The top-level import surface stays in sync with the widget packages.

:mod:`material_qt` re-exports every widget package's ``__all__`` plus the
theming API; these tests recompute that union by walking
``src/material_qt/widgets/*/`` so a widget added without wiring up the
re-exports fails loudly.
"""

from __future__ import annotations

import importlib
import pkgutil

import material_qt
import material_qt.widgets as widgets_pkg

_THEME_EXPORTS = {"ColorScheme", "ThemeManager", "ThemeMode"}


def _widget_packages() -> list[str]:
    return sorted(
        m.name for m in pkgutil.iter_modules(widgets_pkg.__path__) if m.ispkg
    )


def _union_of_widget_alls() -> set[str]:
    names: set[str] = set()
    for pkg in _widget_packages():
        mod = importlib.import_module(f"material_qt.widgets.{pkg}")
        names.update(mod.__all__)
    return names


def test_widgets_all_matches_package_union():
    assert set(widgets_pkg.__all__) == _union_of_widget_alls()


def test_top_level_all_is_widgets_plus_theme():
    expected = _union_of_widget_alls() | _THEME_EXPORTS | {"__version__"}
    assert set(material_qt.__all__) == expected


def test_every_export_importable():
    for name in material_qt.__all__:
        assert getattr(material_qt, name, None) is not None, name


def test_version_matches_pyproject():
    assert material_qt.__version__ == "1.0.0"
