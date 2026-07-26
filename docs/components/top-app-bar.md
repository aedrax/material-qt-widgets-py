# Top app bar

Title and actions at the top of a screen.

**Classes:** `MdTopAppBar`, `TopAppBarVariant` · **Source:** `src/material_qt/widgets/topappbar/`
**Spec:** https://m3.material.io/components/top-app-bar — ports the Material 3 top app bar (cf. Flutter's `AppBar` and the M3 scroll-under configs).

## Usage

```python
from material_qt import MdIconButton, MdTopAppBar, TopAppBarVariant

bar = MdTopAppBar("Title", variant=TopAppBarVariant.SMALL,
                  leading=MdIconButton("menu"))
bar.add_action("search")
more = bar.add_action("more_vert")
more.clicked.connect(lambda: print("menu"))

# Medium/large bars collapse as content scrolls under them:
settings = MdTopAppBar("Settings", variant=TopAppBarVariant.MEDIUM)
settings.attach_scroll_area(my_scroll_area)  # 112 -> 64 px as you scroll
```

## API

### MdTopAppBar

```python
MdTopAppBar(
    title="",
    parent=None,
    *,
    variant=TopAppBarVariant.SMALL,
    leading=None,
    toolbar_height=None,
    bottom=None,
    scrolled_under_elevation=ElevationLevel.LEVEL3,
)
```

- `set_title(title)` — update the title (both titles on two-row variants).
- `add_action(icon="", *, toggle=False)` — append a trailing `MdIconButton` action and return it; `icon` is a Material Symbols ligature name.
- `set_bottom(widget)` — set (or clear with `None`) the persistent bottom slot, e.g. a tab bar (Flutter `AppBar.bottom`); the bar's height grows to fit it.
- `set_collapse_fraction(t)` — drive scroll-under collapse directly, `0.0` expanded to `1.0` collapsed; clamped, and a no-op for the single-row CENTER/SMALL variants.
- `collapse_fraction` — read-only property, the current collapse fraction.
- `attach_scroll_area(scroll_area)` — wire collapse to a `QScrollArea`'s vertical scroll position; a no-op for single-row variants.

**Signals:**

- None. Action buttons returned by `add_action` expose their own `clicked` signal.

### TopAppBarVariant

- `CENTER` — 64 px, centered `title-large` title.
- `SMALL` — 64 px, leading-aligned `title-large` title.
- `MEDIUM` — 112 px, `headline-small` title on a second row.
- `LARGE` — 152 px, `headline-medium` title on a second row.

## Notes

- Heights from source constants: row height 64; expanded heights 64/64/112/152 for CENTER/SMALL/MEDIUM/LARGE. `toolbar_height` overrides the 64 px per-row default and shifts every variant's expanded height by the delta (Flutter `AppBar.toolbarHeight`).
- Scroll-under collapse (MEDIUM/LARGE only): as the bar collapses to one row, the bottom headline title cross-fades out while a `title-large` title fades in at the top-row position, the container tints from `surface` to `surface-container`, and elevation rises from level 0 to `scrolled_under_elevation` (M3 level 3 by default, cf. Flutter `AppBar.scrolledUnderElevation`).
- The `bottom` slot sits below the toolbar rows and is not affected by collapse — a natural home for [tabs](./tabs.md).
- `leading` is any widget, typically a navigation `MdIconButton`; without one a zero-width spacer keeps the layout consistent.
- Container uses the `surface` role, title `on-surface`; there are no raw-color overrides.
- The bar keeps a fixed height at all times; place it above your content in a plain `QVBoxLayout` — it does not overlay or manage the scroll view itself.
- See [../theming.md](../theming.md) for color roles and elevation.
