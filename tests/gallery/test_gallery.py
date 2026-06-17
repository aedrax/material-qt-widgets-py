"""Smoke test: the gallery builds every component page without crashing."""

from __future__ import annotations

from material_qt.gallery.gallery import _COMPONENTS, GalleryWindow
from material_qt.theme.theme_manager import ThemeManager, ThemeMode


def test_gallery_builds_all_pages(qtbot):
    w = GalleryWindow()
    qtbot.addWidget(w)
    assert w._stack.count() == len(_COMPONENTS)
    # Visit every page (forces each builder + a paint).
    for i in range(w._stack.count()):
        w._nav.setCurrentRow(i)
    w.resize(900, 620)
    w.grab()


def test_theme_toggle_flips_on_first_click(qtbot):
    # Start from a known LIGHT state.
    ThemeManager.instance().set_mode(ThemeMode.LIGHT)
    w = GalleryWindow()
    qtbot.addWidget(w)
    assert ThemeManager.instance().is_dark is False
    assert w._theme_btn.text() == "Dark mode"
    w._toggle_theme()
    assert ThemeManager.instance().is_dark is True
    assert w._theme_btn.text() == "Light mode"


def test_toggle_button_reflects_starting_theme(qtbot):
    # If the app starts dark (e.g. SYSTEM mode on a dark OS), the button must
    # already offer "Light mode" so a single click switches to light.
    ThemeManager.instance().set_mode(ThemeMode.DARK)
    w = GalleryWindow()
    qtbot.addWidget(w)
    assert w._theme_btn.text() == "Light mode"
    w._toggle_theme()
    assert ThemeManager.instance().is_dark is False
