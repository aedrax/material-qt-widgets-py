"""Tests for MdCarousel."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel

from material_qt.widgets.carousel import MdCarousel


def test_add_tile_and_item_count(qtbot):
    c = MdCarousel()
    qtbot.addWidget(c)
    c.add_tile("One")
    c.add_tile("Two")
    c.add_item(QLabel("custom"))
    assert c.count() == 3


def test_renders(qtbot):
    c = MdCarousel()
    qtbot.addWidget(c)
    for name in ["Beach", "Mountain", "Forest", "City", "Desert"]:
        c.add_tile(name)
    c.resize(400, 200)
    c.grab()
