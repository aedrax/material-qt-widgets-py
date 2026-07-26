# Tabs

Organize content across primary/secondary tabs.

**Classes:** `MdTabs`, `MdTab` · **Source:** `src/material_qt/widgets/tabs/`
**Spec:** https://m3.material.io/components/tabs — ports Material Web's `tabs/`.

## Usage

```python
from material_qt import MdTabs

primary = MdTabs()
primary.add_tab("Flights", icon="flight")
primary.add_tab("Trips", icon="luggage")
primary.add_tab("Explore", icon="explore")
primary.changed.connect(lambda index: print("active:", index))

secondary = MdTabs(secondary=True)
for t in ("Overview", "Specifications", "Reviews"):
    secondary.add_tab(t)
```

Run the demo: `python -m material_qt.widgets.tabs.demo`.

## API

### MdTabs

```python
MdTabs(parent=None, *, secondary=False, scrollable=False)
```

- `add_tab(label, *, icon="")` — append an `MdTab` and return it; `icon` is a Material Symbols ligature name. The first tab added is selected automatically.
- `selected_index` — property, index of the active tab or `-1`; assignable.
- `set_selected_index(index)` — programmatically select the tab at `index`.
- `is_scrollable` — property; `set_scrollable(scrollable)` — non-scrollable tabs share the full width; scrollable tabs keep natural width and overflow into a hidden-scrollbar scroll area (Flutter `isScrollable`).
- `set_indicator_color(color)` — override the indicator color; `None` restores the `primary` role default.
- `set_indicator_weight(weight)` — indicator thickness in px (Flutter `indicatorWeight`); `0` restores the role default (3 px primary / 2 px secondary).
- `set_indicator_size(size)` — `"tab"` (full tab width) or `"label"` (label width) — Flutter `indicatorSize`. Defaults to `"tab"` for secondary, `"label"` for primary.
- `set_label_color(color)` / `set_unselected_label_color(color)` — override active / inactive label+icon colors; `None` restores role defaults.
- `set_divider_color(color)` — override the bottom divider color; `None` restores the default.

**Signals:**

- `changed = Signal(int)` — emitted with the active index when a tab is selected (also fires for programmatic `set_selected_index`).

### MdTab

```python
MdTab(label="", parent=None, *, icon="", secondary=False)
```

- `set_label_colors(selected, unselected)` — override the active / inactive label+icon colors (`QColor` or `None` for the role default). Usually set through the `MdTabs` methods above.
- `label_width()` — pixel width of the label text (used for `"label"`-sized indicators).
- No signals of its own; the inherited `QAbstractButton` `toggled(bool)` / `clicked` apply.

## Notes

- The bar is fixed at 48 px tall; each tab is at least 90 px wide (minimum 72). A 1 px divider (`surface-container-highest`) runs under the whole strip.
- Primary tabs stack an optional 24 px icon above the label and use a short rounded label-width indicator; secondary tabs are label-only with a full-tab-width indicator. Active label/icon is `primary` (primary tabs) or `on-surface` (secondary); inactive is `on-surface-variant`. Active icons use the filled Material Symbols axis.
- The active indicator slides to the selected tab (`SHORT4` duration, `EMPHASIZED` easing); it snaps without animation when motion is disabled, the widget is not yet visible, or on the first selection.
- Indicator corner shape: rounded top corners only, radius equal to the indicator height.
- With `scrollable=True`, selecting a tab auto-scrolls it into view with a 24 px margin; scrollbars are always hidden.
- Color overrides take `QColor` values; these are the only widgets in the family exposing raw-color overrides (mirroring Flutter's `TabBar` theme parameters).
- The color-override setters (`set_label_color` etc.) are `MdTabs`-level and apply to all current and future tabs.
- Note this is a tab *bar* only — pair it with your own `QStackedWidget` (or similar) via `changed`. For a tab bar inside a top app bar, see the bottom slot in [top-app-bar](./top-app-bar.md).
- See [../theming.md](../theming.md) for color roles.
