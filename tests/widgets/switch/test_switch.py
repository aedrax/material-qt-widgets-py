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
