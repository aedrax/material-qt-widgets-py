# Select

Dropdown to pick from options.

**Classes:** `MdFilledSelect`, `MdOutlinedSelect` · **Source:** `src/material_qt/widgets/select/`
**Spec:** https://m3.material.io/components/menus (a select is a field that opens a menu of options). The module docstring names Material Web's `select/` and Flutter's `DropdownMenu` / `DropdownButton` as the upstream counterparts.

A select reuses the [field chrome](./field.md) (label, indicator/outline, supporting text) to show the chosen option, with a trailing dropdown arrow. Clicking anywhere in the field opens a menu of options below it; choosing an option updates the value and emits `changed(value)`.

## Usage

```python
from material_qt import MdFilledSelect, MdOutlinedSelect

fruit = MdFilledSelect(label="Fruit", supporting_text="Pick one")
for f in ("Apple", "Banana", "Cherry", "Date"):
    fruit.add_option(f)
fruit.changed.connect(lambda v: print("Chose:", v))

country = MdOutlinedSelect(label="Country", items=["USA", "Canada", "Mexico"])
country.set_value("Canada")
```

Run the demo: `python -m material_qt.widgets.select.demo`.

## API

### MdFilledSelect / MdOutlinedSelect — shared API

```python
MdFilledSelect(
    parent: QWidget | None = None,
    *,
    label: str = "",
    hint_text: str = "",
    supporting_text: str = "",
    items: list | None = None,
    value: object = None,
    enabled: bool = True,
    leading_icon: str = "",
    menu_height: int = 0,
    enable_filter: bool = False,
)
```

- `add_option(text, value=None)` — append one option; when `value` is `None` the display text doubles as the value.
- `set_options(items)` — replace all options. Each item is a `str` or a `(text, value)` pair.
- `set_value(value)` / `value()` — select the option whose value equals `value` / read the current value.
- `is_enabled()` / `set_enabled(enabled)` — the select's own enabled flag (see Notes).
- `set_menu_height(height)` — cap the popup height; the menu scrolls past it (`0` means no explicit cap).
- **Signals:** `changed = Signal(object)` — emits the selected value.

## Notes

- The two public classes are thin subclasses of a private base (`_MdSelect`) that differ only in the `VARIANT` class attribute (`FieldVariant.FILLED` / `FieldVariant.OUTLINED`).
- The payload of `changed` is the option **value** (an arbitrary object), not its display text — unlike the text field's `textChanged(str)`. The signal is declared as `Signal(object)`.
- `set_value` silently does nothing when no option matches; set options before the initial value (the constructor applies `items` before `value` for you).
- `leading_icon` is a Material Symbols ligature name (e.g. `"public"`), placed in the field's leading slot so the label and text inset to clear it.
- `enable_filter=True` makes the display editable: typing narrows the open menu (Flutter's `enableFilter`), the top match is auto-highlighted so Enter commits it, and the cursor switches to an I-beam. Without it the display is read-only and shows a pointing-hand cursor.
- `hint_text` is the placeholder shown in the display edit while nothing is selected.
- Options with duplicate display labels stay distinct: menu rows are committed by index, not by label lookup.
- A press that dismisses the open popup is not allowed to immediately reopen it (a 0.1s grace period reproduces `QComboBox` click-to-toggle behavior).
- `set_enabled` toggles the select's internal flag and the inner display edit; it intentionally does not call `setEnabled` on the whole widget, so the field chrome keeps its normal colors. Calling Qt's plain `setEnabled` instead will grey out everything but does not update the select's own click/cursor handling.
- The popup is the shared menu surface driven by a `DropdownController`; [autocomplete](./autocomplete.md) uses the same machinery with free-text input. For general navigation see [../usage.md](../usage.md).
