# Date picker

Select a date from a calendar.

**Classes:** `MdDatePicker` · **Source:** `src/material_qt/widgets/datepicker/`
**Spec:** <https://m3.material.io/components/date-pickers>. Ports the Material 3 modal date picker (cf. Flutter's `showDatePicker` / `CalendarDatePicker`).

For the inline (non-modal) calendar from the same package, see [calendar](./calendar.md).

## Usage

```python
from material_qt import MdDatePicker

picker = MdDatePicker(window)
picker.closed.connect(picker.deleteLater)
picker.accepted.connect(lambda d: print(d.toString("dddd, MMMM d, yyyy")))
picker.open()
```

## API

### MdDatePicker

A modal date picker overlay: an elevated `surface-container-high` panel with a header (supporting label + the selected date as a headline), a month navigation row, a weekday row, a 6x7 day grid, and Cancel / OK actions. Extends `core.ModalOverlay` (see [architecture: modal overlay](../architecture.md#modal-overlay)).

```python
MdDatePicker(
    parent: QWidget,
    *,
    initial_date: QDate | None = None,
    first_date: QDate | None = None,
    last_date: QDate | None = None,
    current_date: QDate | None = None,
    selectable_day_predicate: SelectableDayPredicate | None = None,
    confirm_text: str = "OK",
    cancel_text: str = "Cancel",
    help_text: str = "Select date",
)
```

- `open()` — inherited from `ModalOverlay`; shows the overlay over its parent with a fading scrim and slight panel rise.
- `dismiss()` — inherited; reject and close (also triggered by a scrim click, Escape, or Cancel).
- `selected_date` — property; the currently selected `QDate` (defaults to `initial_date`, falling back to `current_date` / today).
- `is_selectable(date)` — whether `date` is within `[first_date, last_date]` and passes the predicate.

**Signals:**

- `accepted = Signal(QDate)` — fires on OK with the selected date.
- `rejected = Signal()` — inherited from `ModalOverlay`; fires on Cancel, Escape, or a scrim click.
- `closed = Signal()` — inherited from `ModalOverlay`; fires whenever the overlay closes (accept or reject).

Helper functions exported by the package: `first_column(year, month)` returns the Sunday-first grid column of the month's 1st, and `day_enabled(date, *, first_date, last_date, predicate)` is the range + predicate selectability test (`SelectableDayPredicate = Callable[[QDate], bool]`, cf. Flutter's `SelectableDayPredicate`).

## Notes

- Behavior inherited from `ModalOverlay`: full-parent scrim (32% opacity), fade + 12px slide-in motion, dismissal on scrim click or Escape, a Tab focus trap confined to the overlay, and focus handed back to the previous owner on close.
- Selecting a day only updates the headline; nothing is committed until OK. OK is disabled while the selection is out of range or fails `selectable_day_predicate` (cf. Flutter disabling confirm).
- Clicking the month/year label toggles a scrollable year grid in place of the day grid; the year range is `[first_date.year, last_date.year]` when bounds are given, otherwise the viewed year ±100.
- `current_date` controls which day is ringed as "today" (defaults to `QDate.currentDate()`); the selected day is a `primary` filled circle, out-of-range/unselectable days dim to 38% and are inert.
- The grid is hardcoded Sunday-first; locale-driven first-day-of-week is a deliberate deferral, as are the docked and text-input variants (module docstring).
- Parent the picker to the top-level window so the scrim covers the whole window, and connect `closed` to `deleteLater` for one-shot use (as the gallery does).
- See also [time picker](./time-picker.md) and [dialog](./dialog.md), which share the same overlay base.
