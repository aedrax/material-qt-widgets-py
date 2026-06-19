"""Tests for MdRangeSlider."""

from __future__ import annotations

from material_qt.widgets.rangeslider import MdRangeSlider


def _slider(qtbot, **kw) -> MdRangeSlider:
    rs = MdRangeSlider(**kw)
    qtbot.addWidget(rs)
    rs.resize(220, 40)
    return rs


def test_initial_values_clamped_and_ordered(qtbot):
    rs = _slider(qtbot, minimum=0, maximum=100, low=80, high=20)
    # Out-of-order inputs are sorted.
    assert rs.values() == (20, 80)


def test_set_values_clamps_to_bounds(qtbot):
    rs = _slider(qtbot, minimum=0, maximum=100)
    rs.set_values(-50, 200)
    assert rs.values() == (0, 100)


def test_values_changed_signal(qtbot):
    rs = _slider(qtbot, low=10, high=90)
    seen = []
    rs.valuesChanged.connect(lambda lo, hi: seen.append((lo, hi)))
    rs.set_values(30, 70)
    assert seen[-1] == (30, 70)


def test_nearest_handle_picks_closer(qtbot):
    rs = _slider(qtbot, minimum=0, maximum=100, low=20, high=80)
    # x near the low handle vs the high handle.
    lx = rs._handle_x(20)
    hx = rs._handle_x(80)
    assert rs._nearest_handle(lx + 1) == "low"
    assert rs._nearest_handle(hx - 1) == "high"


def test_drag_low_cannot_cross_high(qtbot):
    rs = _slider(qtbot, minimum=0, maximum=100, low=20, high=60)
    rs._active = "low"
    # Drag the low handle far past the high handle; it clamps at high.
    rs._set_active_from_x(rs._handle_x(90))
    assert rs.low == rs.high == 60


def test_drag_high_cannot_cross_low(qtbot):
    rs = _slider(qtbot, minimum=0, maximum=100, low=40, high=80)
    rs._active = "high"
    rs._set_active_from_x(rs._handle_x(10))
    assert rs.high == rs.low == 40


def test_renders(qtbot):
    rs = _slider(qtbot, low=25, high=75)
    rs.grab()
