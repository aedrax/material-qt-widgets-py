"""Tests for MdRangeSlider."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

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


def test_divisions_snap_both_handles(qtbot):
    # 4 divisions over 0..100 → stops 0/25/50/75/100.
    rs = _slider(qtbot, minimum=0, maximum=100, low=10, high=90, divisions=4)
    assert rs.divisions == 4
    assert rs.values() == (0, 100)  # 10→0, 90→100


def test_divisions_snap_seam(qtbot):
    rs = _slider(qtbot, minimum=0, maximum=100, divisions=4)
    assert rs._snap(13) == 25
    assert rs._snap(60) == 50
    assert rs._snap(-5) == 0
    assert rs._snap(999) == 100


def test_set_divisions_resnaps(qtbot):
    rs = _slider(qtbot, minimum=0, maximum=100, low=40, high=60)
    assert rs.values() == (40, 60)  # continuous
    rs.set_divisions(2)  # stops 0/50/100
    assert rs.values() == (50, 50)


def test_divisions_value_from_x_snaps(qtbot):
    rs = _slider(qtbot, minimum=0, maximum=100, divisions=4)
    track = rs._track_rect()
    v = rs._value_from_x(track.left() + track.width() * 0.62)
    assert v in (0, 25, 50, 75, 100)


def test_coincident_at_min_press_right_moves_high(qtbot):
    # low == high == min used to tie to 'low', which clamps against high —
    # permanently stuck at (min, min). The tie must pick the movable handle.
    rs = _slider(qtbot, minimum=0, maximum=100, low=0, high=0)
    mid = rs._track_rect().center().x()
    assert rs._nearest_handle(mid) == "high"
    rs._active = rs._nearest_handle(mid)
    rs._set_active_from_x(mid)
    assert rs.low == 0
    assert rs.high == 50
    # Dragging further right keeps moving the high handle.
    rs._set_active_from_x(rs._handle_x(80))
    assert rs.values() == (0, 80)


def test_coincident_at_max_press_left_moves_low(qtbot):
    rs = _slider(qtbot, minimum=0, maximum=100, low=100, high=100)
    mid = rs._track_rect().center().x()
    assert rs._nearest_handle(mid) == "low"
    rs._active = rs._nearest_handle(mid)
    rs._set_active_from_x(mid)
    assert rs.values() == (50, 100)


def test_keyboard_steps_low_handle(qtbot):
    # Arrows step the focused handle ('low' until a handle is pressed) by
    # the single step and emit valuesChanged.
    rs = _slider(qtbot, minimum=0, maximum=100, low=20, high=80, step=5)
    seen = []
    rs.valuesChanged.connect(lambda lo, hi: seen.append((lo, hi)))
    qtbot.keyClick(rs, Qt.Key.Key_Right)
    assert rs.values() == (25, 80)
    assert seen == [(25, 80)]
    qtbot.keyClick(rs, Qt.Key.Key_Down)
    assert rs.values() == (20, 80)
    qtbot.keyClick(rs, Qt.Key.Key_End)  # stops at the other handle
    assert rs.values() == (80, 80)


def test_keyboard_steps_last_pressed_handle(qtbot):
    rs = _slider(qtbot, minimum=0, maximum=100, low=20, high=80)
    # Press exactly on the high handle: it becomes the keyboard target.
    hx = rs._handle_x(80)
    qtbot.mousePress(
        rs, Qt.MouseButton.LeftButton, pos=QPointF(hx, 20).toPoint()
    )
    qtbot.mouseRelease(rs, Qt.MouseButton.LeftButton)
    assert rs._focus_handle == "high"
    qtbot.keyClick(rs, Qt.Key.Key_Left)
    assert rs.values() == (20, 79)


def test_keyboard_divisions_step_one_stop(qtbot):
    rs = _slider(qtbot, minimum=0, maximum=100, low=0, high=100, divisions=4)
    qtbot.keyClick(rs, Qt.Key.Key_Right)
    assert rs.values() == (25, 100)


def test_hover_tracks_near_handle(qtbot):
    rs = _slider(qtbot, minimum=0, maximum=100, low=20, high=80)
    for value, expected in ((20, "low"), (80, "high")):
        pos = QPointF(rs._handle_x(value), 20)
        ev = QMouseEvent(
            QEvent.Type.MouseMove,
            pos,
            pos,
            Qt.MouseButton.NoButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(rs, ev)
        assert rs._hover == expected
    rs.leaveEvent(QEvent(QEvent.Type.Leave))
    assert rs._hover is None


def test_rtl_mapping_mirrors(qtbot):
    rs = _slider(qtbot, minimum=0, maximum=100, low=25, high=75)
    track = rs._track_rect()
    ltr_x = rs._handle_x(25)
    rs.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    rtl_x = rs._handle_x(25)
    assert abs((ltr_x - track.left()) - (track.right() - rtl_x)) < 1e-6
    assert rs._value_from_x(rtl_x) == 25
    # Under RTL the low handle sits to the right of the high handle.
    assert rs._handle_x(25) > rs._handle_x(75)


def test_rtl_keys_mirror(qtbot):
    rs = _slider(qtbot, minimum=0, maximum=100, low=20, high=80)
    rs.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    qtbot.keyClick(rs, Qt.Key.Key_Left)  # RTL: Left steps toward maximum
    assert rs.values() == (21, 80)
    qtbot.keyClick(rs, Qt.Key.Key_Right)
    assert rs.values() == (20, 80)


def test_renders(qtbot):
    rs = _slider(qtbot, low=25, high=75)
    rs.grab()
    rs2 = _slider(qtbot, low=20, high=80, divisions=5)
    rs2.grab()
