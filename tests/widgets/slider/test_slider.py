"""Tests for MdSlider."""

from __future__ import annotations

from PySide6.QtCore import Qt

from material_qt.widgets.slider import MdSlider


def test_value_range(qtbot):
    s = MdSlider(minimum=0, maximum=100, value=25)
    qtbot.addWidget(s)
    assert s.value() == 25
    s.setValue(80)
    assert s.value() == 80


def test_value_changed_signal(qtbot):
    s = MdSlider(value=0)
    qtbot.addWidget(s)
    seen = []
    s.valueChanged.connect(seen.append)
    s.setValue(50)
    assert seen == [50]


def test_discrete_snaps(qtbot):
    s = MdSlider(minimum=0, maximum=100, value=0, step=10, ticks=True)
    qtbot.addWidget(s)
    s.resize(s.sizeHint())
    # Map a pixel near the middle to a stepped value.
    v = s._value_from_x(s._track_rect().left() + s._track_rect().width() * 0.47)
    assert v % 10 == 0


def test_keyboard_steps(qtbot):
    s = MdSlider(minimum=0, maximum=10, value=5, step=1)
    qtbot.addWidget(s)
    s.setValue(5)
    s.triggerAction(MdSlider.SliderAction.SliderSingleStepAdd)
    assert s.value() == 6


def test_renders(qtbot):
    for kw in ({"value": 40}, {"value": 60, "step": 10, "ticks": True}):
        s = MdSlider(**kw)
        qtbot.addWidget(s)
        s.resize(s.sizeHint())
        s.grab()
