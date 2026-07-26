# Button

Five common button variants for actions.

**Classes:** `MdButton`, `MdElevatedButton`, `MdFilledButton`, `MdFilledTonalButton`, `MdOutlinedButton`, `MdTextButton`, `ButtonStyle`, `IconAlignment` · **Source:** `src/material_qt/widgets/button/`
**Spec:** <https://m3.material.io/components/buttons>. Ports Material Web's `button/` package (`md-elevated-button`, `md-filled-button`, `md-filled-tonal-button`, `md-outlined-button`, `md-text-button`).

## Usage

```python
from material_qt import (
    MdElevatedButton, MdFilledButton, MdFilledTonalButton,
    MdOutlinedButton, MdTextButton,
)

save = MdFilledButton("Save", icon="save", parent=page)
save.clicked.connect(on_save)

cancel = MdTextButton("Cancel", parent=page)
disabled = MdOutlinedButton("Unavailable", parent=page)
disabled.setEnabled(False)
```

Run the demo: `python -m material_qt.widgets.button.demo`.

## API

### MdButton

Base class shared by all five variants; it is concrete (it defaults to filled colors), but use a variant subclass for real styling. Extends `QAbstractButton` via `LongPressMixin` and `MaterialWidgetMixin`.

```python
MdButton(
    text: str = "",
    parent: QWidget | None = None,
    *,
    icon: str = "",
    icon_alignment: IconAlignment = IconAlignment.START,
    tooltip: str = "",
    autofocus: bool = False,
)
```

- `icon_name` — property; the current Material Symbols ligature name (e.g. `"save"`), never a `QIcon`.
- `set_icon(name)` — change the icon; triggers a geometry update.
- `icon_alignment` / `set_icon_alignment(alignment)` — leading (`START`) vs. trailing (`END`) icon placement.
- Inherited Qt API to use directly: `clicked`, `text()` / `setText()`, `setEnabled()`, `setToolTip()`, `setFocus()`. There is no snake_case `set_enabled` on buttons — the Qt camelCase methods are the intended surface here (the widget reacts to `EnabledChange` events).
- Space/Enter keyboard activation comes from `QAbstractButton`.

**Signals:**

- `longPressed = Signal()` — emitted on a sustained press (Flutter `onLongPress` parity).
- `clicked` (inherited from `QAbstractButton`).

### MdElevatedButton / MdFilledButton / MdFilledTonalButton / MdOutlinedButton / MdTextButton

The variants add no methods; each overrides only the class-level `STYLE: ButtonStyle` to select container/label/outline color roles and rest/hover/pressed elevation. Construction is identical to `MdButton`.

### ButtonStyle

Frozen dataclass mirroring the per-variant component tokens:

- `container_role: ColorRole | None` — `None` means a transparent container (outlined, text).
- `label_role: ColorRole` — label and icon color.
- `outline_role: ColorRole | None` — `None` means no outline.
- `elevation`, `hover_elevation`, `pressed_elevation: ElevationLevel` — rest/hover/pressed shadow levels.
- `text_padding: bool = False` — the text variant's tighter 12px horizontal padding.

### IconAlignment

Enum for icon placement (Flutter parity): `START` (leading, the default) and `END` (trailing).

## Notes

- Variant pattern: subclasses override only `STYLE`; all geometry, painting, and interaction live in `MdButton`. Custom color schemes can be made the same way.
- Metrics (from the button tokens / M3 spec): 40px height, corner-full pill shape, `label-large` typescale, 18px icon, 24px horizontal padding (16px on the icon side, 12px for the text variant), 8px icon–label gap. `sizeHint()` returns exactly this content-fitted size.
- A long press (500 ms, Android's default timeout) fires `longPressed` and suppresses the subsequent `clicked` — a long press replaces the tap, mirroring Flutter. Moving more than 12px while pressed cancels the long press.
- Disabled buttons repaint with on-surface at 12% (container) / 38% (label) opacity and cast no shadow.
- `autofocus=True` is honored on first show (`setFocus` before show is a no-op in Qt).
- Elevation changes on hover/press are driven by a `QGraphicsDropShadowEffect`, not painted; only the elevated/filled/tonal variants lift on hover.
- See also [icon buttons](./icon-button.md), [FAB](./fab.md), and [theming](../theming.md) for color roles.
