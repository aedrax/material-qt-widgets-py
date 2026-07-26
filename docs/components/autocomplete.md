# Autocomplete

Text field that filters options as you type.

**Classes:** `MdAutocomplete`, `MdFilledAutocomplete`, `MdOutlinedAutocomplete` · **Source:** `src/material_qt/widgets/autocomplete/`
**Spec:** https://api.flutter.dev/flutter/material/Autocomplete-class.html (not a distinct entry in the M3 catalogue). The module docstring names Flutter's `Autocomplete` (`autocomplete.dart`) as the upstream counterpart.

An autocomplete composes the [field chrome](./field.md) with a `QLineEdit` for input and reuses the menu surface for the options popup. As the user types, options whose display string contains the query are shown in a dropdown; picking one fills the field and emits `selected(option)`.

## Usage

```python
from material_qt import MdOutlinedAutocomplete

ac = MdOutlinedAutocomplete(
    label="Fruit",
    options=["Apple", "Apricot", "Banana", "Blueberry", "Cherry",
             "Date", "Fig", "Grape", "Mango", "Orange"],
)
ac.selected.connect(lambda v: print("Selected:", v))
ac.textChanged.connect(lambda t: print("typing:", t))
```

## API

### MdAutocomplete / MdFilledAutocomplete / MdOutlinedAutocomplete — shared API

```python
MdFilledAutocomplete(
    parent: QWidget | None = None,
    *,
    options: Sequence[object] | None = None,
    label: str = "",
    placeholder: str = "",
    supporting_text: str = "",
    display_string_for_option: Callable[[object], str] | None = None,
    options_max_height: int = 200,
    initial_value: str = "",
)
```

- `set_options(options)` / `options()` — replace / copy the option list. Options may be strings or arbitrary objects.
- `set_display_string_for_option(fn)` — the callable mapping an option to its display text (defaults to `str`); used both to render rows and to match the typed query.
- `text()` / `set_text(value)` — read/write the field text; `set_text` also updates the field's populated state so the label floats.
- `matching_options(query)` — the options whose display string contains `query` (case-insensitive); an empty query matches everything.
- `line_edit` — escape hatch: the underlying `QLineEdit` for advanced configuration.
- **Signals:**
  - `selected = Signal(object)` — emits the chosen *option object* (Flutter `onSelected`).
  - `textChanged = Signal(str)` — emits the field text on every keystroke.

## Notes

- `MdAutocomplete` is an alias for `MdFilledAutocomplete` — the filled variant, matching Flutter's Material default. The variant classes are thin subclasses of a private base (`_MdAutocomplete`) differing only in the `VARIANT` class attribute (`FieldVariant.FILLED` / `FieldVariant.OUTLINED`).
- The popup opens (and refilters) on user edits — it is wired to `QLineEdit.textEdited` — so programmatic `set_text` does not pop the menu, and there is no popup-on-focus.
- Matching is a case-insensitive (`casefold`) substring test against the display string. Override `matching_options` in a subclass for a different strategy.
- `selected` carries the original option object, not its display text; with the default `str` display function on a list of strings the two coincide.
- Options with duplicate display labels each get their own row and stay distinct: rows are committed by index, not by label lookup.
- The popup does not grab focus; navigation keys are forwarded from the input, and the top match is auto-highlighted so Enter commits it.
- `options_max_height` (default 200) caps the popup height; it scrolls past that.
- Constructor `initial_value` sets the initial field text (Flutter `initialValue`); it does not have to match any option.
- For a fixed-choice control without free text, see [select](./select.md) (its `enable_filter` mode is the closest cousin); for plain input, see [text field](./text-field.md).
