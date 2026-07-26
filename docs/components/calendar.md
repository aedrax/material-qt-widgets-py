# Calendar

Inline calendar for selecting a date.

**Classes:** `MdCalendarDatePicker` · **Source:** `src/material_qt/widgets/datepicker/`
**Spec:** <https://api.flutter.dev/flutter/material/CalendarDatePicker-class.html> (Flutter `CalendarDatePicker`; the modal form is in the M3 catalogue at <https://m3.material.io/components/date-pickers>).

This is the inline (non-modal) sibling of the modal [date picker](./date-picker.md), shipped in the same `datepicker/` package.

## Usage

```python
from material_qt import MdCalendarDatePicker

cal = MdCalendarDatePicker(parent=page)
cal.dateChanged.connect(lambda d: print(d.toString("dddd, MMMM d, yyyy")))
layout.addWidget(cal)
```

## API

### MdCalendarDatePicker

An inline (non-modal) Material calendar: a docked month grid with the same month-navigation row, weekday header, and 6x7 day grid as the modal `MdDatePicker`, reusing the shared `first_column` helper and day-cell primitive. Unlike the modal it has no scrim, header headline, or OK/Cancel — selecting a day emits `dateChanged` directly.

```python
MdCalendarDatePicker(
    parent: QWidget | None = None,
    *,
    initial_date: QDate | None = None,
    first_date: QDate | None = None,
    last_date: QDate | None = None,
    current_date: QDate | None = None,
    selectable_day_predicate: SelectableDayPredicate | None = None,
)
```

- `selected_date` — property; the currently selected `QDate` (defaults to `initial_date`, falling back to `current_date` / today).
- `displayed_month` — property; a `QDate` for the first day of the month currently shown in the grid.
- `is_selectable(date)` — whether `date` is within `[first_date, last_date]` and passes the predicate.

**Signals:**

- `dateChanged = Signal(QDate)` — emitted immediately when a day is clicked (there is no confirm step).
- `displayedMonthChanged = Signal(QDate)` — emitted when the chevron buttons page to another month; the payload is the new month's first day.

The package also exports the pure helpers `first_column(year, month)` (Sunday-first grid column of the month's 1st) and `day_enabled(date, *, first_date, last_date, predicate)` (the range + predicate selectability test); both are shared with the modal picker.

## Notes

- Signal names are camelCase (`dateChanged`, `displayedMonthChanged`), matching the Flutter `CalendarDatePicker` callbacks they port — unlike the modal picker's `accepted`.
- Selection commits instantly: every click on a selectable day both updates `selected_date` and emits `dateChanged`. Out-of-range or predicate-rejected days dim to 38% and are inert.
- `current_date` controls which day is ringed as "today" (defaults to `QDate.currentDate()`); the selected day is a `primary` filled circle.
- The widget has a fixed 328px width. It paints no surface of its own, so it sits directly on the parent's background.
- The grid is hardcoded Sunday-first; locale-driven first-day-of-week is a deliberate deferral shared with the modal picker.
- Unlike the modal picker, there is no month/year toggle — the year picker grid exists only in [MdDatePicker](./date-picker.md). Use the chevrons to page months.
