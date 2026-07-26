# FAB menu

A FAB that expands into labeled actions.

**Classes:** `MdFabMenu` · **Source:** `src/material_qt/widgets/fabmenu/`
**Spec:** <https://m3.material.io/components/fab-menu>. Ports the Material 3 Expressive FAB menu; there is no `@material/web` tag for it — the module composes this library's own [`MdFab`](./fab.md) widgets.

## Usage

```python
from material_qt import MdFabMenu
from PySide6.QtCore import Qt

menu = MdFabMenu(page, icon="add")
for label, icon in [("Share", "share"), ("Edit", "edit"), ("Delete", "delete")]:
    menu.add_item(label, icon=icon)
menu.itemClicked.connect(lambda index: print("picked", index))

# Typically anchored to a corner of the page:
layout.addWidget(menu, 0, Qt.AlignmentFlag.AlignRight)
```

## API

### MdFabMenu

A plain `QWidget` containing a primary regular FAB (color `PRIMARY`) that toggles a vertical column of labeled small FABs (color `SECONDARY`) stacked above it.

```python
MdFabMenu(
    parent: QWidget | None = None,
    *,
    icon: str = "add",
)
```

- `icon` is the closed-state Material Symbols ligature name for the toggle FAB; while open the toggle FAB shows `"close"`.
- `add_item(label, *, icon="") -> MdFab` — append a labeled menu item; returns its small `MdFab` so you can connect to it directly (e.g. its `clicked` or `longPressed`).
- `is_open` — property; whether the menu is currently expanded.
- `toggle()` — flip open/closed (also wired to the primary FAB's `clicked`).
- `set_open(open_)` — set the state explicitly; no-op if unchanged, otherwise shows/hides the items, swaps the toggle icon, and emits `toggled`.
- Standard Qt `setEnabled()` etc. apply to the container; individual item FABs can be disabled via the `MdFab` returned by `add_item`.

**Signals:**

- `itemClicked = Signal(int)` — the index of the activated menu item (in `add_item` order). The menu closes itself after emitting.
- `toggled = Signal(bool)` — emitted on open (`True`) / close (`False`).

## Notes

- Activating an item emits `itemClicked(index)` and then closes the menu (which also emits `toggled(False)`).
- Items are inserted as nested layouts, not wrapper widgets, so each small FAB's level-3 drop shadow is clipped only by the menu's inset bounds; the menu keeps an 18px content margin (22px at the bottom) for exactly this reason — do not pack it tightly.
- Items added while the menu is closed start hidden and appear on open; `add_item` can be called at any time.
- Item labels are `label-large` `QLabel`s colored `on-surface`; they restyle automatically on theme changes via a `ThemeManager.themeChanged` connection.
- The menu's size policy is `Preferred` x `Maximum`, and a leading stretch keeps items packed just above the FAB instead of spreading over extra height.
- Deferred (scaffold): the background scrim (use the dialog/bottom-sheet pattern if you need one) and the staggered open/close item animation — items simply show and hide.
- See also [FAB](./fab.md) for the underlying button and its `longPressed` contract.
