"""Tests for MdSwitch."""

from __future__ import annotations

from material_qt.widgets.switch import MdSwitch


def test_toggle(qtbot):
    sw = MdSwitch()
    qtbot.addWidget(sw)
    states = []
    sw.toggled.connect(states.append)
    sw.toggle()
    assert sw.isChecked() is True
    assert states == [True]


def test_size(qtbot):
    sw = MdSwitch()
    qtbot.addWidget(sw)
    assert sw.sizeHint().width() == 52
    assert sw.sizeHint().height() == 40


def test_handle_moves_with_state(qtbot):
    sw = MdSwitch()
    qtbot.addWidget(sw)
    sw.resize(sw.sizeHint())
    off_x, _ = sw._handle_center()
    sw.setChecked(True)
    on_x, _ = sw._handle_center()
    assert on_x > off_x


def test_renders(qtbot):
    for kw in ({}, {"checked": True}):
        sw = MdSwitch(**kw)
        qtbot.addWidget(sw)
        sw.resize(sw.sizeHint())
        sw.grab()
    sw = MdSwitch(checked=True)
    qtbot.addWidget(sw)
    sw.setEnabled(False)
    sw.resize(sw.sizeHint())
    sw.grab()


def test_focus_ring(qtbot):
    sw = MdSwitch()
    qtbot.addWidget(sw)
    assert sw.focus_ring is not None


def test_repeated_toggle_with_animation_settle(qtbot):
    """Regression: a finished animation must not leave a stale C++ object that
    crashes the next toggle (persistent-animation fix)."""
    from PySide6.QtTest import QTest

    sw = MdSwitch()
    qtbot.addWidget(sw)
    sw.show()
    for _ in range(4):
        sw.toggle()
        QTest.qWait(250)  # let the 200ms animation fully finish between toggles
    assert sw.isChecked() is False
