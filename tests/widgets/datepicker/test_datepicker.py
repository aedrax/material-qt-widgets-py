"""Tests for MdDatePicker."""

from __future__ import annotations

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

from material_qt.widgets.datepicker import (
    MdCalendarDatePicker,
    MdDatePicker,
    day_enabled,
    first_column,
)
from material_qt.widgets.iconbutton import MdIconButton


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


def test_close_does_not_leave_focus_ring_on_sibling(qtbot):
    # Closing the modal (hide) while a button inside it holds focus must not make
    # Qt reassign TabFocusReason focus to a sibling focusable widget — that would
    # spuriously show the sibling's keyboard focus ring (cf. the OK button / the
    # app bar theme toggle in the gallery).
    host = QWidget()
    host.resize(600, 600)
    layout = QVBoxLayout(host)
    sibling = MdIconButton("dark_mode")  # focus_ring=True
    layout.addWidget(sibling)
    qtbot.addWidget(host)
    host.show()
    # Focus only transfers between widgets while the top-level window is active;
    # offscreen windows aren't auto-activated, so force it for the repro.
    QApplication.setActiveWindow(host)

    dp = MdDatePicker(host, initial_date=QDate(2026, 6, 15))
    dp.open()
    # Mimic the user clicking OK: the button takes mouse focus, then OK closes.
    dp._ok.setFocus(Qt.FocusReason.MouseFocusReason)
    dp._on_ok()

    assert dp.isHidden()
    assert not sibling.hasFocus()
    assert not sibling.focus_ring.visible


def test_renders(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    dp = MdDatePicker(host, initial_date=QDate(2026, 6, 15))
    dp.open()
    dp.grab()


# -- range / predicate ----------------------------------------------------


def test_day_enabled_helper():
    lo, hi = QDate(2026, 6, 10), QDate(2026, 6, 20)
    assert not day_enabled(QDate(2026, 6, 9), first_date=lo, last_date=hi, predicate=None)
    assert day_enabled(QDate(2026, 6, 10), first_date=lo, last_date=hi, predicate=None)
    assert day_enabled(QDate(2026, 6, 20), first_date=lo, last_date=hi, predicate=None)
    assert not day_enabled(QDate(2026, 6, 21), first_date=lo, last_date=hi, predicate=None)
    # Open-ended bounds.
    assert day_enabled(QDate(1900, 1, 1), first_date=None, last_date=hi, predicate=None)
    # Predicate veto.
    weekday = lambda d: d.dayOfWeek() <= 5  # noqa: E731
    sat = QDate(2026, 6, 13)
    assert sat.dayOfWeek() == 6
    assert not day_enabled(sat, first_date=None, last_date=None, predicate=weekday)


def test_range_disables_out_of_range_cells(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    dp = MdDatePicker(
        host,
        initial_date=QDate(2026, 6, 15),
        first_date=QDate(2026, 6, 10),
        last_date=QDate(2026, 6, 20),
    )
    offset = first_column(2026, 6)
    # Day 5 is before firstDate -> disabled and inert.
    cell5 = dp._cells[offset + 4]
    assert cell5._date == QDate(2026, 6, 5)
    assert cell5._enabled is False
    # Clicking a disabled cell does not change the selection.
    before = dp.selected_date
    cell5.mousePressEvent(_press_event(cell5))
    assert dp.selected_date == before
    # Day 15 is in range and selectable.
    assert dp._cells[offset + 14]._enabled is True


def test_predicate_disables_and_ok_gating(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    # Only even days selectable.
    dp = MdDatePicker(
        host,
        initial_date=QDate(2026, 6, 14),
        selectable_day_predicate=lambda d: d.day() % 2 == 0,
    )
    assert dp._ok.isEnabled()  # 14 is even
    # Selecting an odd day is impossible via cells, but a programmatic out-of-range
    # selection must disable OK rather than emit an invalid date.
    dp._selected = QDate(2026, 6, 13)
    dp._refresh()
    assert not dp._ok.isEnabled()


def test_current_date_override(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    dp = MdDatePicker(
        host,
        initial_date=QDate(2026, 6, 15),
        current_date=QDate(2026, 6, 3),
    )
    offset = first_column(2026, 6)
    assert dp._cells[offset + 2]._today is True   # June 3 marked today
    assert dp._cells[offset + 14]._today is False  # June 15 is selected, not today


def test_custom_text(qtbot):
    host = QWidget()
    host.resize(600, 600)
    qtbot.addWidget(host)
    dp = MdDatePicker(
        host,
        confirm_text="Done",
        cancel_text="Nope",
        help_text="Pick a day",
    )
    assert dp._support.text() == "Pick a day"


# -- inline calendar (MdCalendarDatePicker) -------------------------------


def test_calendar_inline_emits_date_changed(qtbot):
    host = QWidget()
    qtbot.addWidget(host)
    cal = MdCalendarDatePicker(host, initial_date=QDate(2026, 6, 15))
    got = []
    cal.dateChanged.connect(got.append)
    offset = first_column(2026, 6)
    assert cal._cells[offset + 14]._date == QDate(2026, 6, 15)
    cal._on_day_clicked(QDate(2026, 6, 20))
    assert got == [QDate(2026, 6, 20)]
    assert cal.selected_date == QDate(2026, 6, 20)


def test_calendar_inline_month_change_signal(qtbot):
    host = QWidget()
    qtbot.addWidget(host)
    cal = MdCalendarDatePicker(host, initial_date=QDate(2026, 12, 10))
    months = []
    cal.displayedMonthChanged.connect(months.append)
    cal._shift_month(1)
    assert cal.displayed_month == QDate(2027, 1, 1)
    assert months == [QDate(2027, 1, 1)]


def test_calendar_inline_range_disables(qtbot):
    host = QWidget()
    qtbot.addWidget(host)
    cal = MdCalendarDatePicker(
        host,
        initial_date=QDate(2026, 6, 15),
        first_date=QDate(2026, 6, 10),
        last_date=QDate(2026, 6, 20),
    )
    offset = first_column(2026, 6)
    assert cal._cells[offset + 4]._enabled is False   # June 5
    assert cal._cells[offset + 14]._enabled is True   # June 15


def _press_event(widget):
    from PySide6.QtCore import QPointF
    from PySide6.QtGui import QMouseEvent

    return QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPointF(1, 1),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
