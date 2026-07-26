# Floating action button (FAB)

Floating action button for the primary action.

**Classes:** `MdFab`, `MdBrandedFab`, `FabSize`, `FabColor` · **Source:** `src/material_qt/widgets/fab/`
**Spec:** <https://m3.material.io/components/floating-action-button>. Ports Material Web's `fab/` package (`md-fab`, `md-branded-fab`), including the extended (labeled) form.

## Usage

```python
from material_qt import MdFab, MdBrandedFab, FabColor, FabSize

fab = MdFab("edit", parent=page, size=FabSize.LARGE)
fab.clicked.connect(on_edit)

# Extended FAB: icon + label, always 56px tall.
compose = MdFab("add", parent=page, label="Compose", color=FabColor.PRIMARY)

# Branded FAB: surface FAB with a multicolor logo placeholder.
branded = MdBrandedFab(parent=page, label="Create")
```

Run the demo: `python -m material_qt.widgets.fab.demo`.

## API

### MdFab

Extends `QAbstractButton` via `LongPressMixin` and `MaterialWidgetMixin`.

```python
MdFab(
    icon: str = "",
    parent: QWidget | None = None,
    *,
    size: FabSize = FabSize.REGULAR,
    color: FabColor = FabColor.SURFACE,
    label: str = "",
    lowered: bool = False,
    tooltip: str = "",
    autofocus: bool = False,
)
```

- `icon` is a Material Symbols ligature name (e.g. `"edit"`), never a `QIcon`.
- `set_icon(name)` — change the icon.
- `label` — a non-empty label produces the extended FAB: 56px tall, `label-large` text beside the icon, corner-large shape regardless of `size`.
- `lowered=True` rests at elevation level 1 (rising to 2 on hover) instead of level 3 (rising to 4).
- Inherited Qt API to use directly: `clicked`, `setEnabled()`, `setToolTip()`. There is no snake_case enabled API — the Qt camelCase methods are the intended surface.
- `size`, `color`, `label`, and `lowered` are constructor-only; there are no setters for them.

**Signals:**

- `longPressed = Signal()` — emitted on a sustained press (Flutter `onLongPress` parity).
- `clicked` (inherited from `QAbstractButton`).

### MdBrandedFab

A surface FAB whose icon slot holds a multicolor logo. The logo is a placeholder drawn from the four Material key colors (primary/secondary/tertiary/error quadrants), since branded logos are app-specific.

```python
MdBrandedFab(
    parent: QWidget | None = None,
    *,
    size: FabSize = FabSize.REGULAR,
    label: str = "",
)
```

Color is fixed to `FabColor.SURFACE`; `label` makes an extended branded FAB. All `MdFab` behavior (signals, elevation, long press) is inherited.

### FabSize

`SMALL` (40px container, corner-medium, 24px icon), `REGULAR` (56px, corner-large, 24px icon), `LARGE` (96px, corner-extra-large, 36px icon).

### FabColor

`SURFACE`, `PRIMARY`, `SECONDARY`, `TERTIARY` — each maps to a container/foreground role pair (e.g. `PRIMARY` uses `primary-container` / `on-primary-container`).

## Notes

- The FAB has a `Fixed` size policy in both directions; `sizeHint()` is the square container size, or padded icon+gap+label width by 56px when extended (extended padding 16px, icon–label gap 12px).
- Rest elevation is level 3, rising to level 4 on hover (levels 1 → 2 when `lowered`); disabling does not drop the shadow — a FAB keeps its rest elevation when disabled, unlike common buttons.
- There is no disabled repaint styling: colors do not dim when disabled, so prefer hiding a FAB over disabling it.
- A long press (500 ms) fires `longPressed` and suppresses the subsequent `clicked`; moving more than 12px while pressed cancels it.
- `autofocus=True` is honored on first show.
- The FAB casts a drop shadow via `QGraphicsDropShadowEffect`; give it breathing room in layouts so the shadow is not clipped (see how [FAB menu](./fab-menu.md) insets its items).
- See also [FAB menu](./fab-menu.md) for a FAB that expands into actions.
