# Menu

Popup list of choices anchored to a control.

**Classes:** `MdMenu`, `MdMenuItem`, `MdSubmenuItem`, `DropdownController` · **Source:** `src/material_qt/widgets/menu/`
**Spec:** <https://m3.material.io/components/menus>. Ports Material Web's `menu/` package; `MdMenuItem` mirrors Flutter `MenuItemButton` / `PopupMenuItem`, and `MdSubmenuItem` mirrors Flutter `SubmenuButton`.

## Usage

```python
from material_qt import MdFilledButton, MdMenu, MdMenuItem

trigger = MdFilledButton("Open menu", parent=page)

def open_menu():
    menu = MdMenu(trigger)
    for label, icon in [("Cut", "content_cut"), ("Copy", "content_copy"),
                        ("Paste", "content_paste"), ("Delete", "delete")]:
        menu.add_item(MdMenuItem(label, leading_icon=icon))
    menu.selected.connect(lambda t: print("Selected:", t))
    menu.open_at(trigger)

trigger.clicked.connect(open_menu)
```

Run the demo: `python -m material_qt.widgets.menu.demo`.

## API

### MdMenu

A popup menu surface anchored to a trigger widget (`surface-container`, level-2 elevation, corner-extra-small).

```python
MdMenu(
    parent: QWidget | None = None,
    *,
    max_height: int = 0,
    grabs_focus: bool = True,
)
```

- `open_at(anchor, *, side="bottom")` — show the menu next to `anchor`. `"bottom"` (default) anchors below the trigger, left-aligned; `"right"` anchors to the trigger's right edge (used by submenus). The popup stays on the anchor's screen: it flips above the anchor when there is no room below, clamps horizontally, and caps its height to the available space.
- `add_item(item)` — append an `MdMenuItem`; a nested `MdSubmenuItem`'s picks re-emit on this menu and close the whole popup chain.
- `clear()` — remove and delete all items.
- `set_max_height(height)` — cap the content height; items scroll inside a `QScrollArea` past it (`0` = uncapped).
- `highlight_first()` / `highlight_next()` / `highlight_prev()` — move the keyboard highlight, skipping disabled items (wraps around).
- `activate_highlighted()` — trigger the highlighted item; returns `True` if one was activated.

**Signals:**

- `selected = Signal(str)` — emits the chosen item's text.
- `activated = Signal(object)` — emits the chosen item's value.

### MdMenuItem

A single row in a menu.

```python
MdMenuItem(
    text: str = "",
    parent: QWidget | None = None,
    *,
    leading_icon: str = "",
    trailing_icon: str = "",
    trailing_text: str = "",
    enabled: bool = True,
    value: object = None,
)
```

- `text` — property; the row's label.
- `value` — property; the item's value (defaults to its `text` when unset).
- `is_enabled()` / `set_enabled(enabled)` — disabled rows dim to 38% opacity and never trigger.
- `set_highlighted(on)` — keyboard highlight (used when the menu does not hold widget focus).
- `set_leading_icon(name)` / `set_trailing_icon(name)` — icons are Material Symbols ligature names (e.g. `"content_cut"`), never `QIcon`.
- `trailing_text` is typically a keyboard shortcut, drawn in `on-surface-variant`.

**Signals:**

- `triggered = Signal()` — emitted when the item is activated (click or Enter on the highlighted row).

### MdSubmenuItem

A menu item that opens a nested `MdMenu` anchored to its right edge; hovering or clicking the row opens it instead of selecting it.

```python
MdSubmenuItem(
    text: str = "",
    parent: QWidget | None = None,
    *,
    leading_icon: str = "",
    submenu_icon: str = "arrow_right",
    enabled: bool = True,
)
```

- `submenu` — property; the nested `MdMenu`.
- `add_item(item)` — convenience passthrough to the nested menu.
- `open_submenu()` — open the submenu anchored to the item's right edge.

### DropdownController

`QObject` that drives a single reused `MdMenu` anchored under a field — the shared machinery behind the autocomplete, the filterable select, and the search bar's suggestions. It rebuilds one persistent popup in place, anchors it at the field's width, and (for a non-grabbing popup) forwards Up/Down/Enter/Escape from the typing input so the field keeps the keyboard.

```python
DropdownController(
    anchor: QWidget,
    *,
    key_source: QWidget | None = None,
    max_height: int = 0,
    grabs_focus: bool = False,
    auto_highlight: bool = False,
)
```

- `show(labels)` — rebuild the rows from display labels and (re)open under the anchor; closes instead when `labels` is empty.
- `close()` — close the popup if open.
- `is_open()` — whether the popup is currently shown.
- `menu` — property; the managed `MdMenu` (or `None` before first `show`).

**Signals:**

- `selected = Signal(str)` — re-emits the chosen row's text/label. The controller is deliberately value-agnostic: the host maps label to value.

## Notes

- With `grabs_focus=True` (default) the menu uses the `Qt.Popup` window flag: it takes an implicit keyboard and mouse grab, dismisses on an outside click, and owns keyboard navigation (Escape closes; Up/Down move; Enter activates).
- With `grabs_focus=False` the menu is a non-activating `Qt.Tool` window (the QCompleter popup pattern) for autocomplete/filterable fields: the keyboard stays on the typing field, and an app-wide event filter dismisses the popup on an outside press, focus moving elsewhere, or the host window moving/resizing/deactivating.
- Selecting a regular item emits `selected(text)` then `activated(value)` and closes the menu; a submenu item opens its child menu instead of dismissing. Nested picks surface on the parent menu too and close the whole chain.
- Rows are fixed at 48px; the popup shows the Material scrollbar when content exceeds `max_height`.
- The dropdown controller backs the [select](./select.md) and autocomplete fields; see [architecture](../architecture.md) for the shared widget machinery.
