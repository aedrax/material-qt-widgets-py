# Field

Chrome shared by text fields and selects.

**Classes:** `MdField`, `FieldVariant` · **Source:** `src/material_qt/widgets/field/`
**Spec:** https://api.flutter.dev/flutter/material/InputDecorator-class.html (the field is a building block, not an entry in the M3 catalogue). The module docstring names Material Web's `field/` as the upstream counterpart.

`MdField` is the visual container that [text fields](./text-field.md), [selects](./select.md), and [autocomplete](./autocomplete.md) compose: a floating label, an active indicator (filled) or notched outline (outlined), supporting text, an error state, optional leading/trailing icon slots, and a content slot where an input widget (e.g. a `QLineEdit`) is placed. Most applications use the higher-level widgets; reach for `MdField` directly when building a custom input.

## Usage

```python
from PySide6.QtWidgets import QLineEdit

from material_qt import FieldVariant, MdField

field = MdField(
    variant=FieldVariant.OUTLINED,
    label="Outlined label",
    supporting_text="Supporting text",
)
edit = QLineEdit()
edit.textChanged.connect(lambda t: field.set_populated(bool(t)))
field.set_content(edit)
```

Run the demo: `python -m material_qt.widgets.field.demo`.

## API

### FieldVariant

An `Enum` selecting the chrome style:

- `FieldVariant.FILLED` — `surface-container-highest` container with an active indicator along the bottom; corners rounded on top only.
- `FieldVariant.OUTLINED` — a 1px `outline` border (2px `primary` on focus) with the floated label notching the top edge.

### MdField

```python
MdField(
    parent: QWidget | None = None,
    *,
    variant: FieldVariant = FieldVariant.FILLED,
    label: str = "",
    supporting_text: str = "",
    error: bool = False,
    multiline_box_height: int | None = None,
)
```

- `set_content(widget)` — place the input/content widget inside the field and track its focus. Known editor types (`QLineEdit`, `QPlainTextEdit`, `QTextEdit`) are made chrome-less (frame removed, transparent background) so the field draws the container.
- `set_populated(populated)` — tell the field whether the content has a value; together with focus this decides whether the label floats.
- `set_error(error)` — toggle the error state (indicator, outline, label, and supporting text switch to the `error` color role).
- `set_supporting_text(text)` — set the supporting text drawn below the box.
- `set_counter(text)` — set the counter text shown at the bottom-right of the supporting row (e.g. `"3/10"`).
- `set_leading(widget)` / `set_trailing(widget)` — place a widget (typically an icon) at the leading/trailing edge; passing `None` clears the slot. Replacing a slot deletes the previous occupant.
- `variant` — read-only property returning the `FieldVariant`.

**Signals:** none. `MdField` is passive chrome; interaction signals live on the composing widgets.

## Notes

- The label floats when the content widget has focus **or** the field is marked populated. Focus is observed with an event filter installed by `set_content`; the populated flag is your responsibility (see the `textChanged` hookup in Usage).
- The float transition animates over the `SHORT3` duration with standard easing and is skipped entirely when motion is disabled or the widget is not visible.
- The single-line box is 48px tall plus an 8px reserve above it, so the floated label of the outlined variant can sit on the top border (56px total). `multiline_box_height` grows the box for multiline content; `None` keeps the single-line box.
- The 20px supporting row is only reserved (and `sizeHint` only grows) when supporting text, an error, or a counter is present.
- Icon slots take arbitrary `QWidget`s. The higher-level widgets pass `MdIcon` instances built from Material Symbols ligature names (e.g. `"search"`); the label and content inset automatically to clear an occupied leading slot.
- When the field is disabled, the label is drawn in `on-surface` instead of the accent roles.
- See [../theming.md](../theming.md) for the color roles used and [../architecture.md](../architecture.md) for the `MaterialWidgetMixin` machinery the field builds on.
