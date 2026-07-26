# Architecture

material-qt is built as four layers, each depending only on the ones above
it:

```
tokens/    pure Python design values — generated, headless, never imports Qt
theme/     ColorRole → QColor resolution at runtime + the themeChanged signal
core/      shared QWidget machinery: ripple, focus ring, elevation, motion…
widgets/   53 component packages composing all of the above
```

## Tokens (`material_qt.tokens`)

Design values transcribed from upstream
[Material Web](https://github.com/material-components/material-web)'s SCSS
tokens, **version v0_192**. The generator is `scripts/gen_tokens.py`; its
output is committed under `tokens/_generated/` (headers say "GENERATED — DO
NOT EDIT"). The invariant, stated in the package docstring: everything in
`tokens/` is headless-testable and must never import Qt.

| Module | Public API |
| --- | --- |
| `color` | `ColorRole` — `StrEnum`, 48 roles, kebab-case values (`"on-surface-variant"`); `resolve_hex(role, dark)` chain role → tone key → palette hex |
| `typography` | `TypescaleRole` (15 roles), `TypescaleSpec` (frozen dataclass; rem + px accessors), `spec_for(role)`, `REM_PX = 16.0` |
| `shape` | `ShapeScale` (NONE…FULL), `CornerRadii` (per-corner, `.uniform()`, `.from_scale()`, `.from_shorthand()`), `FULL_SENTINEL = 9999` |
| `elevation` | `ElevationLevel` (IntEnum 0–5, `.dp`), `ShadowSpec`, `key_shadow()`, `ambient_shadow()` |
| `motion` | `Duration` (SHORT1…EXTRA_LONG4, `.ms`), `Easing` (standard/emphasized/legacy families, `.control_points` → cubic-bezier) |
| `state` | `StateLayer` (HOVER/FOCUS/PRESSED/DRAGGED, `.opacity`) |

> **Regeneration caveat:** `gen_tokens.py --repo-root` must point at a
> checkout of the upstream material-web (JS) repository containing
> `tokens/versions/v0_192/*.scss`; this repository does not vendor the SCSS.
> The committed `_generated/` output is the source of truth day-to-day.

## Theme (`material_qt.theme`)

`ColorScheme` turns the token tables into immutable `ColorRole → QColor`
maps (one light, one dark, cached); `ThemeManager` is the app-wide singleton
that picks the active scheme, layers runtime overrides on top, and emits
`themeChanged`. Covered in depth in [Theming](./theming.md).

## Core (`material_qt.core`)

The Qt-dependent machinery every widget shares.

### MaterialWidgetMixin — the base contract

Nearly every component mixes `MaterialWidgetMixin` in before its Qt base and
calls `_init_material(...)` at the end of `__init__`:

```python
class MdCard(MaterialWidgetMixin, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_material(
            shape=ShapeScale.MEDIUM,
            elevation=ElevationLevel.LEVEL1,
            ripple=False,
            surface_role=ColorRole.SURFACE_CONTAINER_LOW,
        )
```

`_init_material(*, shape, typescale, elevation, ripple, focus_ring,
ripple_role, surface_role)` wires, in one call:

- **Theme reactivity** — `themeChanged → update()`, plus re-applying the
  drop-shadow effect (its color is baked in at apply time).
- **`self.interaction`** — an `InteractionState` tracking
  enabled/hovered/pressed/focused/dragged, with Material's precedence
  (pressed > dragged > focus > hover) and `changed → update()`.
- **Shape** — `self._radii` (a `CornerRadii`), used consistently to clip
  the surface, the ripple, and the focus ring; `clip_path()` exposes it.
- **`self.ripple`** — a `RippleController` (optional): an overlay child
  widget animating hover/press state layers and the expanding press ripple.
- **`self.focus_ring`** — a `FocusRingController` (optional): the animated
  outer ring on keyboard focus; forces `StrongFocus` if the widget had
  `NoFocus`.
- **Typography** — applies a `TypescaleRole` font when given.
- **Elevation** — `apply_elevation(widget, level)`, a
  `QGraphicsDropShadowEffect` derived from the ambient shadow tokens.

Subclasses get `radii` / `set_radii()`, `set_elevation()`, and
`paint_material_surface(painter)` — the themed, shape-clipped fill to call
from `paintEvent`. `MaterialWidget` is the concrete ready-made surface.

### State layers, ripple, focus ring

`StateLayerPainter` resolves the state-layer color **at every paint** from
the current theme — this is why theme switches need only a repaint.
`RippleController` and `FocusRingController` are `QObject`s owning private
transparent overlay children, so composite widgets can also instantiate
them directly for sub-regions.

### Motion

`core.motion` wraps `QPropertyAnimation` in token terms:

```python
from material_qt.core import animate
from material_qt.tokens import Duration, Easing

animate(widget, b"pos", end_pos, duration=Duration.MEDIUM2,
        easing=Easing.EMPHASIZED, on_finished=cleanup)
```

`MOTION_ENABLED` is a module flag: when `False`, animations complete
instantly (end value applied, `on_finished` still fired) — used by the test
suite and usable for a reduced-motion setting. Note it is imported by name
into widget modules, so tests patch it on the *widget's* module.

### Modal overlay

`ModalOverlay` is the shared base for `MdDialog`, `MdDatePicker`,
`MdTimePicker`, and `MdSearchView`: scrim painting, fade/slide-in, Esc and
scrim-click dismissal, a focus trap cycling the panel's tab targets, and
`rejected` / `closed` signals. Modal lifecycle fixes belong here, not in
subclasses.

### Long press

`LongPressMixin` gives buttons Flutter's `onLongPress` (500 ms hold, 12 px
slop). Contract quirk worth knowing: the *declaring class* must define
`longPressed = Signal()` itself — a Signal doesn't reliably inherit through
a plain mixin across the QObject metaclass.

### Responsive layout

`WindowSizeClass` implements the M3 window size classes (COMPACT < 600 ≤
MEDIUM < 840 ≤ EXPANDED < 1200 ≤ LARGE < 1600 ≤ EXTRA_LARGE);
`ResponsiveHelper(widget)` emits `sizeClassChanged` only on class
transitions. The gallery uses this to swap its navigation drawer between
persistent and modal. `clamp_dialog_width(available)` is the shared
`min(560, available - 48)` dialog rule.

### Focus hygiene

`drop_focus_within(container)` — call before hiding any container, or Qt
reassigns focus with `TabFocusReason` and a spurious focus ring appears on
a sibling. The modal overlay does this for you.

## Typography — the type scale

The Material 3 type scale (the gallery's "Typography" page) is 15 roles —
display / headline / title / body / label, each in large / medium / small.
Fonts resolve through `core.typography_util`:

```python
from material_qt.core import apply_typography, font_for_role
from material_qt.tokens import TypescaleRole

apply_typography(label, TypescaleRole.HEADLINE_SMALL)   # sets the QFont
font = font_for_role(TypescaleRole.BODY_MEDIUM)          # or build one
```

The bundled **Roboto** registers lazily on first use, with a fallback chain
(Noto Sans, Segoe UI, Helvetica Neue, Arial). Sizes are pixel-set at
16 px/rem; letter tracking maps to `QFont.AbsoluteSpacing`.

## Widgets (`material_qt.widgets`)

One package per component, flat and alphabetical — 53 packages, all
re-exported at the package root. Conventions across them:

- **Variants as subclasses overriding a class-level style spec** — e.g. the
  five button variants override only `STYLE: ButtonStyle` (roles, elevation,
  padding); filled vs outlined text fields override only `VARIANT`.
- **Casing** — signals are camelCase (`textChanged`, `indexChanged`);
  library-added methods are snake_case (`set_icon`, `set_error`); inherited
  Qt API keeps its camelCase (`setText`, `sizeHint`). Where both exist,
  prefer the snake_case one — it updates the Material chrome too.
- **Icons as strings** — Material Symbols ligature names everywhere; see
  [usage](./usage.md#icons).
- **Pure seams** — geometry/logic that matters is factored into pure
  functions (e.g. the time picker's `angle_to_hour`, the reorderable list's
  `reorder_target_index`) so it tests headlessly.
- Some shared bases are private (`_MdTextField`, `_MdSelect`,
  `_MdAutocomplete`); their API is documented on the public variant classes.

Each package's doc in [components/](./README.md#components) covers its
constructor, methods, and exact signal names.
