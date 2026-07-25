"""Tests for MdDraggableScrollableSheet."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from material_qt import core
from material_qt.widgets.draggablesheet import (
    MdDraggableScrollableSheet,
    clamp_size,
    couple_wheel,
    nearest_snap,
)
from material_qt.widgets.draggablesheet import draggablesheet as mod


# -- pure seams -------------------------------------------------------------

def test_clamp_size():
    assert clamp_size(0.5, 0.25, 1.0) == 0.5
    assert clamp_size(0.1, 0.25, 1.0) == 0.25
    assert clamp_size(2.0, 0.25, 1.0) == 1.0


def test_nearest_snap():
    assert nearest_snap(0.55, [0.25, 0.5, 1.0]) == 0.5
    assert nearest_snap(0.9, [0.25, 0.5, 1.0]) == 1.0
    assert nearest_snap(0.3, []) == 0.3  # no snaps -> unchanged


# couple_wheel truth table (angle_y >0 = toward top, <0 = toward bottom).
def test_couple_wheel_down_below_max_grows():
    assert couple_wheel(-120, True, 0.5, 0.25, 1.0) == "grow"


def test_couple_wheel_down_at_max_scrolls():
    assert couple_wheel(-120, True, 1.0, 0.25, 1.0) == "scroll"


def test_couple_wheel_up_not_at_top_scrolls():
    assert couple_wheel(120, False, 0.5, 0.25, 1.0) == "scroll"


def test_couple_wheel_up_at_top_above_min_shrinks():
    assert couple_wheel(120, True, 0.5, 0.25, 1.0) == "shrink"


def test_couple_wheel_up_at_top_at_min_scrolls():
    assert couple_wheel(120, True, 0.25, 0.25, 1.0) == "scroll"


def test_couple_wheel_zero_is_scroll():
    assert couple_wheel(0, True, 0.5, 0.25, 1.0) == "scroll"


# -- controller API (motion off -> synchronous) ----------------------------

def _sheet(qtbot, **kw):
    host = QWidget()
    qtbot.addWidget(host)
    host.resize(400, 600)
    sheet = MdDraggableScrollableSheet(host, **kw)
    for i in range(20):
        sheet.add_content(QLabel(f"Item {i}"))
    return host, sheet


def test_initial_size_clamped(qtbot):
    host, sheet = _sheet(qtbot, initial_size=2.0, min_size=0.2, max_size=0.8)
    assert sheet.size_fraction == 0.8


def test_set_frac_clamps_and_emits(qtbot):
    mod.MOTION_ENABLED = False
    try:
        host, sheet = _sheet(qtbot, initial_size=0.5, min_size=0.25, max_size=0.9)
        seen: list[float] = []
        sheet.sizeChanged.connect(seen.append)
        sheet.set_size(0.7)
        assert sheet.size_fraction == 0.7
        sheet.set_size(5.0)  # clamps to max
        assert sheet.size_fraction == 0.9
        assert seen == [0.7, 0.9]
    finally:
        mod.MOTION_ENABLED = True


def test_geometry_tracks_fraction(qtbot):
    mod.MOTION_ENABLED = False
    try:
        host, sheet = _sheet(qtbot, initial_size=0.5)
        host.show()
        qtbot.waitExposed(host)
        sheet.set_size(0.5)
        # 600px host * 0.5 = 300px tall, anchored to the bottom.
        assert abs(sheet.height() - 300) <= 2
        assert abs(sheet.y() - 300) <= 2
    finally:
        mod.MOTION_ENABLED = True


def test_reset_returns_to_initial(qtbot):
    mod.MOTION_ENABLED = False
    try:
        host, sheet = _sheet(qtbot, initial_size=0.4, min_size=0.2, max_size=0.9)
        sheet.set_size(0.9)
        sheet.reset()
        assert sheet.size_fraction == 0.4
    finally:
        mod.MOTION_ENABLED = True


# -- handle drag vs animation races (motion ON) ------------------------------

def _send_mouse(widget, type_, x, y, *, button, buttons):
    local = QPointF(x, y)
    gp = QPointF(widget.mapToGlobal(QPoint(int(x), int(y))))
    ev = QMouseEvent(type_, local, local, gp, button, buttons,
                     Qt.KeyboardModifier.NoModifier)
    QApplication.sendEvent(widget, ev)


def test_new_handle_drag_stops_snap_animation(qtbot):
    # The snap animation must not keep writing `frac` while the user holds the
    # handle — that yanked the sheet out of the user's hand.
    assert core.motion.MOTION_ENABLED is True
    host, sheet = _sheet(qtbot, initial_size=0.5, min_size=0.25, max_size=0.9,
                         snap_sizes=[0.5])
    host.show()
    qtbot.waitExposed(host)

    # Drag the handle up a bit and release: snap animation starts.
    _send_mouse(sheet, QEvent.Type.MouseButtonPress, 200, 10,
                button=Qt.MouseButton.LeftButton, buttons=Qt.MouseButton.LeftButton)
    _send_mouse(sheet, QEvent.Type.MouseMove, 200, -80,
                button=Qt.MouseButton.NoButton, buttons=Qt.MouseButton.LeftButton)
    _send_mouse(sheet, QEvent.Type.MouseButtonRelease, 200, -80,
                button=Qt.MouseButton.LeftButton, buttons=Qt.MouseButton.NoButton)
    assert sheet._snap_anim is not None  # snapping

    # Grab the handle again mid-snap: the animation must stop immediately.
    _send_mouse(sheet, QEvent.Type.MouseButtonPress, 200, 10,
                button=Qt.MouseButton.LeftButton, buttons=Qt.MouseButton.LeftButton)
    assert sheet._snap_anim is None
    grabbed = sheet.size_fraction
    qtbot.wait(50)
    assert sheet.size_fraction == grabbed  # nothing else is driving frac


def test_overlapping_animate_to_lands_on_last_target(qtbot):
    assert core.motion.MOTION_ENABLED is True
    host, sheet = _sheet(qtbot, initial_size=0.5, min_size=0.2, max_size=0.9)
    host.show()
    qtbot.waitExposed(host)
    sheet.animate_to(0.9)
    sheet.animate_to(0.3)  # must cancel the first, not run both concurrently
    qtbot.waitUntil(lambda: abs(sheet.size_fraction - 0.3) < 1e-2, timeout=2000)
    qtbot.wait(50)  # a surviving first animation would keep moving it
    assert abs(sheet.size_fraction - 0.3) < 1e-2


# -- one motion-ON test for the animated path -------------------------------

def test_animate_to_reaches_target(qtbot):
    assert core.motion.MOTION_ENABLED is True
    host, sheet = _sheet(qtbot, initial_size=0.3, min_size=0.2, max_size=0.9)
    host.show()
    qtbot.waitExposed(host)
    seen: list[float] = []
    sheet.sizeChanged.connect(seen.append)
    sheet.animate_to(0.8)
    qtbot.waitUntil(lambda: abs(sheet.size_fraction - 0.8) < 1e-2, timeout=2000)
    assert seen  # ticks were emitted
    assert abs(seen[-1] - 0.8) < 1e-2
