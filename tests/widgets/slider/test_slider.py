"""Tests for MdSlider."""

from __future__ import annotations

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


def test_divisions_snap_constructor(qtbot):
    # 4 divisions over 0..100 → stops at 0/25/50/75/100; 40 snaps to 50.
    s = MdSlider(minimum=0, maximum=100, value=40, divisions=4)
    qtbot.addWidget(s)
    assert s.divisions == 4
    assert s.value() == 50


def test_divisions_snap_seam(qtbot):
    s = MdSlider(minimum=0, maximum=100, divisions=4)
    qtbot.addWidget(s)
    # Nearest of {0,25,50,75,100}.
    assert s._snap(10) == 0
    assert s._snap(13) == 25
    assert s._snap(60) == 50
    assert s._snap(99) == 100
    # Out-of-range clamps.
    assert s._snap(-5) == 0
    assert s._snap(500) == 100


def test_divisions_uneven_span(qtbot):
    # 3 divisions over 0..100 → 0/33/67/100 (rounded to int).
    s = MdSlider(minimum=0, maximum=100, divisions=3)
    qtbot.addWidget(s)
    assert s._snap(40) == 33
    assert s._snap(50) == 67  # 1.5 rounds to even (2) → 2*100/3 ≈ 67
    assert s._snap(90) == 100


def test_set_divisions_resnaps(qtbot):
    s = MdSlider(minimum=0, maximum=100, value=40)
    qtbot.addWidget(s)
    assert s.value() == 40  # continuous: no snap
    s.set_divisions(2)  # stops 0/50/100
    assert s.divisions == 2
    assert s.value() == 50


def test_divisions_value_from_x_snaps(qtbot):
    s = MdSlider(minimum=0, maximum=100, divisions=4)
    qtbot.addWidget(s)
    s.resize(s.sizeHint())
    track = s._track_rect()
    v = s._value_from_x(track.left() + track.width() * 0.47)
    assert v in (0, 25, 50, 75, 100)


def test_divisions_keyboard_stays_on_stops(qtbot):
    # Keyboard/wheel/page input must also snap to division stops, not the
    # default singleStep of 1.
    s = MdSlider(minimum=0, maximum=100, value=50, divisions=4)
    qtbot.addWidget(s)
    s.triggerAction(MdSlider.SliderAction.SliderSingleStepAdd)
    assert s.value() in (0, 25, 50, 75, 100)
    assert s.value() == 75


def test_pressed_released_signals(qtbot):
    # onChangeStart/onChangeEnd parity: native QAbstractSlider signals fire.
    s = MdSlider(minimum=0, maximum=100, value=50)
    qtbot.addWidget(s)
    events = []
    s.sliderPressed.connect(lambda: events.append("start"))
    s.sliderReleased.connect(lambda: events.append("end"))
    s.setSliderDown(True)
    s.setSliderDown(False)
    assert events == ["start", "end"]


def test_renders(qtbot):
    for kw in (
        {"value": 40},
        {"value": 60, "step": 10, "ticks": True},
        {"value": 40, "divisions": 5, "labeled": True},
    ):
        s = MdSlider(**kw)
        qtbot.addWidget(s)
        s.resize(s.sizeHint())
        s.grab()
