# Buttons — Flutter ↔ material_qt parity

Status legend: ✅ verified · ➕ added this pass · 🆕 built this pass · ⛔ N/A (rationale)

Scope: Elevated / Filled / Outlined / Text / Filled-tonal buttons (+ leading/trailing
`.icon` form), FAB (small / regular / large / extended + branded), IconButton (4
variants + toggle). No whole component was missing — every Flutter widget below
already had a material_qt equivalent, so there are **zero 🆕 builds**. This pass
filled four genuine property gaps (`tooltip`, `autofocus`, `onLongPress`,
`iconAlignment`) and verified the rest.

## Idiom mapping (applies to every row below)

- **Callbacks → Qt Signals / native events.** `onPressed`→`clicked` Signal,
  `onLongPress`→`longPressed` Signal (added), `onHover`→`enterEvent`/`leaveEvent`,
  `onFocusChange`→`focusInEvent`/`focusOutEvent` (native `QWidget` events — no
  signal added, that would be un-idiomatic).
- **Per-instance colors → theme roles.** `backgroundColor`, `foregroundColor`,
  `focusColor`, `hoverColor`, `splashColor`, `highlightColor`, `disabledColor`,
  `overlayColor` are ⛔ **by design**: color comes from the active `ThemeManager`
  palette via `ColorRole`, not per-widget args. State/hover/disabled overlays are
  produced by the shared foundation (state layer + opacity tokens).
- **Dart named params → constructor kwargs / `set_*()` / `@property`.**
- **Variant selection → subclass**, not a `style`/`type` enum arg.

---

## ButtonStyleButton base (button_style_button.dart) — shared by Elevated/Filled/Outlined/Text/Tonal

`MdButton` base in `widgets/button/button.py`.

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `onPressed(cb)` | `clicked` Signal (QAbstractButton) | ✅ |
| `onLongPress(cb)` | `longPressed` Signal (LongPressMixin, QTimer-driven) | ➕ |
| `onHover(cb)` | `enterEvent` / `leaveEvent` overrides (native) | ✅ |
| `onFocusChange(cb)` | `focusInEvent` / `focusOutEvent` (native) | ✅ |
| `child` (label widget) | `text` ctor arg → `setText()` / `text()` | ✅ |
| `icon` (`.icon` factory) | `icon=` kwarg + `set_icon()` / `icon_name` | ✅ |
| `iconAlignment` (start/end) | `icon_alignment=` kwarg + `set_icon_alignment()` (`IconAlignment`) | ➕ |
| `tooltip` | `tooltip=` kwarg → `setToolTip()` (also exposable natively) | ➕ |
| `autofocus` | `autofocus=` kwarg → `setFocus()` | ➕ |
| `focusNode` | `setFocusPolicy` / `setFocus` (Qt focus is built into QWidget) | ✅ |
| `mouseCursor` | `setCursor(PointingHandCursor)` (native) | ✅ |
| enabled state | `setEnabled()` / `isEnabled()` (native; disabled colors via tokens) | ✅ |
| elevation (Filled/Elevated) | `ButtonStyle.elevation` + `_current_elevation()` (drop-shadow effect) | ✅ |
| `style` (ButtonStyle) | ⛔ Flutter styling object; per-variant `ButtonStyle` dataclass + theme roles | ⛔ |
| `statesController` | ⛔ Flutter MaterialStatesController; Qt tracks state via `InteractionState` | ⛔ |
| `clipBehavior` | ⛔ always clips to the pill `clip_path()` | ⛔ |
| `isSemanticButton` | ⛔ Flutter semantics flag; Qt a11y via QAccessible (default button role) | ⛔ |
| `backgroundColor`/`foregroundColor`/`overlayColor`/… | ⛔ theme roles, not per-instance (see idiom mapping) | ⛔ |

### Variant coverage

| Flutter widget (file) | material_qt class | Status |
|---|---|---|
| `ElevatedButton` / `.icon` (elevated_button.dart) | `MdElevatedButton` | ✅ |
| `FilledButton` / `.icon` (filled_button.dart) | `MdFilledButton` | ✅ |
| `FilledButton.tonal` / `.tonalIcon` (filled_button.dart) | `MdFilledTonalButton` | ✅ |
| `OutlinedButton` / `.icon` (outlined_button.dart) | `MdOutlinedButton` | ✅ |
| `TextButton` / `.icon` (text_button.dart) | `MdTextButton` | ✅ |
| `MaterialButton` (material_button.dart) | — | ⛔ legacy pre-M3 button (StatelessWidget/RawMaterialButton); not ported |

Note on `.icon` form: Flutter exposes it as a named factory; material_qt folds it
into the `icon=` kwarg on the single constructor (idiomatic — no factory needed).
`iconAlignment` honours start/end in both `sizeHint` and `paintEvent`.

- [x] all base + variant properties verified or added

---

