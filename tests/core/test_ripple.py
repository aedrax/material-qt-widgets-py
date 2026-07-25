"""Tests for the RippleController (core/ripple.py)."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from material_qt.widgets.button import MdFilledButton


def _mouse_event(etype, pos: QPointF) -> QMouseEvent:
    buttons = (
        Qt.MouseButton.NoButton
        if etype == QEvent.Type.MouseButtonRelease
        else Qt.MouseButton.LeftButton
    )
    return QMouseEvent(
        etype,
        pos,
        Qt.MouseButton.LeftButton,
        buttons,
        Qt.KeyboardModifier.NoModifier,
    )


def test_double_click_begins_second_press_ripple(qtbot):
    """Regression: Qt delivers the second press of a double-click as a
    MouseButtonDblClick event, which must begin a press ripple like a plain
    press (it used to be treated as a release, so the second click never
    rippled)."""
    b = MdFilledButton("OK")
    qtbot.addWidget(b)
    b.resize(b.sizeHint())
    ctl = b.ripple
    begun = []
    orig = ctl._start_press

    def counting(origin):
        begun.append(1)
        orig(origin)

    ctl._start_press = counting
    pos = QPointF(5.0, 5.0)
    # sendEvent so the ripple's installed event filter sees the events.
    QApplication.sendEvent(b, _mouse_event(QEvent.Type.MouseButtonPress, pos))
    QApplication.sendEvent(b, _mouse_event(QEvent.Type.MouseButtonRelease, pos))
    QApplication.sendEvent(b, _mouse_event(QEvent.Type.MouseButtonDblClick, pos))
    QApplication.sendEvent(b, _mouse_event(QEvent.Type.MouseButtonRelease, pos))
    assert len(begun) == 2


def test_release_still_ends_press(qtbot):
    b = MdFilledButton("OK")
    qtbot.addWidget(b)
    b.resize(b.sizeHint())
    ctl = b.ripple
    pos = QPointF(5.0, 5.0)
    QApplication.sendEvent(b, _mouse_event(QEvent.Type.MouseButtonPress, pos))
    assert ctl._pressed is True
    QApplication.sendEvent(b, _mouse_event(QEvent.Type.MouseButtonRelease, pos))
    # The minimum-press guard may defer the fade, but the release must be
    # registered (either already faded or pending).
    assert ctl._pressed is False or ctl._release_pending is True
