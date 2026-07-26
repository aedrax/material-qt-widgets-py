# Navigation rail

Vertical side rail switching destinations.

**Classes:** `MdNavigationRail` · **Source:** `src/material_qt/widgets/navigationrail/`
**Spec:** https://m3.material.io/components/navigation-rail — ports the Material 3 navigation rail (cf. Flutter's `NavigationRail` / `_NavigationRailDefaultsM3`).

## Usage

```python
from material_qt import FabColor, FabSize, MdFab, MdNavigationRail

rail = MdNavigationRail()
for label, icon in [("Home", "home"), ("Search", "search"),
                    ("Saved", "bookmark"), ("Profile", "person")]:
    rail.add_destination(label, icon=icon)
rail.set_leading(MdFab("edit", size=FabSize.SMALL, color=FabColor.PRIMARY))
rail.changed.connect(lambda index: print("active:", index))

rail.set_extended(True)   # animate 80 -> 256 px with labels beside icons
```

## API

### MdNavigationRail

```python
MdNavigationRail(
    parent=None,
    *,
    extended=False,
    label_type="all",
    group_alignment="top",
    leading_at_top=True,
    trailing_at_bottom=False,
)
```

- `add_destination(label, *, icon="", active_icon="")` — append a destination and return it; icons are Material Symbols ligature names. The first destination added is selected automatically.
- `selected_index` — property, index of the active destination or `-1`; assignable.
- `set_selected_index(index)` — programmatically select the destination at `index`.
- `extended` — read-only property; `set_extended(extended, *, animated=True)` animates the rail between 80 px and 256 px wide (labels appear beside the icons when extended).
- `set_label_type(label_type)` — `"all"` / `"selected"` / `"none"`; controls compact-mode labels.
- `set_group_alignment(alignment)` — `"top"` / `"center"` / `"bottom"`; positions the destination group.
- `set_leading(widget, *, at_top=None)` / `set_trailing(widget, *, at_bottom=None)` — pin widgets above / below the destination group (e.g. a FAB or menu button).
- `set_leading_at_top(at_top)` / `set_trailing_at_bottom(at_bottom)` — `True` pins the widget to the rail's very top / bottom; `False` keeps it adjacent to the destination group (Flutter `leadingAtTop` / `trailingAtBottom`).

**Signals:**

- `changed = Signal(int)` — emitted with the destination index when the active destination changes.

## Notes

- Metrics from source constants: compact width 80, extended width 256, 24 px icon in a 56x32 `secondary-container` pill indicator, destination height 56 (48 with `label_type="none"` in compact mode), 12 px spacing, 8 px top/bottom padding.
- The rail's background is the `surface` role; active icon uses `on-secondary-container` (filled glyph), inactive `on-surface-variant`.
- The extend/collapse width change animates with the `EMPHASIZED` easing over the `MEDIUM2` duration; pass `animated=False` (or run with motion disabled) to snap. The icon column stays fixed in the compact 80 px zone, so extending only reveals labels to its right.
- In extended mode labels always show regardless of `label_type`; `label_type` only affects compact mode.
- Selection is exclusive via an internal `QButtonGroup`; `changed` also fires for programmatic `set_selected_index` calls.
- The public API mirrors [navigation-bar](./navigation-bar.md) (`changed(int)`, `add_destination`), but the rail's `add_destination` has no `badge` kwarg.
- Width is fixed (`QSizePolicy.Fixed` horizontally); give the rail its height from your layout.
- See [../theming.md](../theming.md) for color roles.
