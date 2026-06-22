# Segmented & button groups — Flutter ↔ material_qt parity

Status legend: ✅ verified · ➕ added this pass · 🆕 built this pass · ⛔ N/A (rationale)

This unit covers three Qt components. Only **SegmentedButton** has a 1:1 Flutter
class (`segmented_button.dart`). **ButtonGroup** and **SplitButton** are Material 3
*expressive* components with no 1:1 Flutter class — their public APIs were audited
for completeness (no external spec cross-walk was run) and noted as such.

---

## SegmentedButton (segmented_button.dart) → MdSegmentedButtonSet (widgets/segmentedbutton) — covered ✅

`SegmentedButton<T>` maps to `MdSegmentedButtonSet`; `ButtonSegment<T>` maps to
`MdSegmentedButton`. Set-level properties (selection, multi/empty/icon config)
live on the set; per-segment properties live on the segment.

### Set-level (`SegmentedButton`)

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `segments` (List<ButtonSegment>) | `add_segment(MdSegmentedButton)` / `segments() -> list` | ✅ |
| `selected` (Set<T>) | `selected_indices() -> list[int]`, `selected_values() -> list`, `set_selected_indices(indices)` | ➕ |
| `onSelectionChanged` (void Function(Set<T>)) | `changed(list)` Signal (indices) + `selectionChanged(list)` Signal (values) | ➕ |
| `multiSelectionEnabled` (bool, def false) | `multi=` ctor kwarg; `multi_selection_enabled() -> bool` | ✅ (getter ➕) |
| `emptySelectionAllowed` (bool, def false) | `empty_selection_allowed=` ctor kwarg; `empty_selection_allowed() -> bool` | ➕ |
| `showSelectedIcon` (bool, def true) | `show_selected_icon=` ctor kwarg; `show_selected_icon()` / `set_show_selected_icon(bool)` | ➕ |
| `selectedIcon` (Widget?) | `selected_icon=` ctor kwarg (glyph name, def `"check"`); `selected_icon()` / `set_selected_icon(name)` | ➕ |
| `style` (ButtonStyle) | theme-role colors (SECONDARY_CONTAINER / ON_SURFACE / OUTLINE) | ⛔ styling via ThemeManager roles, not a per-instance ButtonStyle |
| `direction` (Axis, def horizontal) | horizontal only | ⛔ `_Pos` corner-radii logic assumes a horizontal row; vertical is a layout rework, not a property toggle — see Coordinator follow-up |
| `expandedInsets` (EdgeInsets?) | Qt layout / size-policy concern | ⛔ N/A — handled by parent layout |

### Per-segment (`ButtonSegment`) → MdSegmentedButton

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `value` (T, required) | `value=` ctor kwarg; `value()` / `set_value()` (defaults to index when unset) | ➕ |
| `label` (Widget?) | `text` ctor arg (`setText`) | ✅ |
| `icon` (Widget?) | `icon=` ctor kwarg (Material Symbols glyph name) | ✅ |
| `tooltip` (String?) | `tooltip=` ctor kwarg → native `setToolTip` | ➕ |
| `enabled` (bool, def true) | `enabled=` ctor kwarg → native `setEnabled`; also `setEnabled()` at runtime | ➕ (kwarg) / ✅ (native) |

Notes:
- Single-select + empty-disallowed (the Flutter default) uses an exclusive
  `QButtonGroup` so the last selection can't be cleared by clicking it. Every
  other combination (multi-select, or single-select with empty allowed) is
  managed manually in `_on_toggled`, including re-asserting the last selection
  when `empty_selection_allowed` is `False`.
- `PySide6.QtWidgets.QButtonGroup` in this build (6.11.1) has **no**
  `ExclusionPolicy` enum (verified), so `ExclusiveOptional` is not available;
  empty-allowed single-select is hand-managed.
- `changed` mirrors sibling `MdButtonGroup.changed` (index list);
  `selectionChanged` is the value-list alias closest to Flutter's `Set<T>`.

- [x] all properties verified or added

## ButtonGroup (M3 expressive — no 1:1 Flutter class) → MdButtonGroup (widgets/buttongroup) — verified ✅

Row of separated pill toggles; single- or multi-select. No Flutter `ButtonGroup`
class exists — public API audited for completeness.

Deliberate scope note: `MdButtonGroup` intentionally does **not** mirror the
`set_selected_indices()` setter or the single-emit-on-switch behaviour added to
`MdSegmentedButtonSet` this pass. Flutter's `SegmentedButton` has a *required*,
app-managed `selected` set that demands a programmatic setter and clean change
notification; `MdButtonGroup` has no such Flutter contract, so adding that surface
would be gold-plating. Its existing `changed(list)` + `selected_indices()` are
sufficient for the expressive spec.

| Capability (M3 expressive) | Qt (QObject) equivalent | Status |
|---|---|---|
| Add toggle pill (label + icon) | `add_button(label, icon=...) -> _GroupButton` | ✅ |
| Single vs multi selection | `multi=` ctor kwarg (exclusive `QButtonGroup` when single) | ✅ |
| Selection-changed notification | `changed(list)` Signal (selected indices) | ✅ |
| Query selection | `selected_indices() -> list[int]` | ✅ |
| Selected / unselected container colors | SECONDARY_CONTAINER / SURFACE_CONTAINER_LOW theme roles | ✅ |
| Press-morph animation (pressed pill widens) | deferred (documented scaffold) | ⛔ deferred — noted in module docstring; not part of property parity |

- [x] verified complete for the expressive spec (no missing public properties)

## SplitButton (M3 expressive — no 1:1 Flutter class) → MdSplitButton (widgets/splitbutton) — verified ✅

Connected pair: primary action (leading) + dropdown (trailing). Verified against
the M3 expressive split-button spec and the labs/gb reference.

| Capability (M3 expressive) | Qt (QObject) equivalent | Status |
|---|---|---|
| Leading action click | `clicked()` Signal | ✅ |
| Trailing (dropdown) click | `trailing_clicked()` Signal | ✅ |
| Attach dropdown menu | `set_menu(MdMenu)` (opens at trailing on click) | ✅ |
| Color variants | `color=SplitButtonColor.{FILLED,ELEVATED,TONAL,OUTLINED}` | ✅ |
| Leading label / icon | `text` ctor arg + `set_text()`/`text()`; `icon=` kwarg | ✅ |
| Trailing icon | `trailing_icon=` kwarg (def `arrow_drop_down`) | ✅ |
| Enabled state (both halves) | `setEnabled()` propagates to leading + trailing | ✅ |
| Elevation by interaction (hover) | per-variant elevation spec, refreshed on enter/leave | ✅ |

- [x] verified complete for the expressive spec (no missing public properties)

## Coordinator follow-up
- None required for wiring (all additions are backward-compatible kwargs/methods;
  gallery usage of `MdSegmentedButtonSet()` / `add_segment` / `MdSegmentedButton(label)`
  is unchanged).
- Optional future work (not blocking parity): `direction=Axis.vertical` support on
  `MdSegmentedButtonSet` would require reworking `_Pos` corner-radii for a vertical
  stack; deferred as a non-trivial layout change.
