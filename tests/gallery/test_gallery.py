"""Smoke test: the gallery builds every component page without crashing."""

from __future__ import annotations

from material_qt.gallery.gallery import _COMPONENTS, GalleryWindow


def test_gallery_builds_all_pages(qtbot):
    w = GalleryWindow()
    qtbot.addWidget(w)
    assert w._stack.count() == len(_COMPONENTS)
    # Visit every page (forces each builder + a paint).
    for i in range(w._stack.count()):
        w._nav.setCurrentRow(i)
    w.resize(900, 620)
    w.grab()


def test_theme_toggle(qtbot):
    w = GalleryWindow()
    qtbot.addWidget(w)
    assert w._dark is False
    w._toggle_theme()
    assert w._dark is True
