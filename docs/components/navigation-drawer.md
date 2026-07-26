# Navigation drawer

Side panel of navigation destinations.

**Classes:** `MdNavigationDrawer` · **Source:** `src/material_qt/widgets/navigationdrawer/`
**Spec:** https://m3.material.io/components/navigation-drawer — ports Material Web's `labs/navigationdrawer`.

## Usage

```python
from material_qt import MdNavigationDrawer

drawer = MdNavigationDrawer(headline="Mail")
for label, icon in [("Inbox", "inbox"), ("Starred", "star"),
                    ("Sent", "send"), ("Drafts", "drafts")]:
    drawer.add_destination(label, icon=icon)
drawer.add_divider()
drawer.add_section("Labels")
drawer.add_destination("Work", icon="work")
drawer.add_destination("Personal", icon="person")
drawer.changed.connect(lambda index: print("active:", index))
```

## API

### MdNavigationDrawer

```python
MdNavigationDrawer(parent=None, *, headline="")
```

- `add_destination(label, *, icon="", active_icon="")` — append a destination row and return it; icons are Material Symbols ligature names. The first destination added is selected automatically.
- `add_section(text)` — add a non-destination section header (`title-small`, `on-surface-variant`) and return the `QLabel`.
- `add_divider()` — add an `MdDivider` between destinations and return it.
- `add_widget(widget)` — add an arbitrary widget; it does not count as a destination.
- `set_footer(widget)` — pin a widget to the drawer's bottom, below the destinations (Flutter `NavigationDrawer.footer`); replaces any previous footer.
- `set_width(width)` — override the drawer's container width (Flutter `Drawer.width`).
- `selected_index` — property, index of the active destination among destinations only, or `-1`; assignable.
- `set_selected_index(index)` — programmatically select the destination at `index`.

**Signals:**

- `changed = Signal(int)` — emitted when the active destination changes. The index counts destinations only, ignoring sections, dividers, and arbitrary widgets.

## Notes

- Fixed width 360 px by default (the M3 navigation-drawer container width); override with `set_width`.
- The drawer surface is `surface-container-low`. Destination rows are 56 px tall full-corner pills; the active row fills `secondary-container` with `on-secondary-container` icon (filled glyph) and label, inactive rows are transparent with `on-surface-variant`.
- Mixed content: destinations can be interspersed with `add_section` headers, `add_divider`, and `add_widget`, like Flutter's `NavigationDrawer` children. Only `add_destination` rows participate in selection and index numbering.
- Selection is exclusive via an internal `QButtonGroup`; `changed` also fires for programmatic `set_selected_index` calls.
- The optional `headline` constructor kwarg adds a `title-small` header above the destinations; it restyles itself on theme change.
- `active_icon` swaps the glyph while the row is selected; it defaults to `icon`.
- The widget is a plain panel — it does not manage modal/overlay presentation or open/close animation; embed it in your own layout or overlay.
- See [navigation-rail](./navigation-rail.md) and [navigation-bar](./navigation-bar.md) for the other navigation surfaces, and [../theming.md](../theming.md) for color roles.
