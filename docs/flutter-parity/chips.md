# Chips — Flutter ↔ material_qt parity

Maps the Flutter Material **chip** family (`chip.dart`, `action_chip.dart`,
`choice_chip.dart`, `filter_chip.dart`, `input_chip.dart`) onto the
`material_qt` chip types in `widgets/chips`. Callbacks become Qt Signals,
`set_*()` / `@property` / constructor kwargs replace named params, and
container/label colors are Material theme :class:`ColorRole`s resolved live
from `ThemeManager`.

Status legend: ✅ verified · ➕ added this pass · 🆕 built this pass · ⛔ N/A (rationale)

## Family mapping

| Flutter type | material_qt type | Notes |
|---|---|---|
| `ActionChip` | `MdAssistChip` / `MdSuggestionChip` | action chips (suggestion = on-surface-variant label) |
| `ChoiceChip` | `MdChoiceChip` 🆕 | single-select; container fill, **no** checkmark |
| `FilterChip` | `MdFilterChip` | toggle + leading checkmark; `deletable=True` adds delete |
| `InputChip` | `MdInputChip` | deletable (trailing close icon → `removed`) |
| — | `MdChip` (base) | shared base, not a Flutter type |
| — | `MdChipSet` | horizontal container with spacing + auto-remove on delete |

## Shared `ChipAttributes` (chip.dart) — base `MdChip`

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `label` (Widget) | `setText` / `set_label` + `label` property | ✅ |
| `labelStyle` | `set_label_style(QFont)` | ➕ |
| `avatar` (Widget) | `avatar` kwarg + `set_avatar(QPixmap)` / `avatar` property (24px, circular-clipped) | ➕ |
| `backgroundColor` | `set_background_color(ColorRole)` | ➕ |
| `side` | outline drawn from `OUTLINE` role (1px) when transparent/unselected | ✅ |
| `shape` | corner-small (`ShapeScale.SMALL`) via `_init_material` | ✅ |
| `elevation` | `elevated=True` kwarg → level-1 shadow via `apply_elevation` | ➕ |
| `focusNode` / `autofocus` | native Qt focus (`setFocus`, `setFocusPolicy`) + focus ring | ✅ |
| `clipBehavior` | ⛔ Flutter render-tree clip flag; Qt clips via `clip_path()` | ⛔ |
| `padding` / `labelPadding` | layout constants (`_PAD`, `_PAD_ICON`, `_GAP`) | ⛔ (internal layout) |
| `materialTapTargetSize` | ⛔ Flutter tap-target padding policy; n/a in QtWidgets | ⛔ |
| `visualDensity` | ⛔ Flutter density system; n/a | ⛔ |
| `shadowColor` | ⛔ shadow uses `SHADOW` role in `apply_elevation` | ⛔ (role-fixed) |
| `surfaceTintColor` | ⛔ M2→M3 tint shim; M3 port uses container roles directly | ⛔ |
| `iconTheme` | ⛔ Flutter IconTheme inheritance; icons take label color here | ⛔ |
| `avatarBoxConstraints` / `deleteIconBoxConstraints` | ⛔ fixed glyph/avatar sizes | ⛔ |
| `chipAnimationStyle` / `*AnimationStyle` | ⛔ Flutter AnimationStyle plumbing; ripple/repaint here | ⛔ |
| `color` (WidgetStateProperty) | ⛔ per-state color map; covered by role overrides + disabled opacity | ⛔ |
| `mouseCursor` | `setCursor` (defaults to PointingHandCursor) | ✅ |
| `tooltip` | `setToolTip` (native) | ✅ |

## DeletableChipAttributes (input_chip.dart, filter_chip.dart)

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `onDeleted` | `removed` Signal | ✅ (InputChip) / ➕ (FilterChip) |
| `deleteIcon` | trailing `"close"` glyph (`trailing_icon`) | ✅ |
| `deleteIconColor` | takes label color; override via `set_label_style`-adjacent role n/a | ⛔ (uses label role) |
| `deleteButtonTooltipMessage` | `setToolTip` (native) | ✅ |

