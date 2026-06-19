"""Tests for MdDatePicker."""

from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QWidget

from material_qt.widgets.datepicker import MdDatePicker, first_column


def test_first_column_sunday_first():
    # Anchor on weekdays Qt reports, not memory. June 1 2026 is a Monday.
    assert QDate(2026, 6, 1).dayOfWeek() == 1  # 1=Mon
    assert first_column(2026, 6) == 1  # Mon -> column 1 (Sun-first)
    # Feb 1 2026 is a Sunday -> column 0.
    assert QDate(2026, 2, 1).dayOfWeek() == 7
    assert first_column(2026, 2) == 0
    # A Saturday lands in the last column (6).
    assert first_column(2025, 11) == QDate(2025, 11, 1).dayOfWeek() % 7


def test_grid_places_days_at_correct_columns(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    dp = MdDatePicker(host, initial_date=QDate(2026, 6, 15))
    # June 2026 starts Monday (col 1); day 1 sits in cell index 1, day 15 at 15.
    offset = first_column(2026, 6)
    assert dp._cells[offset]._date == QDate(2026, 6, 1)
    assert dp._cells[offset + 14]._date == QDate(2026, 6, 15)
    # Leading cell before the offset is blank.
    assert dp._cells[offset - 1]._date is None


def test_selection_and_accept(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    dp = MdDatePicker(host, initial_date=QDate(2026, 6, 15))
    got = []
    dp.accepted.connect(got.append)
    dp._on_day_clicked(QDate(2026, 6, 20))
    assert dp.selected_date == QDate(2026, 6, 20)
    dp._on_ok()
    assert got == [QDate(2026, 6, 20)]


def test_month_navigation_wraps(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    dp = MdDatePicker(host, initial_date=QDate(2026, 12, 10))
    dp._shift_month(1)
    assert dp._view.year() == 2027 and dp._view.month() == 1


def test_cancel_emits_rejected_and_closed(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    dp = MdDatePicker(host, initial_date=QDate(2026, 6, 15))
    rej, clo = [], []
    dp.rejected.connect(lambda: rej.append(True))
    dp.closed.connect(lambda: clo.append(True))
    dp.open()
    dp._on_cancel()
    assert rej == [True] and clo == [True] and dp.isHidden()


def test_renders(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    dp = MdDatePicker(host, initial_date=QDate(2026, 6, 15))
    dp.open()
    dp.grab()
