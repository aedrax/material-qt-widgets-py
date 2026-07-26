# Button group

Connected pills, single- or multi-select.

**Classes:** `MdButtonGroup` · **Source:** `src/material_qt/widgets/buttongroup/`
**Spec:** <https://m3.material.io/components/button-groups>. Ports the Material 3 Expressive button group; there is no stable `@material/web` tag for it. Unlike the connected [`MdSegmentedButtonSet`](./segmented.md), the buttons here are separate pills with small gaps between them.

## Usage

```python
from material_qt import MdButtonGroup

# Multi-select (the default): a formatting toolbar.
fmt = MdButtonGroup(page, multi=True)
for label, icon in [("Bold", "format_bold"), ("Italic", "format_italic"),
                    ("Underline", "format_underlined")]:
    fmt.add_button(label, icon=icon)
fmt.changed.connect(lambda indices: print("selected:", indices))

# Single-select (exclusive): a view switcher.
view = MdButtonGroup(page, multi=False)
for label in ["Day", "Week", "Month"]:
    view.add_button(label)
```

## API

### MdButtonGroup

A transparent `QWidget` container laying out its pill toggle buttons in a row with 8px gaps.

```python
MdButtonGroup(
    parent: QWidget | None = None,
    *,
    multi: bool = True,
)
```

- `multi=True` (the default) allows any number of buttons to be selected; `multi=False` uses an exclusive `QButtonGroup`, so exactly one button is selected once any is, and clicking the selected button cannot clear it.
- `add_button(label="", *, icon="")` — append a pill button; `icon` is a Material Symbols ligature name (e.g. `"format_bold"`), never a `QIcon`. Returns the button widget, on which you can use the standard Qt checkable API: `setChecked(True)` for an initial selection, `isChecked()`, `toggled(bool)`, `setEnabled()`.
- `selected_indices() -> list[int]` — indices of the currently checked buttons, in add order.
- There is no remove/clear API and no programmatic bulk-selection setter; drive individual buttons via the objects returned by `add_button`.

**Signals:**

- `changed = Signal(list)` — the list of selected indices, emitted whenever the selection changes.

## Notes

- In single-select mode an exclusive switch fires two internal `toggled` signals (old button off, new button on); the group deliberately emits `changed` only once per switch, on the selection.
- Calling `setChecked` on a returned button emits `changed` too — it is not signal-blocked, unlike `MdSegmentedButtonSet.set_selected_indices`.
- Metrics: 48px tall pills (corner radius 24, i.e. fully rounded), 8px gap between buttons, 16px horizontal padding, 18px icon, `label-large` text. A trailing stretch keeps the row left-packed.
- Selected buttons fill `secondary-container` with `on-secondary-container` content; unselected use `surface-container-low` / `on-surface-variant`. The icon glyph renders in the filled Material Symbols style while selected.
- The peer widget `MdSegmentedButtonSet` also emits `changed(list)` with indices, so the two are drop-in similar; only the segmented set additionally offers a values-based signal.
- Deferred (scaffold): the press-morph animation (the pressed button widening as its neighbors shrink).
- See also [segmented buttons](./segmented.md) for the connected, outlined variant of this pattern.