## FloatingActionButton (floating_action_button.dart) → MdFab / MdBrandedFab (widgets/fab) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `onPressed(cb)` | `clicked` Signal | ✅ |
| `onLongPress` (no FAB arg, but inherited InkWell) | `longPressed` Signal (added) | ➕ |
| `child` (icon) | `icon=` kwarg + `set_icon()` | ✅ |
| `mini` | `size=FabSize.SMALL` | ✅ |
| `.large` ctor | `size=FabSize.LARGE` | ✅ |
| `.extended` ctor / `isExtended` | `label=` kwarg (presence → extended form) | ✅ |
| `extendedIconLabelSpacing` | `_EXTENDED_GAP` constant (token) | ✅ |
| `extendedPadding` | `_EXTENDED_PAD` constant (token) | ✅ |
| `extendedTextStyle` | `label-large` typescale via `font_for` | ✅ |
| branded FAB | `MdBrandedFab` (logo overlay) | ✅ |
| `tooltip` | `tooltip=` kwarg → `setToolTip()` | ➕ |
| `autofocus` | `autofocus=` kwarg → `setFocus()` | ➕ |
| `elevation` (rest) | LEVEL3 (or LEVEL1 when `lowered=`) via `_rest_elevation()` | ✅ |
| `hoverElevation` | LEVEL4 (LEVEL2 lowered) via `_current_elevation()` | ✅ |
| `focusElevation` / `highlightElevation` | handled by `_current_elevation()` state logic (token-driven) | ✅ |
| `disabledElevation` | disabled keeps rest elevation in `_current_elevation()` | ✅ |
| `mouseCursor` | `setCursor(PointingHandCursor)` | ✅ |
| `focusNode` / focus | native QWidget focus | ✅ |
| `shape` | derived from `FabSize` (`_SIZE_SPEC` ShapeScale); extended → LARGE corner | ✅ |
| `foregroundColor`/`backgroundColor`/`focusColor`/`hoverColor`/`splashColor` | ⛔ theme roles via `FabColor` → `_COLOR_SPEC` | ⛔ |
| `heroTag` | ⛔ Flutter Hero-animation tag; no Qt analog | ⛔ |
| `materialTapTargetSize` | ⛔ Flutter tap-target padding; Qt uses fixed container size | ⛔ |
| `clipBehavior` | ⛔ always clips to shape | ⛔ |
| `enableFeedback` | ⛔ Flutter haptic/sound feedback flag; no Qt analog | ⛔ |

Color variants (surface/primary/secondary/tertiary) → `FabColor` enum; this is a
material_qt extension beyond the base FAB (Material 3 spec colors), all theme-role
driven.

- [x] all properties verified or added

---

## IconButton (icon_button.dart) → MdIconButton + 3 variants (widgets/iconbutton) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `onPressed(cb)` | `clicked` Signal | ✅ |
| `onLongPress(cb)` | `longPressed` Signal (added) | ➕ |
| `onHover(cb)` | `enterEvent` / `leaveEvent` (native) | ✅ |
| `icon` | `icon=` kwarg + `set_icon()` / `icon_name` | ✅ |
| `isSelected` (toggle) | `toggle=` kwarg (`setCheckable`) + `checked=` / `isChecked()` | ✅ |
| `selectedIcon` | `selected_icon=` kwarg | ✅ |
| `.filled` / `.filledTonal` / `.outlined` ctors | `MdFilledIconButton` / `MdFilledTonalIconButton` / `MdOutlinedIconButton` | ✅ |
| `tooltip` | `tooltip=` kwarg → `setToolTip()` | ➕ |
| `autofocus` | `autofocus=` kwarg → `setFocus()` | ➕ |
| `mouseCursor` | `setCursor(PointingHandCursor)` | ✅ |
| `focusNode` / focus | native QWidget focus | ✅ |
| enabled state | `setEnabled()` (disabled colors via opacity tokens) | ✅ |
| `iconSize` | ⛔ fixed 24px per M3 spec (`_ICON_SIZE`) | ⛔ |
| `constraints` | ⛔ fixed 40px target (`_SIZE`) per M3 spec | ⛔ |
| `padding` / `alignment` | ⛔ glyph centered in fixed circular target | ⛔ |
| `splashRadius` | ⛔ ripple radius derived from shape by foundation | ⛔ |
| `visualDensity` | ⛔ Flutter density adjustment; Qt uses fixed M3 size | ⛔ |
| `enableFeedback` | ⛔ Flutter haptic/sound feedback flag; no Qt analog | ⛔ |
| `statesController` | ⛔ Flutter states object; Qt tracks via `InteractionState` | ⛔ |
| `style` (ButtonStyle) | ⛔ per-variant `IconButtonStyle` dataclass + theme roles | ⛔ |
| `color`/`focusColor`/`hoverColor`/`highlightColor`/`splashColor`/`disabledColor` | ⛔ theme roles, not per-instance | ⛔ |

Toggle behavior: selected/unselected container + icon + outline colors come from
`IconButtonStyle.toggle_*` roles, switched on `isChecked()` (mirrors Flutter
`isSelected`).

- [x] all properties verified or added

---

## This pass — summary of changes

- **`core/long_press.py` (new):** `LongPressMixin` + `longPressed` Signal pattern —
  QTimer armed on press, cancelled on release / leave / drag past slop. Added to all
  three button families (the only callback with no native QAbstractButton mechanism).
  A fired long press suppresses the subsequent `clicked` (release returns before
  `super().mouseReleaseEvent`), mirroring Flutter where `onLongPress` suppresses
  `onTap`. The mixin owns `mouseMoveEvent` (slop-cancel) for all three widgets.
- **`tooltip=` kwarg** on `MdButton`, `MdFab`, `MdIconButton` → `setToolTip()`.
- **`autofocus=` kwarg** on the same → `setFocus()` on first `showEvent`
  (deferred because `setFocus` is a no-op before the widget is shown).
- **`IconAlignment` (start/end)** on `MdButton` — `icon_alignment=` kwarg +
  `set_icon_alignment()`, honoured in `sizeHint`/`paintEvent`.
- Tests extended in `tests/widgets/{button,fab,iconbutton}` (long-press fire/cancel,
  tooltip, icon alignment). All 21 green.

No gallery/core-export wiring required:
- `core/long_press.py` is imported directly by module path (no `core/__init__.py` edit).
- `IconAlignment` is re-exported from `widgets/button/__init__.py` (within this unit).
- No new top-level-exported class, so `widgets/__init__.py` is untouched.

### Coordinator follow-up

None.
