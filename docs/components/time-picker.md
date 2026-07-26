# Time picker

Select a time on a clock dial.

**Classes:** `MdTimePicker` · **Source:** `src/material_qt/widgets/timepicker/`
**Spec:** <https://m3.material.io/components/time-pickers>. Ports the Material 3 modal time picker (cf. Flutter's `showTimePicker`, with both `TimePickerEntryMode` styles).

## Usage

```python
from material_qt import MdTimePicker

picker = MdTimePicker(window, hour24=False)
picker.closed.connect(picker.deleteLater)
picker.accepted.connect(lambda t: print(t.toString("h:mm AP")))
picker.open()
```

## API

### MdTimePicker

A modal time picker overlay: an elevated `surface-container-high` panel with a time display (selectable hour/minute fields plus an AM/PM toggle) and a clock dial; clicking or dragging on the dial sets the active field. Extends `core.ModalOverlay` (see [architecture: modal overlay](../architecture.md#modal-overlay)).

```python
MdTimePicker(
    parent: QWidget,
    *,
    initial_time: QTime | None = None,
    initial_entry_mode: str = "dial",
    hour24: bool = False,
    confirm_text: str = "OK",
    cancel_text: str = "Cancel",
    help_text: str | None = None,
)
```

- `open()` — inherited from `ModalOverlay`; shows the overlay over its parent with a fading scrim.
- `dismiss()` — inherited; reject and close (also triggered by a scrim click, Escape, or Cancel).
- `selected_time` — property; the current selection as a `QTime` (in 12h mode the hour is combined with the AM/PM state).

**Signals:**

- `accepted = Signal(QTime)` — fires on OK with the selected time.
- `rejected = Signal()` — inherited from `ModalOverlay`; fires on Cancel, Escape, or a scrim click.
- `closed = Signal()` — inherited from `ModalOverlay`; fires whenever the overlay closes (accept or reject).

Pure helper functions exported by the package: `angle_to_hour(dx, dy)` (screen vector to hour 1..12), `angle_to_minute(dx, dy)` (to minute 0..59), and `angle_to_hour24(dx, dy, *, inner)` (to a 24-hour value, picking the ring). They expose the dial's `atan2(dx, -dy)` math so the cardinal mapping is unit-tested (top=12, right=3, bottom=6, left=9).

## Notes

- Behavior inherited from `ModalOverlay`: full-parent scrim, fade + slide-in motion, Esc and scrim-click dismissal, a Tab focus trap, and focus restoration on close. Parent to the top-level window so the scrim covers it, and connect `closed` to `deleteLater` for one-shot use.
- Entry modes (cf. Flutter `TimePickerEntryMode`): `"dial"` shows the clock face; `"input"` replaces it with validated hour/minute `QLineEdit`s. `initial_entry_mode` picks the start; any value other than `"input"` falls back to `"dial"`. The icon button in the actions row switches modes at runtime and shows the mode you can switch to (`"keyboard"` in dial mode, `"schedule"` in input mode).
- `hour24=False` (default) is the 12-hour dial with an AM/PM toggle; the dial edits hours 1–12. `hour24=True` renders a dual-ring dial — inner ring `12, 1..11`, outer ring `00, 13..23` (top is 12 and 00 respectively) — and hides the AM/PM selector entirely; the dial value is the 0–23 hour.
- Clicking the hour or minute display field chooses which value the dial edits; the active field is highlighted in `primary-container`.
- In input mode, typed values are clamped to range (`1–12` or `0–23` for hours, `0–59` for minutes) and the boxes are synced to the clamped value on commit and on OK, so the display can never disagree with the committed time.
- `help_text` overrides the per-mode supporting label ("Select time" / "Enter time"); when given it is shown verbatim in both entry modes (cf. Flutter `helpText`).
- `initial_time` defaults to `QTime.currentTime()`.
- See also [date picker](./date-picker.md) and [dialog](./dialog.md), which share the same overlay base.
