"""Tests for MdTimePicker."""

from __future__ import annotations

from PySide6.QtCore import QTime
from PySide6.QtWidgets import QWidget

from material_qt.widgets.timepicker import (
    MdTimePicker,
    angle_to_hour,
    angle_to_hour24,
    angle_to_minute,
)
from material_qt.widgets.timepicker.timepicker import (
    _DIAL,
    _OUTER_R,
    _ClockDial,
    _hour24_layout,
    _pos,
)

_R = 100  # distance from center; magnitude is irrelevant to the angle


def test_dial_draws_the_hand_line(qtbot):
    # Regression: the face is painted with NoPen; the hand must use its own solid
    # pen or the connecting "stick" silently vanishes (only the hub + knob show).
    from material_qt.theme.theme_manager import ThemeManager
    from material_qt.tokens.color import ColorRole

    dial = _ClockDial()
    dial.set_mode("hour")
    dial.set_values(10, 30)
    qtbot.addWidget(dial)
    img = dial.grab().toImage()

    primary = ThemeManager.instance().color(ColorRole.PRIMARY)
    cx, cy = _DIAL / 2.0, _DIAL / 2.0
    kx, ky = _pos(10, 30.0, cx, cy, _OUTER_R)

    def close(px) -> bool:
        return (abs(px.red() - primary.red()) < 24
                and abs(px.green() - primary.green()) < 24
                and abs(px.blue() - primary.blue()) < 24)

    # Sample the mid-section of the hand, clear of both the centre hub and the
    # knob — those would render even with the bug, so they can't vouch for it.
    hits = sum(
        close(img.pixelColor(round(cx + (kx - cx) * t), round(cy + (ky - cy) * t)))
        for t in (0.4, 0.45, 0.5, 0.55, 0.6)
    )
    assert hits > 0, "no primary-colored pixels along the hand — stick missing"


def test_angle_to_hour_cardinals():
    assert angle_to_hour(0, -_R) == 12  # top
    assert angle_to_hour(_R, 0) == 3    # right
    assert angle_to_hour(0, _R) == 6    # bottom
    assert angle_to_hour(-_R, 0) == 9   # left


def test_angle_to_minute_cardinals():
    assert angle_to_minute(0, -_R) == 0   # top
    assert angle_to_minute(_R, 0) == 15   # right
    assert angle_to_minute(0, _R) == 30   # bottom
    assert angle_to_minute(-_R, 0) == 45  # left


