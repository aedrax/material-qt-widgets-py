# Reorderable list

Drag rows by a handle to reorder them.

**Classes:** `MdReorderableList` · **Source:** `src/material_qt/widgets/reorderablelist/`
**Spec:** Flutter API — [`ReorderableListView`](https://api.flutter.dev/flutter/material/ReorderableListView-class.html). Ports Flutter's `material/reorderable_list.dart`, including the desktop drag handles (`buildDefaultDragHandles`).

## Usage

```python
from material_qt import MdIcon, MdListItem, MdReorderableList

lst = MdReorderableList(parent)
for name, icon in [("Reduce", "wb_sunny"), ("Reuse", "recycling"),
                   ("Recycle", "compost"), ("Repair", "build")]:
    lst.add_item(MdListItem(name, leading=MdIcon(icon), interactive=False))

lst.reordered.connect(lambda old, new: print(f"reordered {old} -> {new}"))
```

Run the demo: `python -m material_qt.widgets.reorderablelist.demo`.

## API

### MdReorderableList

```python
MdReorderableList(parent: QWidget | None = None, *, drag_handles: bool = True)
```

- `add_item(content)` — append any `QWidget` as a new reorderable row; a trailing drag handle is added when `drag_handles` is on.
- `items` (property) — the content widgets in current (possibly reordered) order.
- `count()` — number of rows.
- `move_item(old_index, new_index)` — programmatically move a row; emits `reordered` only if the position actually changes. `new_index` is clamped into range.

**Signals:**

- `reordered = Signal(int, int)` — `(old_index, new_index)`, emitted after a drag (or `move_item`) commits a move.

### reorder_target_index

`reorder_target_index(centers, dragged_index, cursor_y)` — pure, unit-testable helper that computes the final resting index for a dragged row: the number of *other* rows whose resting center lies above the cursor. Importable from `material_qt` directly.

## Notes

- **The list owns its order.** Unlike Flutter — where `onReorder` hands you a pre-removal `newIndex` you must decrement yourself — `MdReorderableList` applies the move internally and emits `reordered(old, new)` purely as a notification, where `new` is the item's *final resting index*. A `(2, 5)` signal means "the item now sits at index 5"; mirror it onto your model with a plain `pop`/`insert`.
- With `drag_handles=True` (default) only the handle starts a drag, so interactive content (buttons, list items) still receives clicks. With `drag_handles=False` the whole row drags — best paired with non-interactive content such as `MdListItem(..., interactive=False)`.
- A press only becomes a drag after 4 px of vertical movement; a plain press-and-release on the handle changes nothing. While dragging, the lifted row gets level-3 elevation and floats over a live gap that previews the drop slot.
- Rows are positioned by manual geometry (no `QLayout`) so the lifted row can float free; each row is at least 56 px tall and an 8 px top/bottom gutter keeps the lifted row's shadow from being clipped.
- The committed drop slot is exactly the slot the preview showed (the drop target is carried from the last move, not recomputed from geometry, which would land one slot short at the bottom edge).
- Ownership: `add_item` reparents the content widget into an internal row wrapper; `items` returns the content widgets, not the wrappers.
- Deferred (vs Flutter): animated gap reflow (rows snap to their new slots instantly), auto-scroll while dragging near an edge, and a drop shadow extending past the list's own edges.
- See [List](./list.md) for the row widgets typically used as content.
