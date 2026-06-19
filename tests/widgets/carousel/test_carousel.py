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


def test_snap_positions_are_item_leading_edges(qtbot):
    c = MdCarousel()
    qtbot.addWidget(c)
    for n in ["a", "b", "c"]:
        c.add_tile(n)
    # 150px tiles + 8px gap -> 0, 158, 316.
    assert c._positions == [0.0, 158.0, 316.0]


def test_nearest_index_snaps_to_closest(qtbot):
    c = MdCarousel()
    qtbot.addWidget(c)
    for n in ["a", "b", "c"]:
        c.add_tile(n)
    assert c._nearest_index(0) == 0
    assert c._nearest_index(160) == 1   # closest to 158
    assert c._nearest_index(300) == 2   # closest to 316


def test_index_changed_signal(qtbot):
    c = MdCarousel()
    qtbot.addWidget(c)
    for n in ["a", "b", "c"]:
        c.add_tile(n)
    seen = []
    c.indexChanged.connect(seen.append)
    c._on_scroll(int(c._positions[2]))  # as if scrolled to the third item
    assert c.current_index == 2 and seen[-1] == 2


def test_renders(qtbot):
    c = MdCarousel()
    qtbot.addWidget(c)
    for name in ["Beach", "Mountain", "Forest", "City", "Desert"]:
        c.add_tile(name)
    c.resize(400, 200)
    c.grab()
