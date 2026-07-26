# Text field

Let users enter and edit text.

**Classes:** `MdFilledTextField`, `MdOutlinedTextField` · **Source:** `src/material_qt/widgets/textfield/`
**Spec:** https://m3.material.io/components/text-fields. The module docstring names Material Web's `textfield/` and Flutter's `TextField` / `InputDecoration` as the upstream counterparts.

Each text field composes the [field chrome](./field.md) (floating label, active indicator / notched outline, supporting text, error, icon slots, counter) with a `QLineEdit` (single-line) or `QPlainTextEdit` (multiline) for input.

## Usage

```python
from material_qt import MdFilledTextField, MdOutlinedTextField

name = MdFilledTextField(label="Name", supporting_text="As it appears on your ID")
name.textChanged.connect(lambda t: print("typing:", t))
name.submitted.connect(lambda t: print("submitted:", t))

password = MdOutlinedTextField(
    label="Password", password=True,
    supporting_text="At least 8 characters",
)
```

Run the demo: `python -m material_qt.widgets.textfield.demo`.

## API

### MdFilledTextField / MdOutlinedTextField — shared API

```python
MdFilledTextField(
    parent: QWidget | None = None,
    *,
    label: str = "",
    text: str = "",
    placeholder: str = "",
    supporting_text: str = "",
    error: bool = False,
    password: bool = False,
    enabled: bool = True,
    read_only: bool = False,
    max_length: int = 0,
    max_lines: int = 1,
    min_lines: int = 1,
    leading_icon: str = "",
    trailing_icon: str = "",
    validator: QValidator | None = None,
)
```

- `text()` / `set_text(value)` — read/write the field value.
- `max_length()` — the configured cap (`0` means unlimited).
- `set_error(error)` / `set_supporting_text(text)` / `set_placeholder(text)` — forwarded to the field chrome and inner edit.
- `set_enabled(enabled)` — enable/disable the widget, the inner edit, and the field chrome together.
- `set_read_only(read_only)` / `is_read_only()` — read-only state of the inner edit.
- `set_validator(validator)` — set a `QValidator` (the idiomatic Qt input formatter). Ignored in multiline mode, which has no validator hook.
- `set_leading_icon(name)` / `set_trailing_icon(name)` — Material Symbols ligature names (e.g. `"search"`); an empty string clears the slot.
- `password_visible` — read-only property: whether the password toggle currently reveals the text.
- `line_edit` — escape hatch: the underlying input widget (`QLineEdit` or `QPlainTextEdit`) for advanced configuration.
- `field` — escape hatch: the underlying `MdField` chrome.

**Signals:**

- `textChanged = Signal(str)`
- `submitted = Signal(str)` — fires on Enter / editing complete (single-line fields; it is wired to `QLineEdit.returnPressed`).

## Notes

- The two public classes are thin subclasses of a private base (`_MdTextField`) that differ only in the `VARIANT` class attribute (`FieldVariant.FILLED` / `FieldVariant.OUTLINED`).
- Constructor validation raises `ValueError` for: `password` with `max_lines != 1` (obscured fields cannot be multiline, mirroring Flutter's assert); `password` combined with `trailing_icon` (the trailing slot is owned by the visibility toggle); and `min_lines > max_lines`.
- `max_lines > 1` selects multiline mode (a `QPlainTextEdit`); `min_lines` sets the initial box height. The content-widget type is picked once, at construction.
- `max_length` is counted in **UTF-16 code units** — the units `QLineEdit.maxLength` counts — so an emoji outside the BMP counts as 2. The live counter (`"3/10"`) uses the same unit. In multiline mode the cap is enforced manually: only the overflowing part of the last insertion is rejected, undo keeps working, and surrogate pairs are never cut in half.
- `password=True` obscures input and installs a built-in trailing visibility toggle (`visibility` / `visibility_off`). Calling `set_trailing_icon` later retires the toggle and restores the obscured echo mode.
- Per M3, when a label is set the placeholder only shows while the field is focused (the label has floated out of the way).
- Use `set_enabled` rather than plain `setEnabled` — it also disables the inner edit and the field chrome so the disabled styling is consistent.
- Flutter → QObject parity, from the module docstring ("Idiomatic QObject surface"):

  | Flutter | material-qt |
  | --- | --- |
  | callbacks | Qt Signals: `textChanged(str)`, `submitted(str)` |
  | controller value | `text()` / `set_text()` |
  | `maxLines` / `minLines` | `max_lines` / `min_lines` (multiline mode) |
  | `prefixIcon` / `suffixIcon` | `leading_icon` / `trailing_icon` |
  | `obscureText` | `password` (with a built-in visibility toggle) |
  | `maxLength` | `max_length` (with a live character counter, enforced) |
  | `inputFormatters` | `set_validator` (a `QValidator`) |

- For a field that filters a dropdown as you type, see [autocomplete](./autocomplete.md); for picking from fixed options, see [select](./select.md).