def test_initial_time_round_trips(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    tp = MdTimePicker(host, initial_time=QTime(14, 35))
    assert tp.selected_time == QTime(14, 35)
    # 14:35 -> 2 PM
    assert tp._hour == 2 and tp._minute == 35 and tp._is_pm


def test_ampm_toggle_changes_24h(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    tp = MdTimePicker(host, initial_time=QTime(9, 0))  # 9 AM
    assert tp.selected_time == QTime(9, 0)
    tp._set_pm(True)
    assert tp.selected_time == QTime(21, 0)  # 9 PM


def test_dial_sets_active_field_and_accepts(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    tp = MdTimePicker(host, initial_time=QTime(10, 10))
    got = []
    tp.accepted.connect(got.append)
    tp._set_mode("hour")
    tp._on_dial(3)  # set hour to 3
    tp._set_mode("minute")
    tp._on_dial(30)  # set minute to 30
    tp._on_ok()
    assert got and got[0] == QTime(3, 30)  # 3 AM (initial was AM)


def test_cancel_emits_rejected_and_closed(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    tp = MdTimePicker(host, initial_time=QTime(10, 10))
    rej, clo = [], []
    tp.rejected.connect(lambda: rej.append(True))
    tp.closed.connect(lambda: clo.append(True))
    tp.open()
    tp._on_cancel()
    assert rej == [True] and clo == [True] and tp.isHidden()


def test_renders(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    tp = MdTimePicker(host, initial_time=QTime(10, 10))
    tp.open()
    tp.grab()


# -- input entry mode -----------------------------------------------------

def test_initial_entry_mode_input(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    tp = MdTimePicker(host, initial_time=QTime(10, 10), initial_entry_mode="input")
    assert tp._entry == "input"
    assert tp._display.currentIndex() == 1  # the input page
    assert tp._dial_row.isHidden()
    assert tp._hour_edit.text() == "10" and tp._minute_edit.text() == "10"


def test_toggle_switches_entry_mode(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    tp = MdTimePicker(host, initial_time=QTime(10, 10))  # dial by default
    assert tp._entry == "dial" and not tp._dial_row.isHidden()
    tp._toggle_entry()
    assert tp._entry == "input" and tp._dial_row.isHidden()
    tp._toggle_entry()
    assert tp._entry == "dial" and not tp._dial_row.isHidden()


def test_typing_updates_selected_time(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    tp = MdTimePicker(host, initial_time=QTime(9, 0), initial_entry_mode="input")
    tp._hour_edit.setText("7")
    tp._on_edit_hour("7")
    tp._minute_edit.setText("45")
    tp._on_edit_minute("45")
    assert tp.selected_time == QTime(7, 45)  # still AM
    tp._set_pm(True)
    assert tp.selected_time == QTime(19, 45)


def test_typed_value_clamps(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    tp = MdTimePicker(host, initial_entry_mode="input")
    tp._on_edit_minute("90")  # out of range -> clamped to 59
    assert tp._minute == 59


def test_renders_input_mode(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    tp = MdTimePicker(host, initial_time=QTime(10, 10), initial_entry_mode="input")
    tp.open()
    tp.grab()


# -- 24-hour dual-ring dial -----------------------------------------------

def test_angle_to_hour24_inner_ring_cardinals():
    _r = 100
    assert angle_to_hour24(0, -_r, inner=True) == 12  # top
    assert angle_to_hour24(_r, 0, inner=True) == 3    # right
    assert angle_to_hour24(0, _r, inner=True) == 6    # bottom
    assert angle_to_hour24(-_r, 0, inner=True) == 9   # left


def test_angle_to_hour24_outer_ring_cardinals():
    _r = 100
    assert angle_to_hour24(0, -_r, inner=False) == 0   # top -> 00
    assert angle_to_hour24(_r, 0, inner=False) == 15   # right -> 15 (3 + 12)
    assert angle_to_hour24(0, _r, inner=False) == 18   # bottom -> 18
    assert angle_to_hour24(-_r, 0, inner=False) == 21  # left -> 21


def test_hour24_layout_round_trips_ring_assignment():
    assert _hour24_layout(0) == (0, False)    # 00 outer, top
    assert _hour24_layout(12) == (0, True)    # 12 inner, top
    assert _hour24_layout(3) == (3, True)     # 3 inner
    assert _hour24_layout(15) == (3, False)   # 15 outer
    assert _hour24_layout(23) == (11, False)  # 23 outer, last position


def test_24h_has_no_ampm_and_reports_24h_time(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    tp = MdTimePicker(host, initial_time=QTime(20, 30), hour24=True)
    assert tp._am.isHidden() and tp._pm.isHidden()
    assert tp._hour == 20  # dial value is the 24h hour directly
    assert tp.selected_time == QTime(20, 30)


def test_24h_dial_sets_hour_directly(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    tp = MdTimePicker(host, initial_time=QTime(9, 0), hour24=True)
    tp._on_dial(18)  # the dial emits a 24h hour
    assert tp.selected_time == QTime(18, 0)


def test_24h_input_accepts_0_to_23(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    tp = MdTimePicker(host, hour24=True, initial_entry_mode="input")
    tp._on_edit_hour("23")
    assert tp._hour == 23
    tp._on_edit_hour("40")  # clamps
    assert tp._hour == 23


def test_renders_24h(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    tp = MdTimePicker(host, initial_time=QTime(20, 30), hour24=True)
    tp.open()
    tp.grab()
