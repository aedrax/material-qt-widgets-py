# Bottom app bar

Bottom action bar with an optional FAB.

**Classes:** `MdBottomAppBar` · **Source:** `src/material_qt/widgets/bottomappbar/`
**Spec:** https://m3.material.io/components/bottom-app-bar — ports Flutter's `BottomAppBar` (`bottom_app_bar.dart`, https://api.flutter.dev/flutter/material/BottomAppBar-class.html).

## Usage

```python
from material_qt import MdBottomAppBar, MdFab

bar = MdBottomAppBar(notch=True)
for icon in ("menu", "search", "favorite", "more_vert"):
    bar.add_action(icon)
bar.set_fab(MdFab("add"))

search = bar.add_action("search")
search.clicked.connect(lambda: print("search"))
```

## API

### MdBottomAppBar

```python
MdBottomAppBar(
    parent=None,
    *,
    notch=False,
    height=80,
    elevation=ElevationLevel.LEVEL3,
)
```

- `add_action(icon="", *, toggle=False)` — append a leading action `MdIconButton` and return it; `icon` is a Material Symbols ligature name.
- `set_fab(fab)` — set (or clear with `None`) the trailing `MdFab`, end-cradled by the notch (mirrors Flutter's `FloatingActionButtonLocation.endContained`). Replaces and deletes any previous FAB.
- `fab` — read-only property, the hosted `MdFab` or `None`.
- `notch` — read-only property; `set_notch(enabled)` toggles the cradle cut-out.
- `count()` — number of leading action buttons.

**Signals:**

- None. Action buttons expose their own `clicked` signal — no callback-to-signal shim is needed.

## Notes

- Defaults follow the M3 token block in Flutter's `bottom_app_bar.dart`: height 80, container `surface-container`, elevation level 3. Content padding is the M3 default of 12 px vertical / 16 px horizontal.
- With `notch=True` and a FAB set, the bar's top edge is cradled with a rounded notch around the FAB (radius = FAB half-width + a 4 px notch margin, cf. Flutter `NotchedShape` / `notchMargin`).
- Unlike Flutter — where the `Scaffold` owns the FAB as a sibling and feeds its geometry to the bar — this widget hosts the FAB itself and positions it manually (trailing, top-aligned) so its lower half nests into the notch entirely within the bar's bounds; the FAB never overhangs the bar's top edge.
- Actions are left-aligned; a trailing stretch keeps the end of the bar clear for the FAB.
- Theme-role colors only: the background is the `surface-container` role (cf. Flutter `BottomAppBar.color` defaulting to `ColorScheme.surfaceContainer`); raw-`QColor` overrides are intentionally not exposed, matching the package convention.
- The FAB repositions on every resize (and defensively on paint), so the bar can be resized freely.
- For destination switching along the bottom edge use [navigation-bar](./navigation-bar.md) instead; the bottom app bar is for actions plus a primary FAB.
- See [../theming.md](../theming.md) for color roles and elevation.
