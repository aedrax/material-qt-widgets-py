# Pickers — Flutter ↔ material_qt parity

Status legend: ✅ verified · ➕ added this pass · 🆕 built this pass · ⛔ N/A (rationale)

Scope: the Material **picker** widgets. Flutter reference (read-only):
`flutter/packages/flutter/lib/src/material/{date_picker.dart, calendar_date_picker.dart, time_picker.dart}`.
Qt port: `qt/src/material_qt/widgets/{datepicker, timepicker}`.

Conventions applied: Flutter callbacks → Qt Signals; Flutter named params →
`set_*()` / `@property` / constructor kwargs; theme-role colors via
`ThemeManager`. The pickers subclass `core.ModalOverlay` (not edited).

---

## DatePickerDialog (date_picker.dart) → MdDatePicker (widgets/datepicker) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| initialDate | `initial_date` kwarg → `selected_date` property | ✅ |
| firstDate | `first_date` kwarg → out-of-range days disabled (dimmed, inert) | ➕ |
| lastDate | `last_date` kwarg → out-of-range days disabled (dimmed, inert) | ➕ |
| currentDate | `current_date` kwarg (the "today" outline; was hardcoded `QDate.currentDate()`) | ➕ |
| selectableDayPredicate | `selectable_day_predicate` kwarg (`Callable[[QDate], bool]`) → disables vetoed days | ➕ |
| cancelText | `cancel_text` kwarg (default "Cancel") | ➕ |
| confirmText | `confirm_text` kwarg (default "OK") | ➕ |
| helpText | `help_text` kwarg (default "Select date") → supporting label | ➕ |
| (no Flutter equivalent — invalid-selection guard) | OK button disabled when `_selected` fails range/predicate, so `accepted` never emits an invalid date | ➕ |
| onDateChanged (implicit via dialog result) | `accepted(QDate)` signal | ✅ |
| (dialog dismiss / Cancel) | `rejected` signal (inherited from `ModalOverlay`) | ✅ |
| (dialog closed) | `closed` signal (inherited from `ModalOverlay`) | ✅ |
| initialEntryMode (calendar ↔ input) | ⛔ — only the calendar entry mode is ported; the text-input entry mode is deferred (see datepicker docstring). No Qt kwarg; calendar is always shown. | ⛔ |
| initialCalendarMode (day ↔ year grid) | ⛔ — year-grid mode not ported; the picker is day-grid only. | ⛔ |
| errorFormatText | ⛔ — belongs to the deferred text-input entry mode. | ⛔ |
| errorInvalidText | ⛔ — belongs to the deferred text-input entry mode. | ⛔ |
| fieldHintText | ⛔ — text-input entry mode deferred. | ⛔ |
| fieldLabelText | ⛔ — text-input entry mode deferred. | ⛔ |
| keyboardType | ⛔ — text-input entry mode deferred. | ⛔ |
| onDatePickerModeChange | ⛔ — no input/calendar mode switch in the port. | ⛔ |
| switchToInputEntryModeIcon | ⛔ — no entry-mode toggle in the port. | ⛔ |
| switchToCalendarEntryModeIcon | ⛔ — no entry-mode toggle in the port. | ⛔ |
| restorationId | ⛔ — Flutter state-restoration framework; no Qt analogue. | ⛔ |
| insetPadding | ⛔ — `ModalOverlay` centers the fixed-width panel itself; padding is not a public seam. | ⛔ |
| calendarDelegate | ⛔ — alternative calendar systems (Hijri, Nepali, …); the port is Gregorian only (also: weekday row is hardcoded Sunday-first). | ⛔ |

Notes:
- Range clamp + predicate are unified in the module-level `day_enabled(date, *, first_date, last_date, predicate)` helper (a pure, testable seam), reused by both the modal and the inline calendar. Also exposed per-instance as `MdDatePicker.is_selectable(date)`.

- [x] all DatePickerDialog properties verified, added, or marked ⛔ with rationale

---