## SelectableChipAttributes (choice/filter/input)

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `selected` | `selected` kwarg + `set_selected` / `selected` property (`setChecked`) | ✅ |
| `onSelected` | `toggled(bool)` Signal | ✅ |
| `selectedColor` | `set_selected_color(ColorRole)` (default `SECONDARY_CONTAINER`) | ➕ |
| `pressElevation` | ⛔ Flutter press-state elevation; n/a | ⛔ |
| `selectedShadowColor` | ⛔ shadow role fixed | ⛔ |
| `tooltip` | `setToolTip` (native) | ✅ |

## CheckmarkableChipAttributes (choice/filter)

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `showCheckmark` | `set_show_checkmark(bool)` (FilterChip; ChoiceChip never shows one) | ➕ |
| `checkmarkColor` | `set_checkmark_color(ColorRole)` | ➕ |

## TappableChipAttributes (action/input)

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `onPressed` | `clicked` Signal (from `QAbstractButton`) | ✅ |
| `pressElevation` | ⛔ Flutter press elevation; n/a | ⛔ |
| `tooltip` | `setToolTip` (native) | ✅ |

## DisabledChipAttributes

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `isEnabled` | `setEnabled` / `isEnabled` (native) — 0.38 label / 0.12 outline opacity | ✅ |
| `disabledColor` | ⛔ disabled is rendered via on-surface opacity per M3 | ⛔ |

## ActionChip (action_chip.dart) → MdAssistChip / MdSuggestionChip — covered ✅

| Flutter | Qt | Status |
|---|---|---|
| `ActionChip(...)` | `MdAssistChip(text, icon=, avatar=, elevated=)` | ✅ |
| `ActionChip.elevated(...)` | `MdAssistChip(..., elevated=True)` / `MdSuggestionChip(..., elevated=True)` | ➕ |
| `onPressed` | `clicked` Signal | ✅ |
| `avatar` | `avatar=` / `set_avatar` | ➕ |

## ChoiceChip (choice_chip.dart) → MdChoiceChip 🆕

| Flutter | Qt | Status |
|---|---|---|
| `ChoiceChip(...)` | `MdChoiceChip(text, selected=, icon=, avatar=, elevated=)` | 🆕 |
| `selected` / `onSelected` | `selected` + `toggled(bool)` Signal | 🆕 |
| single-select grouping | `QButtonGroup(exclusive=True)` (documented; demo shows it) | 🆕 |
| `showCheckmark` | choice chips show **no** leading checkmark (M3) — fill only | 🆕 |

## FilterChip (filter_chip.dart) → MdFilterChip — covered ✅

| Flutter | Qt | Status |
|---|---|---|
| `selected` / `onSelected` | `selected` + `toggled(bool)` Signal | ✅ |
| leading checkmark when selected | `_show_leading_check()` → "check" glyph | ✅ |
| `onDeleted` | `removed` Signal (enable via `deletable=True`) | ➕ |
| `deleteIcon` | trailing "close" glyph when `deletable=True` | ➕ |
| `FilterChip.elevated(...)` | `MdFilterChip(..., elevated=True)` | ➕ |

## InputChip (input_chip.dart) → MdInputChip — covered ✅

| Flutter | Qt | Status |
|---|---|---|
| `onDeleted` | `removed` Signal | ✅ |
| `deleteIcon` | trailing "close" glyph (always) | ✅ |
| `avatar` | `avatar=` / `set_avatar` | ➕ |
| `onPressed` | `clicked` Signal | ✅ |
| `selected` / `onSelected` | inherited `setCheckable`/`toggled` (not enabled by default) | ⛔ (input chips are not selectable in the M3 port; use FilterChip) |

---

- [x] all properties verified or added
- [ ] Coordinator follow-up: `gallery/gallery.py` showcases only flat assist /
      suggestion / filter / input chips. Consider adding the new variants built
      this pass — `MdChoiceChip` (single-select via `QButtonGroup`), an
      `elevated=True` chip, and a `deletable=True` filter chip — to the gallery
      so they are demoed. The shared-file rule kept `gallery.py` out of scope;
      `widgets/chips/demo.py` (in-scope) already demonstrates all three.
