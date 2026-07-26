# Icon button

Icon-only buttons, optionally toggleable.

**Classes:** `MdIconButton`, `MdFilledIconButton`, `MdFilledTonalIconButton`, `MdOutlinedIconButton`, `IconButtonStyle` · **Source:** `src/material_qt/widgets/iconbutton/`
**Spec:** <https://m3.material.io/components/icon-buttons>. Ports Material Web's `iconbutton/` package (`md-icon-button`, `md-filled-icon-button`, `md-filled-tonal-icon-button`, `md-outlined-icon-button`).

## Usage

```python
from material_qt import MdIconButton, MdFilledIconButton

edit = MdFilledIconButton("edit", parent=page)
edit.clicked.connect(on_edit)

# Toggle mode: checkable, with an optional distinct selected glyph.
fav = MdIconButton("favorite", parent=page,
                   toggle=True, selected_icon="favorite", checked=True)
fav.toggled.connect(on_favorite_changed)
```

Run the demo: `python -m material_qt.widgets.iconbutton.demo`.

## API

### MdIconButton

Standard icon button (no container). Extends `QAbstractButton` via `LongPressMixin` and `MaterialWidgetMixin`.

```python
MdIconButton(
    icon: str = "",
    parent: QWidget | None = None,
    *,
    toggle: bool = False,
    selected_icon: str = "",
    checked: bool = False,
    tooltip: str = "",
    autofocus: bool = False,
)
```

- `icon_name` — property; the unselected Material Symbols ligature name (e.g. `"favorite"`), never a `QIcon`.
- `set_icon(name)` — change the unselected icon.
- `toggle=True` calls `setCheckable(True)`; use inherited `isChecked()` / `setChecked()` to read or drive the state. `selected_icon` (if non-empty) is drawn instead of `icon` while checked.
- Inherited Qt API to use directly: `clicked`, `toggled(bool)`, `setChecked()`, `setEnabled()`, `setToolTip()`. There is no snake_case enabled/checked API — the Qt camelCase methods are the intended surface.

**Signals:**

- `longPressed = Signal()` — emitted on a sustained press (Flutter `onLongPress` parity).
- `clicked`, `toggled(bool)` (inherited from `QAbstractButton`).

### MdFilledIconButton / MdFilledTonalIconButton / MdOutlinedIconButton

The variants add no methods; each overrides only the class-level `STYLE: IconButtonStyle` to pick container/icon/outline color roles for static and toggle modes. Construction is identical to `MdIconButton`.

### IconButtonStyle

Frozen dataclass of per-variant colors for static and toggle (selected/unselected) modes:

- `container_role: ColorRole | None` — static container fill (`None` = no container).
- `icon_role: ColorRole` — static icon color.
- `outline_role: ColorRole | None = None` — static outline (outlined variant).
- `toggle_unselected_container: ColorRole | None = None` / `toggle_selected_container: ColorRole | None = None` — container per toggle state.
- `toggle_unselected_icon: ColorRole = ColorRole.ON_SURFACE_VARIANT` / `toggle_selected_icon: ColorRole = ColorRole.PRIMARY` — icon per toggle state.
- `toggle_unselected_outline: ColorRole | None = None` — outlined toggle shows its outline only while unselected.

## Notes

- Variant pattern: subclasses override only `STYLE`; sizing, painting, and interaction live in `MdIconButton`.
- Fixed 40x40px circular target with a 24px glyph; the size policy is `Fixed` in both directions, so the button never stretches in layouts.
- Toggle color resolution is dynamic: a checkable button uses the `toggle_*` roles and switches container/icon (and the ripple color) on `toggled`; a non-checkable one uses the static roles.
- The outlined toggle variant drops its outline and fills with `inverse-surface` when selected, matching the component tokens.
- A long press (500 ms) fires `longPressed` and suppresses the subsequent `clicked`; moving more than 12px while pressed cancels it.
- Disabled buttons repaint with on-surface at 12% (container) / 38% (icon) opacity.
- `autofocus=True` is honored on first show.
- See also [buttons](./button.md) for labeled actions and [theming](../theming.md) for color roles.
