# Selection controls — Flutter ↔ material_qt parity

Status legend: ✅ verified · ➕ added this pass · 🆕 built this pass · ⛔ N/A (rationale)

The Qt port is idiomatic QObject: callbacks → Qt Signals (`toggled(bool)`,
`clicked`); state via `setChecked()`/`isChecked()` + `set_*()`/`@property`;
colors come from theme roles (`ThemeManager`/`ColorRole`), so Flutter's
per-instance color/style knobs are intentionally **not** ported.

## Checkbox (checkbox.dart) → MdCheckbox (widgets/checkbox) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| value | `setChecked()` / `isChecked()` (QAbstractButton) | ✅ |
| onChanged | `toggled(bool)` / `clicked` Signal | ✅ |
| tristate | `indeterminate` @property + `set_indeterminate()` + `indeterminate=` ctor kwarg | ✅ ➕ |
| isError | `error` @property + `set_error()` + `error=` ctor kwarg | ✅ |
| semanticLabel | `label` @property + `set_label()` + `label=` ctor kwarg → `setAccessibleName()` | ➕ |
| (disabled = onChanged null) | `setEnabled(False)` (38% opacity render) | ✅ |
| activeColor | ⛔ theme role `PRIMARY` container fill | ⛔ |
| checkColor | ⛔ theme role `ON_PRIMARY` checkmark | ⛔ |
| fillColor | ⛔ theme roles (PRIMARY/ERROR) | ⛔ |
| focusColor / hoverColor / overlayColor | ⛔ ripple + focus ring use theme roles | ⛔ |
| splashRadius | ⛔ 40px state layer is fixed by foundation | ⛔ |
| shape / side | ⛔ M3 box shape (2px corner, 2px outline) fixed | ⛔ |
| materialTapTargetSize / visualDensity | ⛔ fixed 40px target | ⛔ |
| mouseCursor | ⛔ default Qt cursor | ⛔ |
| focusNode / autofocus | ⛔ standard Qt focus (`setFocus`, `setFocusPolicy`) | ⛔ |
| Checkbox.adaptive | ⛔ no Cupertino target in Qt | ⛔ |

- [x] all properties verified or added

## Radio (radio.dart) → MdRadio (widgets/radio) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| value / groupValue | group membership via `autoExclusive` (shared parent) or `QButtonGroup`; selected = `isChecked()` | ✅ |
| onChanged | `toggled(bool)` / `clicked` Signal | ✅ |
| toggleable | `toggleable` @property + `set_toggleable()` + `toggleable=` ctor kwarg; click on selected radio deselects it (exclusivity temporarily cleared so Qt's own click machinery emits the standard signals) | ➕ |
| enabled | `setEnabled()` / `isEnabled()` | ✅ |
| semanticLabel | `label` @property + `set_label()` + `label=` ctor kwarg → `setAccessibleName()` | ➕ |
| groupRegistry / RadioGroup | ⛔ Qt uses `QButtonGroup` / `autoExclusive` for single-selection | ⛔ |
| activeColor / fillColor / backgroundColor | ⛔ theme roles (ring/dot = PRIMARY, unselected ring = ON_SURFACE_VARIANT) | ⛔ |
| focusColor / hoverColor / overlayColor | ⛔ ripple + focus ring use theme roles | ⛔ |
| splashRadius | ⛔ 40px state layer fixed | ⛔ |
| innerRadius | ⛔ M3 10px dot fixed | ⛔ |
| side | ⛔ M3 2px ring fixed | ⛔ |
| materialTapTargetSize / visualDensity | ⛔ fixed 40px target | ⛔ |
| mouseCursor | ⛔ default Qt cursor | ⛔ |
| focusNode / autofocus | ⛔ standard Qt focus | ⛔ |
| useCupertinoCheckmarkStyle / Radio.adaptive | ⛔ no Cupertino target in Qt | ⛔ |

- [x] all properties verified or added

## Switch (switch.dart) → MdSwitch (widgets/switch) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| value | `setChecked()` / `isChecked()` | ✅ |
| onChanged | `toggled(bool)` / `clicked` Signal | ✅ |
| thumbIcon | `set_thumb_icon(on=, off=)` + `thumb_icon_on`/`thumb_icon_off` @property + `thumb_icon_on=`/`thumb_icon_off=` ctor kwargs; ligature drawn on the handle (off when unselected, on when selected), 16px, `ON_PRIMARY_CONTAINER` (38% `ON_SURFACE` when disabled) | ➕ |
| (disabled) | `setEnabled()` / `isEnabled()` | ✅ |
| semanticLabel (via Semantics) | `label` @property + `set_label()` + `label=` ctor kwarg → `setAccessibleName()` | ➕ |
| activeColor / activeThumbColor / activeTrackColor | ⛔ theme roles (track PRIMARY, handle ON_PRIMARY) | ⛔ |
| inactiveThumbColor / inactiveTrackColor / thumbColor / trackColor | ⛔ theme roles (track SURFACE_CONTAINER_HIGHEST, handle OUTLINE) | ⛔ |
| trackOutlineColor / trackOutlineWidth | ⛔ M3 2px `OUTLINE` border (fades as selected) | ⛔ |
| activeThumbImage / inactiveThumbImage / on*ImageError | ⛔ image thumbs not part of M3 switch; use thumbIcon | ⛔ |
| materialTapTargetSize / padding | ⛔ fixed 52×40 target | ⛔ |
| focusColor / hoverColor / overlayColor | ⛔ handle state layer uses theme roles | ⛔ |
| splashRadius | ⛔ 40px handle state layer fixed | ⛔ |
| mouseCursor | ⛔ default Qt cursor | ⛔ |
| dragStartBehavior | ⛔ Qt toggles on click; no drag gesture | ⛔ |
| focusNode / onFocusChange / autofocus | ⛔ standard Qt focus | ⛔ |
| Switch.adaptive / applyCupertinoTheme | ⛔ no Cupertino target in Qt | ⛔ |

- [x] all properties verified or added

## List-tile composites — ⛔ covered by composition

`checkbox_list_tile.dart`, `radio_list_tile.dart`, `switch_list_tile.dart` map
to MdCheckbox/MdRadio/MdSwitch placed in an `MdItem`/`MdListItem` row. No
dedicated tile widget needed; compose the control with a list item.

## Coordinator follow-up

None required. No edits were made to shared files (`gallery.py`,
`core/__init__.py`, `widgets/__init__.py`). The new ctor kwargs / `set_*()`
methods are additive and backward-compatible; existing gallery demos keep
working. Optional future polish: expose `thumb_icon`/`toggleable` in the switch
and radio gallery demos.
