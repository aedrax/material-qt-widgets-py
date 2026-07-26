# Segmented buttons

Connected toggle buttons for choices.

**Classes:** `MdSegmentedButton`, `MdSegmentedButtonSet` · **Source:** `src/material_qt/widgets/segmentedbutton/`
**Spec:** <https://m3.material.io/components/segmented-buttons>. Ports Material Web's `labs/segmentedbutton` + `labs/segmentedbuttonset`, and mirrors Flutter's `SegmentedButton` / `ButtonSegment` pair (`MdSegmentedButtonSet` ↔ `SegmentedButton`, `MdSegmentedButton` ↔ `ButtonSegment`).

## Usage

```python
from material_qt import MdSegmentedButton, MdSegmentedButtonSet

# Single-select (the default).
period = MdSegmentedButtonSet(page)
for i, label in enumerate(("Day", "Week", "Month")):
    seg = MdSegmentedButton(label)
    if i == 0:
        seg.setChecked(True)
    period.add_segment(seg)
period.changed.connect(lambda indices: print("indices:", indices))

# Multi-select.
fmt = MdSegmentedButtonSet(page, multi=True)
for label in ("Bold", "Italic", "Underline"):
    fmt.add_segment(MdSegmentedButton(label))
```

Run the demo: `python -m material_qt.widgets.segmentedbutton.demo`.

## API

### MdSegmentedButton

A single segment (Flutter `ButtonSegment`). Extends `QAbstractButton` via `MaterialWidgetMixin`; it is always checkable.

```python
MdSegmentedButton(
    text: str = "",
    parent: QWidget | None = None,
    *,
    icon: str = "",
    value: Any = <unset>,
    tooltip: str = "",
    enabled: bool = True,
)
```

- `icon` is a Material Symbols ligature name (e.g. `"calendar_month"`), never a `QIcon`. The `value` default is a private sentinel, so an explicit `value=None` is preserved rather than replaced by the index fallback.
- `value() -> Any` — the segment's identifying value; if never set it falls back to the segment's index within its set (assigned by `add_segment`).
- `set_value(value)` / `has_explicit_value()` — set the value; check whether one was supplied.
- `set_show_selected_icon(show)` / `set_selected_icon(name)` — per-segment selected-checkmark config; normally driven by the parent set, not called directly.
- Inherited Qt API to use directly: `setChecked()` / `isChecked()`, `toggled(bool)`, `setToolTip()`, `setEnabled()` (the `tooltip` and `enabled` constructor args just call these).

### MdSegmentedButtonSet

The connected row (Flutter `SegmentedButton`); a plain `QWidget` with a fixed 40px height.

```python
MdSegmentedButtonSet(
    parent: QWidget | None = None,
    *,
    multi: bool = False,
    empty_selection_allowed: bool = False,
    show_selected_icon: bool = True,
    selected_icon: str = "check",
)
```

- `add_segment(segment)` — append an `MdSegmentedButton`; assigns its index as `value` if none was given, applies the set's selected-icon config, and restyles corner shapes (outer ends corner-full).
- `segments() -> list[MdSegmentedButton]` — a copy of the segment list.
- `selected_indices() -> list[int]` / `selected_values() -> list[Any]` — the current selection as indices or values.
- `set_selected_indices(indices)` — programmatic selection; does not emit `changed`. Raises `ValueError` for multiple indices on a single-select set, or for an empty selection when `empty_selection_allowed=False`.
- `show_selected_icon()` / `set_show_selected_icon(show)` — whether selected segments show the leading checkmark (Flutter `showSelectedIcon`).
- `selected_icon()` / `set_selected_icon(name)` — the selected-indicator glyph (Flutter `selectedIcon`); empty resets to `"check"`.
- `multi_selection_enabled()` / `empty_selection_allowed()` — the constructor flags.

**Signals:**

- `changed = Signal(list)` — the list of selected segment indices (mirrors `MdButtonGroup`).
- `selectionChanged = Signal(list)` — the list of selected segment *values* (Flutter parity alias for `onSelectionChanged`).

Both fire together on every user-driven selection change. Note the peer [`MdButtonGroup`](./button-group.md) has only `changed`; the names are intentionally not normalized.

## Notes

- Selection rules: with the defaults (single-select, empty disallowed) a native exclusive `QButtonGroup` guarantees the last selection cannot be cleared by clicking it. Multi-select and empty-allowed combinations are managed manually — deselecting the last segment when empty is disallowed silently re-asserts it without emitting.
- One user switch in single-select mode emits exactly one `changed`/`selectionChanged` pair, not one per internal toggle.
- Metrics: 40px height, corner-full outer ends (radius 20), 1px `outline` border, 12px horizontal padding, 18px glyph, 8px glyph–label gap, 48px minimum segment width, `label-large` text; segments expand horizontally to share the row.
- A selected segment fills `secondary-container` and (by default) shows the leading checkmark; because the checkmark changes the size hint, selection triggers `updateGeometry`, so avoid layouts that clip on re-flow.
- Unlike the common buttons, segments have no `longPressed` signal and no focus ring.
- See also [button group](./button-group.md) for the gap-separated Expressive variant.
