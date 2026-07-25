"""Tests for MdDismissible."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from material_qt import core
from material_qt.widgets.dismissible import (
    DismissDirection,
    MdDismissible,
    resolve_dismiss,
)
from material_qt.widgets.dismissible import dismissible as mod

D = DismissDirection


# -- pure seam: resolve_dismiss ---------------------------------------------

def test_resolve_horizontal_right_past_threshold():
    assert resolve_dismiss(D.HORIZONTAL, 60, 0, 100, 50, 0.4) == D.START_TO_END


def test_resolve_horizontal_left_past_threshold():
    assert resolve_dismiss(D.HORIZONTAL, -60, 0, 100, 50, 0.4) == D.END_TO_START


def test_resolve_exactly_at_threshold_dismisses():
    # frac == threshold counts as dismiss (>=).
    assert resolve_dismiss(D.HORIZONTAL, 40, 0, 100, 50, 0.4) == D.START_TO_END


def test_resolve_below_threshold_springs_back():
    assert resolve_dismiss(D.HORIZONTAL, 39, 0, 100, 50, 0.4) is None


def test_resolve_wrong_direction_on_single_axis():
    # END_TO_START only allows leftward; a rightward drag must not dismiss.
    assert resolve_dismiss(D.END_TO_START, 80, 0, 100, 50, 0.4) is None
    assert resolve_dismiss(D.END_TO_START, -80, 0, 100, 50, 0.4) == D.END_TO_START


def test_resolve_vertical_up_and_down():
    assert resolve_dismiss(D.VERTICAL, 0, -40, 100, 50, 0.4) == D.UP
    assert resolve_dismiss(D.VERTICAL, 0, 40, 100, 50, 0.4) == D.DOWN


def test_resolve_zero_extent_is_safe():
    assert resolve_dismiss(D.HORIZONTAL, 50, 0, 0, 0, 0.4) is None


# -- dismiss lifecycle (motion off -> synchronous) --------------------------

def _wrap(qtbot):
    host = QWidget()
    lay = QVBoxLayout(host)
    d = MdDismissible(QLabel("row"), direction=D.HORIZONTAL)
    lay.addWidget(d)
    qtbot.addWidget(host)
    host.resize(200, 80)
    return host, d


def test_dismiss_emits_once_and_hides(qtbot):
    mod.MOTION_ENABLED = False
    try:
        host, d = _wrap(qtbot)
        emitted: list[object] = []
        d.dismissed.connect(emitted.append)
        d.dismiss(D.END_TO_START)
        assert emitted == [D.END_TO_START]
        assert d.isHidden()
    finally:
        mod.MOTION_ENABLED = True


def test_second_dismiss_is_noop(qtbot):
    mod.MOTION_ENABLED = False
    try:
        host, d = _wrap(qtbot)
        emitted: list[object] = []
        d.dismissed.connect(emitted.append)
        d.dismiss(D.START_TO_END)
        d.dismiss(D.END_TO_START)  # already dismissed -> ignored
        assert emitted == [D.START_TO_END]
    finally:
        mod.MOTION_ENABLED = True


def test_confirm_reject_springs_back_no_emit(qtbot):
    mod.MOTION_ENABLED = False
    try:
        host = QWidget()
        lay = QVBoxLayout(host)
        d = MdDismissible(QLabel("row"), direction=D.HORIZONTAL,
                          confirm=lambda direction: False)
        lay.addWidget(d)
        qtbot.addWidget(host)
        host.resize(200, 80)
        emitted: list[object] = []
        d.dismissed.connect(emitted.append)
        # Simulate a past-threshold drag, then release through the confirm gate.
        d.set_offset(150.0)
        d._release()
        assert emitted == []
        assert d.get_offset() == 0.0  # sprang back
        assert not d.isHidden()
    finally:
        mod.MOTION_ENABLED = True


def test_collapse_shrinks_size_hint(qtbot):
    mod.MOTION_ENABLED = False
    try:
        host, d = _wrap(qtbot)
        full = d.sizeHint().height()
        assert full > 0
        d.dismiss(D.END_TO_START)
        assert d.sizeHint().height() == 0  # collapsed perpendicular extent
    finally:
        mod.MOTION_ENABLED = True


# -- drag layer (event filter) ----------------------------------------------

def _send_mouse(widget, type_, x, y, *, button, buttons):
    local = QPointF(x, y)
    gp = QPointF(widget.mapToGlobal(QPoint(int(x), int(y))))
    ev = QMouseEvent(type_, local, local, gp, button, buttons,
                     Qt.KeyboardModifier.NoModifier)
    # sendEvent (not .event()) so installed event filters run.
    QApplication.sendEvent(widget, ev)


def _press(widget, x, y):
    _send_mouse(widget, QEvent.Type.MouseButtonPress, x, y,
                button=Qt.MouseButton.LeftButton,
                buttons=Qt.MouseButton.LeftButton)


def _move(widget, x, y):
    _send_mouse(widget, QEvent.Type.MouseMove, x, y,
                button=Qt.MouseButton.NoButton,
                buttons=Qt.MouseButton.LeftButton)


def _release(widget, x, y):
    _send_mouse(widget, QEvent.Type.MouseButtonRelease, x, y,
                button=Qt.MouseButton.LeftButton,
                buttons=Qt.MouseButton.NoButton)


def test_new_drag_stops_spring_back_and_can_dismiss(qtbot):
    # Motion stays ON: the spring-back animation must be cancelled by a new
    # press, not keep writing offset under the user's drag.
    assert core.motion.MOTION_ENABLED is True
    host, d = _wrap(qtbot)
    host.show()
    qtbot.waitExposed(host)
    label = d.content

    _press(label, 10, 10)
    _move(label, 40, 10)  # +30px: claimed, below threshold
    _release(label, 40, 10)
    assert d._settle_anim is not None  # spring-back running

    _press(label, 10, 10)  # grab the row mid-spring
    assert d._settle_anim is None
    grabbed = d.get_offset()
    qtbot.wait(50)
    assert d.get_offset() == grabbed  # nothing is animating it any more

    with qtbot.waitSignal(d.dismissed, timeout=2000) as blocker:
        _move(label, 150, 10)  # well past threshold
        _release(label, 150, 10)
    assert blocker.args == [D.START_TO_END]


def test_claimed_swipe_unpresses_child_button(qtbot):
    mod.MOTION_ENABLED = False
    try:
        host = QWidget()
        lay = QVBoxLayout(host)
        content = QWidget()
        inner = QVBoxLayout(content)
        btn = QPushButton("act")
        inner.addWidget(btn)
        d = MdDismissible(content, direction=D.HORIZONTAL)
        lay.addWidget(d)
        qtbot.addWidget(host)
        host.resize(200, 80)
        host.show()
        clicks: list[int] = []
        btn.clicked.connect(lambda: clicks.append(1))

        _press(btn, 5, 5)
        assert btn.isDown()
        _move(btn, 35, 5)  # past the claim distance -> swipe owns the gesture
        assert not btn.isDown()  # child press cancelled, not left stuck
        _release(btn, 35, 5)
        assert not btn.isDown()
        assert clicks == []  # cancelled, not clicked
    finally:
        mod.MOTION_ENABLED = True


# -- one motion-ON test for the real chained animation path -----------------

def test_animated_dismiss_reaches_emit(qtbot):
    # MOTION_ENABLED stays True: fling -> collapse -> emit chain must arrive.
    assert core.motion.MOTION_ENABLED is True
    host, d = _wrap(qtbot)
    host.show()
    qtbot.waitExposed(host)
    with qtbot.waitSignal(d.dismissed, timeout=2000) as blocker:
        d.dismiss(D.START_TO_END)
    assert blocker.args == [D.START_TO_END]
    assert d.isHidden()
