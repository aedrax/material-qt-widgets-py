"""ColorScheme resolution, light/dark, and ThemeManager signalling."""

from __future__ import annotations

from PySide6.QtGui import QColor

from material_qt.theme.color_scheme import ColorScheme
from material_qt.theme.theme_manager import ThemeManager, ThemeMode
from material_qt.tokens.color import ColorRole


def test_color_scheme_resolves_roles(qapp):
    light = ColorScheme.light()
    dark = ColorScheme.dark()
    assert light.color(ColorRole.PRIMARY) == QColor("#6750a4")
    assert dark.color(ColorRole.PRIMARY) == QColor("#d0bcff")
    assert not light.is_dark
    assert dark.is_dark


def test_color_scheme_cached(qapp):
    assert ColorScheme.light() is ColorScheme.light()
    assert ColorScheme.dark() is ColorScheme.dark()
    assert ColorScheme.for_mode(dark=True) is ColorScheme.dark()


def test_color_scheme_returns_copies(qapp):
    light = ColorScheme.light()
    c1 = light.color(ColorRole.PRIMARY)
    c1.setAlphaF(0.5)
    c2 = light.color(ColorRole.PRIMARY)
    assert c2.alphaF() == 1.0  # mutation did not leak into the scheme


def test_theme_manager_mode_switch_signals(qapp):
    tm = ThemeManager.instance()
    tm.set_mode(ThemeMode.LIGHT)
    received = []
    tm.themeChanged.connect(lambda: received.append(tm.is_dark))

    tm.set_mode(ThemeMode.DARK)
    assert tm.is_dark is True
    assert received == [True]

    tm.set_mode(ThemeMode.LIGHT)
    assert tm.is_dark is False
    assert received == [True, False]


def test_theme_manager_no_signal_when_unchanged(qapp):
    tm = ThemeManager.instance()
    tm.set_mode(ThemeMode.LIGHT)
    received = []
    tm.themeChanged.connect(lambda: received.append(1))
    tm.set_mode(ThemeMode.LIGHT)  # same mode -> same scheme
    assert received == []


def test_theme_manager_color(qapp):
    tm = ThemeManager.instance()
    tm.set_mode(ThemeMode.DARK)
    assert tm.color(ColorRole.PRIMARY) == QColor("#d0bcff")


def test_apply_app_palette(qapp):
    from PySide6.QtGui import QPalette

    tm = ThemeManager.instance()
    tm.set_mode(ThemeMode.LIGHT)
    tm.apply_app_palette(qapp)
    palette = qapp.palette()
    assert palette.color(QPalette.ColorRole.Highlight) == QColor("#6750a4")
    assert palette.color(QPalette.ColorRole.Base) == QColor("#ffffff")
