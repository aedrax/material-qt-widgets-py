# Chips

Compact elements for input, filters, and actions.

**Classes:** `MdChip`, `MdAssistChip`, `MdSuggestionChip`, `MdChoiceChip`, `MdFilterChip`, `MdInputChip`, `MdChipSet` · **Source:** `src/material_qt/widgets/chips/`
**Spec:** https://m3.material.io/components/chips. The module docstring names Material Web's `chips/` as the upstream counterpart; each variant's docstring names its Flutter class (`ActionChip`, `ChoiceChip`, `FilterChip`, `InputChip`).

All chips are 32px tall, corner-small, with a `label-large` label, an optional leading Material Symbols icon or avatar image, ripple, and focus ring. Filter and choice chips are selectable; input chips (and optionally filter chips) carry a trailing remove icon.

## Usage

```python
from PySide6.QtWidgets import QButtonGroup

from material_qt import (
    MdAssistChip, MdChipSet, MdChoiceChip, MdFilterChip, MdInputChip,
)

assist = MdAssistChip("Add to calendar", icon="event")
assist.clicked.connect(lambda: print("action"))

choices = MdChipSet()
group = QButtonGroup()
group.setExclusive(True)
for i, name in enumerate(("Small", "Medium", "Large")):
    chip = MdChoiceChip(name, selected=(i == 0))
    group.addButton(chip)
    choices.add_chip(chip)

unread = MdFilterChip("Unread")
unread.toggled.connect(lambda on: print("filter unread:", on))

tag = MdInputChip("Alice", icon="person")
tag.removed.connect(lambda: print("removed"))
```

Run the demo: `python -m material_qt.widgets.chips.demo`.

## API

### MdChip

The base chip — use a variant subclass. It extends `QAbstractButton`, so `clicked`, `toggled(bool)`, `setEnabled`, and `setToolTip` come from Qt.

```python
MdChip(
    text: str = "",
    parent: QWidget | None = None,
    *,
    leading_icon: str = "",
    trailing_icon: str = "",
    avatar: QPixmap | None = None,
    selectable: bool = False,
    elevated: bool = False,
)
```

- `label` (property) / `set_label(text)` — the chip text (Flutter `label`).
- `set_label_style(font)` — the label `QFont` (Flutter `labelStyle`).
- `selected` (property) / `set_selected(value)` — selection state (Flutter `selected`); only meaningful when selectable.
- `set_leading_icon(name)` / `set_trailing_icon(name)` — Material Symbols glyph names; an empty string clears the slot.
- `set_avatar(pixmap)` / `avatar` (property) — leading avatar image (Flutter `avatar`), clipped to a 24px circle; `None` clears it.
- `set_background_color(role)` / `set_selected_color(role)` — container `ColorRole` overrides (Flutter `backgroundColor` / `selectedColor`); `None` restores the variant default.
- `set_checkmark_color(role)` / `set_show_checkmark(value)` — styling for the filter/choice leading checkmark (Flutter `checkmarkColor` / `showCheckmark`).
- **Signals:** `removed = Signal()` — the trailing delete affordance was activated (Flutter `onDeleted`). Plus the inherited `QAbstractButton` signals, notably `clicked` (Flutter `onPressed`) and `toggled(bool)` (Flutter `onSelected`).

### Variants

- `MdAssistChip(text="", parent=None, *, icon="", avatar=None, elevated=False)` — performs an action (Flutter `ActionChip`).
- `MdSuggestionChip(text="", parent=None, *, icon="", avatar=None, elevated=False)` — a dynamically generated action; label drawn in `on-surface-variant`.
- `MdChoiceChip(text="", parent=None, *, icon="", avatar=None, selected=False, elevated=False)` — single-select within a set (Flutter `ChoiceChip`). Shows no leading checkmark when selected; selection is conveyed by the container fill alone. Group several in an exclusive `QButtonGroup` for single-select behavior.
- `MdFilterChip(text="", parent=None, *, icon="", avatar=None, selected=False, deletable=False, elevated=False)` — toggles a filter and shows a leading checkmark when selected (Flutter `FilterChip`). `deletable=True` adds a trailing remove affordance that emits `removed`.
- `MdInputChip(text="", parent=None, *, icon="", avatar=None)` — represents a discrete piece of input; always deletable (Flutter `InputChip`) and emits `removed` when the trailing icon is activated.

### MdChipSet

```python
MdChipSet(parent: QWidget | None = None)
```

A horizontal container holding chips with consistent 8px spacing.

- `add_chip(chip)` — append a chip. Chips with a delete affordance (input chips, and filter chips created with `deletable=True`) are automatically removed from the set when they emit `removed`.
- `remove_chip(chip)` — detach and delete a chip.

**Signals:** none of its own; connect to the individual chips.

## Notes

- Selectable variants (`MdChoiceChip`, `MdFilterChip`) share a private base (`_SelectableChip`) that fills the container with `secondary-container` when selected; selection state is Qt's checked state (`setCheckable`/`isChecked` under the hood).
- Chips use Qt's plain `setEnabled` directly — there is no `set_enabled` wrapper as on [text fields](./text-field.md). Disabling dims the label and outline to the M3 disabled opacities and, on elevated chips, drops the shadow.
- `elevated=True` swaps the outline for a `surface-container-low` fill plus a level-1 shadow (an unselected elevated chip keeps its filled body).
- Icons are Material Symbols ligature names (`icon="event"`), never `QIcon`; the avatar is a `QPixmap`.
- The trailing remove icon is a hit-tested zone, not a child widget: `removed` fires only when both press and release land in the zone, and such a release does not also fire `clicked`.
- Selection can change the leading content (a filter chip's checkmark), so toggling re-queries the layout — chips size to content (`Fixed` size policy).
- Color overrides take theme `ColorRole` values, not raw `QColor`s, so chips restyle with the theme; see [../theming.md](../theming.md).
