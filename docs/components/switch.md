# Switch

Toggle the state of a single item.

**Classes:** `MdSwitch` · **Source:** `src/material_qt/widgets/switch/`
**Spec:** [m3.material.io/components/switch](https://m3.material.io/components/switch). Ports Material Web's `md-switch`.

## Usage

```python
from material_qt import MdSwitch

off = MdSwitch(parent)
on = MdSwitch(parent, checked=True)

# Optional handle icons (Material Symbols ligature names), resolved by state.
with_icons = MdSwitch(parent, thumb_icon_on="check", thumb_icon_off="close")

on.toggled.connect(lambda checked: print("switch:", checked))
```

Run the demo: `python -m material_qt.widgets.switch.demo`.

## API

### MdSwitch

```python
MdSwitch(
    parent: QWidget | None = None,
    *,
    checked: bool = False,
    thumb_icon_on: str | None = None,
    thumb_icon_off: str | None = None,
    label: str | None = None,
)
```

- `thumb_icon_on` (read-only property) — ligature name drawn on the handle while selected, or `None`.
- `thumb_icon_off` (read-only property) — ligature name drawn on the handle while unselected, or `None`.
- `set_thumb_icon(on=None, off=None)` — set both handle icons (Material `thumbIcon`); `on` shows while selected, `off` while unselected, and `None` shows no icon for that state. This mirrors Flutter's active/inactive icon resolution.
- `label` (property) / `set_label(label)` — accessible name (Material `semanticLabel`); maps to `accessibleName`, no visible text is drawn.
- Inherited from `QAbstractButton`: `setChecked(bool)` / `isChecked()` / `toggle()` for the on/off state (no snake_case wrapper exists; use the Qt API). Space activates the switch.

**Signals:**

- `toggled(bool)` — inherited from `QAbstractButton`; emitted on any on/off change.
- `clicked(bool)` — inherited from `QAbstractButton`; emitted on user activation.

The widget defines no signals of its own.

## Notes

- Base class: `QAbstractButton` (checkable) with the `MaterialWidgetMixin` foundation. The ripple is deliberately disabled (`ripple=False`); instead a 40 px state layer is painted around the moving handle on hover/press, matching the M3 switch anatomy. The focus ring is still supplied by the foundation.
- Metrics: 52×32 track (2 px `outline` border while unselected), widget height 40 px to house the handle state layer; handle diameter 16 px unselected, 24 px selected, growing to 28 px while pressed; thumb icons render at 16 px. `sizeHint()` is 52×40.
- Toggling animates handle position and size over 200 ms (`Duration.SHORT4`) with emphasized easing; track and handle colors crossfade during the same animation. The state snaps without animation when the widget is not visible or motion is disabled.
- Disabled state: track at 0.12 opacity, handle `on-surface` at 0.38 opacity.
- Thumb icons require the bundled Material Symbols font (via the icon widget's `material_symbols_font`); when the font is unavailable the icon is simply skipped.
- See also [Checkbox](./checkbox.md) and [Radio](./radio.md); theming is covered in [../theming.md](../theming.md).
