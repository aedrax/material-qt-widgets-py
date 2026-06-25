"""Tests for MdCarousel."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from material_qt import core
from material_qt.widgets.carousel import MdCarousel, MdWeightedCarousel
from material_qt.widgets.carousel.carousel import weighted_geometry


def test_wheel_reaches_the_end_at_a_narrow_width(qtbot):
    # Regression: at a width too narrow to bring the last item's leading edge to
    # the viewport's left, wheel notches must still scroll to the very end (the
    # max scroll). The step accumulates in _target_index, not the lagging bar.
    core.motion.MOTION_ENABLED = False  # settle each scroll synchronously
    try:
        host = QWidget()
        lay = QVBoxLayout(host)
        c = MdCarousel()
        for n in ["a", "b", "c", "d", "e", "f"]:
            c.add_tile(n)
        lay.addWidget(c)
        qtbot.addWidget(host)
        host.resize(420, 240)
        host.show()
        qtbot.waitExposed(host)
        bar = c._scroll.horizontalScrollBar()
        assert bar.maximum() > 0  # content overflows the narrow viewport
        # The last item's leading edge is beyond the max scroll (the symptom).
        assert c._positions[-1] > bar.maximum()
        # Drive the wheel-down path repeatedly (what eventFilter calls).
        for _ in range(len(c._positions) + 2):
            c._scroll_to_index(c._target_index + 1)
        assert bar.value() == bar.maximum()  # reached the end, not stalled short
        # And wheel-up returns all the way to the start.
        for _ in range(len(c._positions) + 2):
            c._scroll_to_index(c._target_index - 1)
        assert bar.value() == bar.minimum()
    finally:
        core.motion.MOTION_ENABLED = True


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


def test_item_extent_sets_tile_width_and_snap_stride(qtbot):
    c = MdCarousel(item_extent=200)
    qtbot.addWidget(c)
    assert c.item_extent == 200
    for n in ["a", "b", "c"]:
        c.add_tile(n)
    # 200px tiles + 8px gap -> 0, 208, 416.
    assert c._positions == [0.0, 208.0, 416.0]


def test_padding_offsets_snap_positions(qtbot):
    c = MdCarousel(padding=24)
    qtbot.addWidget(c)
    for n in ["a", "b", "c"]:
        c.add_tile(n)
    # Tiles start at the left padding, so leading edges are 24, 182, 340.
    assert c._positions == [24.0, 182.0, 340.0]


def test_item_snapping_toggle_clears_snap_points(qtbot):
    c = MdCarousel(item_snapping=False)
    qtbot.addWidget(c)
    assert c.item_snapping is False
    for n in ["a", "b"]:
        c.add_tile(n)
    # Positions still tracked even when snapping is off.
    assert c._positions == [0.0, 158.0]
    c.set_item_snapping(True)
    assert c.item_snapping is True


def test_vertical_scroll_direction_rejected(qtbot):
    import pytest
    from PySide6.QtCore import Qt

    with pytest.raises(ValueError):
        MdCarousel(scroll_direction=Qt.Orientation.Vertical)


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


def test_weighted_consume_max_weight_last_item_reaches_max_slot():
    # Default consumeMaxWeight=True: the last item can reach the max slot.
    # weights [3,2,1] => max slot is index 0 (the leading/hero slot).
    g = weighted_geometry(4.0, 5, [3, 2, 1], 600)  # p = N-1, last item leading
    assert g[0] == (4, 0.0, 300.0)  # item 4 fills the max (300px) slot
    assert len(g) == 1  # trailing slots are empty


def test_weighted_index_and_clamp(qtbot):
    c = MdWeightedCarousel(weights=[3, 2, 1])  # consume_max_weight=True
    qtbot.addWidget(c)
    for n in ["a", "b", "c", "d", "e"]:
        c.add_tile(n)
    assert c._min_p() == 0.0 and c._max_p() == 4.0  # last item can reach the hero
    seen = []
    c.indexChanged.connect(seen.append)
    c.set_p(1.0)
    assert c.current_index == 1 and seen[-1] == 1
    c.set_p(99)  # clamps to the last item
    assert c.get_p() == 4.0


def test_weighted_full_viewport_mode_clamps_short(qtbot):
    c = MdWeightedCarousel(weights=[3, 2, 1], consume_max_weight=False)
    qtbot.addWidget(c)
    for n in ["a", "b", "c", "d", "e"]:
        c.add_tile(n)
    # Viewport stays full: q=0 -> p in [0, N-k] = [0, 2].
    assert c._min_p() == 0.0 and c._max_p() == 2.0


def test_weighted_centre_hero_anchor():
    # [1,7,1]: max slot is the centre (index 1). At p=0 item 0 fills it.
    g = weighted_geometry(0.0, 5, [1, 7, 1], 900)
    # slot widths: 100/700/100 at lefts 0/100/800.
    by_index = {i: (left, w) for i, left, w in g}
    assert by_index[0] == (100.0, 700.0)  # item 0 in the centre (max) slot
    assert by_index[1] == (800.0, 100.0)  # item 1 in the trailing small slot
    assert all(left >= 100.0 for _, left, _w in g)  # leading small slot is empty


def test_weighted_no_scroll_when_single_item(qtbot):
    c = MdWeightedCarousel(weights=[3, 2, 1])
    qtbot.addWidget(c)
    c.add_tile("only")
    assert c._max_p() == 0.0 and c._min_p() == 0.0  # one item -> nothing to scroll


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
