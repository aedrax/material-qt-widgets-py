"""Smoke test: the gallery builds every component page without crashing."""

from __future__ import annotations

from material_qt.gallery.gallery import COMPONENT_META, _COMPONENTS, GalleryWindow
from material_qt.theme.theme_manager import ThemeManager, ThemeMode


def test_gallery_builds_all_pages(qtbot):
    w = GalleryWindow()
    qtbot.addWidget(w)
    assert w._stack.count() == len(_COMPONENTS)
    # Drawer has one destination per component.
    assert len(w._drawer._items) == len(_COMPONENTS)
    # Visit every page via the nav drawer (forces each builder + a paint).
    for i in range(w._stack.count()):
        w.select(i)
        assert w._stack.currentIndex() == i
    w.resize(900, 620)
    w.grab()


def test_every_component_has_metadata(qtbot):
    # Each page's hero relies on COMPONENT_META for its icon + description.
    for label, _builder in _COMPONENTS:
        assert label in COMPONENT_META


def test_theme_toggle_flips_on_first_click(qtbot):
    ThemeManager.instance().set_mode(ThemeMode.LIGHT)
    w = GalleryWindow()
    qtbot.addWidget(w)
    assert ThemeManager.instance().is_dark is False
    assert w._theme_btn.icon_name == "dark_mode"  # offers to go dark
    w._toggle_theme()
    assert ThemeManager.instance().is_dark is True
    assert w._theme_btn.icon_name == "light_mode"  # now offers to go light


def test_toggle_button_reflects_starting_theme(qtbot):
    # If the app starts dark, the toggle must already show the light-mode icon.
    ThemeManager.instance().set_mode(ThemeMode.DARK)
    w = GalleryWindow()
    qtbot.addWidget(w)
    assert w._theme_btn.icon_name == "light_mode"
    w._toggle_theme()
    assert ThemeManager.instance().is_dark is False


def test_palette_button_cycles_brand_override(qtbot):
    ThemeManager.instance().set_mode(ThemeMode.LIGHT)
    ThemeManager.instance().clear_overrides()
    w = GalleryWindow()
    qtbot.addWidget(w)
    from material_qt.tokens.color import ColorRole

    baseline = ThemeManager.instance().color(ColorRole.PRIMARY).name()
    w._cycle_brand()  # -> first non-None brand color
    assert ThemeManager.instance().color(ColorRole.PRIMARY).name() != baseline
    # Cycle back around to None (clears the override).
    for _ in range(len(__import__("material_qt.gallery.gallery",
                                  fromlist=["_BRAND_COLORS"])._BRAND_COLORS) - 1):
        w._cycle_brand()
    assert ThemeManager.instance().color(ColorRole.PRIMARY).name() == baseline
