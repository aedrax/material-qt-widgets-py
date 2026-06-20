"""Tests for MdTimePicker."""

from __future__ import annotations

from PySide6.QtCore import QTime
from PySide6.QtWidgets import QWidget

from material_qt.widgets.timepicker import (
    MdTimePicker,
    angle_to_hour,
    angle_to_minute,
)

_R = 100  # distance from center; magnitude is irrelevant to the angle


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
