"""Tests for MdCarousel."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel

from material_qt.widgets.carousel import MdCarousel, MdWeightedCarousel
from material_qt.widgets.carousel.carousel import weighted_geometry


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


# -- weighted carousel ----------------------------------------------------

def test_weighted_geometry_snapped_fills_slots():
    # weights [3,2,1], W=600 -> slot widths 300/200/100 at slot lefts 0/300/500.
    g = weighted_geometry(0.0, 5, [3, 2, 1], 600)
    assert g[0] == (0, 0.0, 300.0)
    assert g[1] == (1, 300.0, 200.0)
    assert g[2] == (2, 500.0, 100.0)
    assert len(g) == 3  # the 4th item is collapsed at the right edge


def test_weighted_geometry_tiles_to_width_when_scrolling():
    for p in (0.25, 0.5, 0.75):
        g = weighted_geometry(p, 6, [3, 2, 1], 600)
        assert abs(sum(w for _, _, w in g) - 600) < 1e-6  # no gaps/overlaps
        # lefts are strictly increasing and contiguous
        for (_, l0, w0), (_, l1, _w1) in zip(g, g[1:], strict=False):
            assert abs((l0 + w0) - l1) < 1e-6


def test_weighted_geometry_boundary_continuity():
    # p -> 1 from below equals p == 1 (item 1 becomes the leading hero).
    near = weighted_geometry(0.999, 6, [3, 2, 1], 600)
    at = weighted_geometry(1.0, 6, [3, 2, 1], 600)
    assert at[0] == (1, 0.0, 300.0)
    assert near[0][0] == 1 and abs(near[0][2] - 300.0) < 1.0


def test_weighted_index_and_clamp(qtbot):
    c = MdWeightedCarousel(weights=[3, 2, 1])
    qtbot.addWidget(c)
    for n in ["a", "b", "c", "d", "e"]:
        c.add_tile(n)
    # max_p keeps the viewport full: N - k = 5 - 3 = 2.
    assert c._max_p() == 2.0
    seen = []
    c.indexChanged.connect(seen.append)
    c.set_p(1.0)
    assert c.current_index == 1 and seen[-1] == 1
    c.set_p(99)  # clamps
    assert c.get_p() == 2.0


def test_weighted_no_scroll_when_items_fit(qtbot):
    c = MdWeightedCarousel(weights=[3, 2, 1])
    qtbot.addWidget(c)
    c.add_tile("only")
    c.add_tile("two")
    assert c._max_p() == 0.0  # 2 items <= 3 slots -> nothing to scroll


def test_weighted_animate_again_after_finish_no_error(qtbot):
    # animate() deletes its QPropertyAnimation when it stops; scrolling again
    # after one finished must not call .stop() on the dead C++ object.
    c = MdWeightedCarousel(weights=[3, 2, 1])
    qtbot.addWidget(c)
    for n in ["a", "b", "c", "d", "e", "f"]:
        c.add_tile(n)
    c.resize(600, 196)
    c.show()
    c._animate_to(1)
    qtbot.waitUntil(lambda: c._anim is None, timeout=2000)  # let it finish + clear
    c._animate_to(2)  # would raise RuntimeError on the stale animation before the fix
    assert c._anim is not None


def test_weighted_renders(qtbot):
    c = MdWeightedCarousel(weights=[3, 2, 1])
    qtbot.addWidget(c)
    for n in ["a", "b", "c", "d"]:
        c.add_tile(n)
    c.resize(600, 200)
    c.grab()
