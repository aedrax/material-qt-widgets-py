# Toolbar

Floating or docked row of actions.

**Classes:** `MdToolbar`, `ToolbarVariant` · **Source:** `src/material_qt/widgets/toolbar/`
**Spec:** <https://m3.material.io/components/toolbars>. Ports the Material 3 Expressive toolbar.

## Usage

```python
from material_qt import MdToolbar

toolbar = MdToolbar(parent=page)
for icon in ["format_bold", "format_italic", "format_underlined", "more_vert"]:
    toolbar.add_action(icon)

# Actions are plain MdIconButtons — connect to the returned button:
bold = toolbar.add_action("format_bold", toggle=True)
bold.toggled.connect(on_bold_toggled)
```

A docked variant sits flush in a layout instead of floating:

```python
from material_qt import MdToolbar, ToolbarVariant

docked = MdToolbar(parent=page, variant=ToolbarVariant.DOCKED)
```

## API

### MdToolbar

A Material 3 floating or docked toolbar of icon buttons.

```python
MdToolbar(
    parent: QWidget | None = None,
    *,
    variant: ToolbarVariant = ToolbarVariant.FLOATING,
)
```

- `add_action(icon="", *, toggle=False)` — append an action `MdIconButton` and return it; connect to the returned button's own signals. `icon` is a Material Symbols ligature name (e.g. `"format_bold"`), never a `QIcon`; `toggle=True` makes it a toggle icon button.
- `count()` — number of action buttons added.

**Signals:** none on the toolbar itself — the `MdIconButton` instances returned by `add_action` carry the click/toggle signals (see [icon button](./icon-button.md)).

### ToolbarVariant

- `FLOATING` — a fully-rounded `surface-container` pill (corner radius = half the 64px height) with level-3 elevation. The default.
- `DOCKED` — a flatter bar: `ShapeScale.LARGE` corners on `surface-container` with level-0 elevation.

## Notes

- The toolbar has a fixed 64px height with 8px content padding and 4px spacing between actions.
- Actions are laid out left to right in a plain `QHBoxLayout`; other controls can be added to the layout manually if needed, but `add_action` only creates icon buttons.
- Deferred (scaffold, per the module docstring): pairing with a FAB and the vibrant/standard color variants.
- Related bars: [bottom app bar](./bottom-app-bar.md) and [top app bar](./top-app-bar.md); color roles are covered in [theming](../theming.md).