## CalendarDatePicker (calendar_date_picker.dart) → MdCalendarDatePicker (widgets/datepicker) — built 🆕

A minimal **inline / docked** (non-modal) calendar: month-nav row + weekday
header + 6×7 day grid, reusing the shared `first_column` helper and the
`_DayCell` primitive (no modal refactor required). It is a plain `QWidget` you
parent into a host — no scrim, no headline, no OK/Cancel.

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| initialDate | `initial_date` kwarg → `selected_date` property | 🆕 |
| firstDate | `first_date` kwarg → out-of-range days disabled | 🆕 |
| lastDate | `last_date` kwarg → out-of-range days disabled | 🆕 |
| currentDate | `current_date` kwarg (the "today" outline) | 🆕 |
| onDateChanged | `dateChanged(QDate)` signal | 🆕 |
| onDisplayedMonthChanged | `displayedMonthChanged(QDate)` signal + `displayed_month` property | 🆕 |
| selectableDayPredicate | `selectable_day_predicate` kwarg → disables vetoed days | 🆕 |
| initialCalendarMode (day ↔ year) | ⛔ — year-grid mode not ported (day grid only); matches the modal. | ⛔ |
| calendarDelegate | ⛔ — Gregorian only. | ⛔ |

- [x] inline calendar built; reuses `first_column` + `_DayCell`
- [ ] Coordinator follow-up: wire `MdCalendarDatePicker` into the gallery demo (it is exported from `widgets/datepicker/__init__.py` but not registered in `gallery/gallery.py`, which is outside this unit's scope).

---

## TimePickerDialog (time_picker.dart) → MdTimePicker (widgets/timepicker) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| initialTime | `initial_time` kwarg → `selected_time` property | ✅ |
| initialEntryMode (dial ↔ input) | `initial_entry_mode` kwarg ("dial" / "input"); toggle button switches at runtime | ✅ |
| (12h vs 24h dial) | `hour24` kwarg → dual-ring 24h dial + AM/PM hidden (Flutter derives this from locale `alwaysUse24HourFormat`; the port exposes it directly) | ✅ |
| helpText | `help_text` kwarg → overrides the supporting label in both modes | ➕ |
| cancelText | `cancel_text` kwarg (default "Cancel") | ➕ |
| confirmText | `confirm_text` kwarg (default "OK") | ➕ |
| (dialog result on OK) | `accepted(QTime)` signal | ✅ |
| (dialog dismiss / Cancel) | `rejected` signal (inherited from `ModalOverlay`) | ✅ |
| (dialog closed) | `closed` signal (inherited from `ModalOverlay`) | ✅ |
| onEntryModeChanged | ⛔ — entry mode toggles internally; no public change signal exposed (could be added if a consumer needs it). | ⛔ |
| hourLabelText | ⛔ — the input-mode "Hour" caption is hardcoded; not parameterized. | ⛔ |
| minuteLabelText | ⛔ — the input-mode "Minute" caption is hardcoded; not parameterized. | ⛔ |
| errorInvalidText | ⛔ — input fields clamp to valid ranges (no free-form error state to surface). | ⛔ |
| orientation | ⛔ — fixed portrait layout; no landscape variant. | ⛔ |
| emptyInitialInput | ⛔ — fields always seed from `initial_time`; empty-input start not ported. | ⛔ |
| switchToInputEntryModeIcon | ⛔ — the toggle uses fixed "keyboard"/"schedule" Material Symbols. | ⛔ |
| switchToTimerEntryModeIcon | ⛔ — no timer entry mode in the port. | ⛔ |
| restorationId | ⛔ — Flutter state-restoration framework; no Qt analogue. | ⛔ |

Notes:
- Dial angle math is exposed as pure functions `angle_to_hour` / `angle_to_minute` /
  `angle_to_hour24` (unit-tested cardinal mapping: top=12, right=3, bottom=6, left=9).

- [x] all TimePickerDialog properties verified, added, or marked ⛔ with rationale
