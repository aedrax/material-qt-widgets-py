# Navigation bar

Bottom bar switching destinations.

**Classes:** `MdNavigationBar` · **Source:** `src/material_qt/widgets/navigationbar/`
**Spec:** https://m3.material.io/components/navigation-bar — ports Material Web's `labs/navigationbar`.

## Usage

```python
from material_qt import MdNavigationBar

bar = MdNavigationBar()
bar.add_destination("Home", icon="home")
bar.add_destination("Mail", icon="mail", badge="8")       # count pill
bar.add_destination("Alerts", icon="notifications", badge="")  # dot
bar.add_destination("Profile", icon="person")
bar.changed.connect(lambda index: print("active:", index))

# Show labels only on the selected destination:
sel = MdNavigationBar(label_behavior="selected")
```

## API

### MdNavigationBar

```python
MdNavigationBar(parent=None, *, label_behavior="always")
```

- `add_destination(label, *, icon="", active_icon="", badge=None)` — append an `MdNavigationTab` destination and return it. `icon`/`active_icon` are Material Symbols ligature names; `badge` of `""` shows a dot, any other string a count pill, `None` no badge. The first destination added is selected automatically.
- `set_label_behavior(behavior)` — `"always"` / `"selected"` / `"hide"`; applies to all current and future destinations.
- `selected_index` — property, index of the active destination or `-1` if none; assignable.
- `set_selected_index(index)` — programmatically select the destination at `index`.

**Signals:**

- `changed = Signal(int)` — emitted with the destination index when the active destination changes.

## Notes

- The bar is fixed at 80 px tall on a `surface-container` background, matching the M3 spec; the M3 guidance is 3–5 destinations, though the widget does not enforce a count.
- Destinations are `MdNavigationTab` widgets (see [navigation-tab](./navigation-tab.md)); `add_destination` returns the tab so you can call `set_badge` later.
- Badge semantics come from the tab: `""` renders a small `error`-colored dot at the icon's top-right, a non-empty string renders a 16 px count pill.
- Selection is exclusive via an internal `QButtonGroup`; `changed` fires both for user clicks and programmatic `set_selected_index` calls (it is driven by the tab's `toggled` signal).
- `active_icon` lets a destination swap to a different glyph when selected; the icon is also drawn with the filled Material Symbols axis while active.
- `sizeHint()` reports at least 360 px wide (the sum of tab hints otherwise); tabs expand to share the width evenly.
- See [../theming.md](../theming.md) for color roles and [../usage.md](../usage.md) for app setup.
