"""Elevation drop-shadow effect: the baked-in theme color must track theme
changes (apply_elevation snapshots the SHADOW color at apply time)."""

from __future__ import annotations

from PySide6.QtWidgets import QGraphicsDropShadowEffect

from material_qt.core.material_widget import MaterialWidget
from material_qt.theme.theme_manager import ThemeManager, ThemeMode
from material_qt.tokens.color import ColorRole
from material_qt.tokens.elevation import ElevationLevel


def test_elevation_effect_recolors_on_shadow_override(qtbot):
    tm = ThemeManager.instance()
    tm.set_mode(ThemeMode.LIGHT)
    tm.clear_overrides()
    w = MaterialWidget(elevation=ElevationLevel.LEVEL2)
    qtbot.addWidget(w)
    effect = w.graphicsEffect()
    assert isinstance(effect, QGraphicsDropShadowEffect)

    tm.set_overrides({ColorRole.SHADOW: "#ff0000"})
    try:
        effect = w.graphicsEffect()  # re-applied effect
        assert isinstance(effect, QGraphicsDropShadowEffect)
        color = effect.color()
        assert (color.red(), color.green(), color.blue()) == (255, 0, 0)
        assert 0.0 < color.alphaF() < 1.0  # spec opacity is preserved
    finally:
        tm.clear_overrides()
    color = w.graphicsEffect().color()
    assert (color.red(), color.green(), color.blue()) == (0, 0, 0)


def test_level0_widget_skips_effect_refresh(qtbot):
    tm = ThemeManager.instance()
    tm.set_mode(ThemeMode.LIGHT)
    tm.clear_overrides()
    w = MaterialWidget(elevation=ElevationLevel.LEVEL0)
    qtbot.addWidget(w)
    assert w.graphicsEffect() is None
    tm.set_overrides({ColorRole.SHADOW: "#00ff00"})
    try:
        assert w.graphicsEffect() is None  # no effect gained on theme change
    finally:
        tm.clear_overrides()
