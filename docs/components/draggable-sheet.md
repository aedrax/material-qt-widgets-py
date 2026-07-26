# Draggable scrollable sheet

Resizable bottom sheet with scrollable content.

**Classes:** `MdDraggableScrollableSheet` (plus pure functions `clamp_size`, `nearest_snap`, `couple_wheel`) · **Source:** `src/material_qt/widgets/draggablesheet/`
**Spec:** https://api.flutter.dev/flutter/widgets/DraggableScrollableSheet-class.html. Ports Flutter's `DraggableScrollableSheet` (`widgets/draggable_scrollable_sheet.dart`).

## Usage

```python
from PySide6.QtWidgets import QApplication, QLabel, QWidget
from material_qt import MdDraggableScrollableSheet

app = QApplication([])
window = QWidget()
window.resize(440, 560)

sheet = MdDraggableScrollableSheet(
    window, initial_size=0.4, min_size=0.2, max_size=0.95,
    snap_sizes=[0.4, 0.7])
for i in range(30):
    sheet.add_content(QLabel(f"Item {i + 1}"))
sheet.sizeChanged.connect(lambda f: print(f"sheet at {f:.0%}"))

window.show()
app.exec()
```

Run the demo: `python -m material_qt.widgets.draggablesheet.demo`.

## API

### MdDraggableScrollableSheet

```python
MdDraggableScrollableSheet(
    parent: QWidget,
    *,
    initial_size: float = 0.5,
    min_size: float = 0.25,
    max_size: float = 1.0,
    snap: bool = True,
    snap_sizes: list[float] | None = None,
    show_handle: bool = True,
)
```

- `add_content(widget)` — appends a widget to the internal scroll area's content column.
- `size_fraction` — property; the current sheet size as a fraction of the parent height. This is Flutter's `DraggableScrollableController.size`, deliberately named `size_fraction` here because a `size` attribute would clash with `QWidget.size()`.
- `set_size(fraction, *, animated: bool = False)` — sets the size fraction, immediately or via `animate_to`.
- `animate_to(fraction)` — animates the sheet to `fraction` (clamped to `[min_size, max_size]`), emitting `sizeChanged` on each tick.
- `reset()` — animates back to the (clamped) `initial_size`.
- `frac` — a Qt `Property(float)` backed by `get_frac()` / `set_frac()`; it drives geometry and is what the snap animation animates. `set_frac` clamps, repositions, and emits `sizeChanged`.

**Signals:** `sizeChanged(float)` — emitted with the new fraction on every change (drag, wheel, animation tick).

### Pure functions

- `clamp_size(size: float, min_size: float, max_size: float) -> float` — clamps a size fraction into `[min_size, max_size]`.
- `nearest_snap(size: float, snaps: list[float]) -> float` — returns the snap fraction closest to `size` (`snaps` need not be sorted; returns `size` when the list is empty).
- `couple_wheel(angle_y: float, at_top: bool, size: float, min_size: float, max_size: float) -> str` — decides what a content wheel event does: `"grow"`, `"shrink"`, or `"scroll"`. `angle_y` is Qt's `angleDelta().y()` (positive = toward the content top).

## Notes

- This is a non-modal sheet: no scrim, no open/dismiss. It anchors itself to the bottom of its parent and sizes itself as `size_fraction` of the parent height (never smaller than the handle strip).
- Dragging the 28 px handle strip resizes freely; on release the sheet snaps to the nearest snap size when `snap=True`. The snap set is always `{min_size, max_size}` plus any `snap_sizes`, deduplicated and sorted.
- Wheel events over the content couple to the sheet (Flutter's drag/scroll coupling): wheeling toward the bottom grows the sheet until `max_size`, then scrolls; wheeling toward the top scrolls until the content is at its top, then shrinks the sheet. Each wheel notch moves the sheet by 0.08 of the parent height, and wheel resizes land free — only a handle release snaps.
- Deferred versus Flutter (per the module docstring): mouse/touch finger-drag coupling over the content (only the handle drags; the wheel couples), snap-after-wheel, and `expand` / secondary-animation niceties.
- A new drag, wheel, or `animate_to` cancels any in-flight snap animation, so the last input always wins.
- The sheet raises itself on show and repositions on parent resizes, but a parent resize does not re-raise it; if siblings are added or restacked afterwards, call `raise_()` yourself (the demo does this in its `resizeEvent`).
- The panel uses `surface-container-low`, level-1 elevation, and 28 px rounded top corners; for a modal bottom sheet see [./bottom-sheet.md](./bottom-sheet.md).
