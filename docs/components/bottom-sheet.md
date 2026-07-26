# Bottom sheet

Sheet anchored to the bottom edge.

**Classes:** `MdBottomSheet`, `MdStandardBottomSheet` · **Source:** `src/material_qt/widgets/bottomsheet/`
**Spec:** https://m3.material.io/components/bottom-sheets. The module docstring names Flutter's `showModalBottomSheet` as the upstream counterpart for the modal variant.

## Usage

```python
from PySide6.QtWidgets import QApplication, QLabel, QWidget
from material_qt import MdBottomSheet

app = QApplication([])
window = QWidget()
window.resize(480, 480)

sheet = MdBottomSheet(window)
sheet.add_content(QLabel("Share"))
for label in ["Messages", "Email", "Copy link", "Nearby"]:
    sheet.add_content(QLabel(label))
sheet.closed.connect(lambda: print("closed"))

window.show()
sheet.open()
app.exec()
```

## API

### MdBottomSheet

```python
MdBottomSheet(
    parent: QWidget,
    *,
    show_drag_handle: bool = True,
    is_dismissible: bool = True,
    max_height_ratio: float = 0.6,
)
```

- `add_content(widget)` — appends a widget to the panel's content layout.
- `open()` — covers the parent, then slides the panel up from the bottom edge.
- `dismiss()` — slides the panel out and hides; `closed` fires when the close finishes. A no-op if already hidden.
- `is_dismissible` — property; whether a scrim click dismisses (Flutter's `isDismissible`).
- `set_dismissible(value)` — setter for the above.
- `show_drag_handle` — read-only property; whether the drag handle was requested at construction.

**Signals:** `closed` (no payload) — emitted when the sheet finishes closing. (`MdBottomSheet` is a standalone overlay, not a `ModalOverlay` subclass — there is no `rejected` or `accepted` signal.)

### MdStandardBottomSheet

```python
MdStandardBottomSheet(parent: QWidget | None = None, *, expanded: bool = False)
```

- `add_content(widget)` — appends a widget to the content layout.
- `expanded` — property; whether the sheet is currently expanded.
- `expand()` / `collapse()` — convenience wrappers around `set_expanded`.
- `set_expanded(expanded, *, animated: bool = True)` — animates the fixed height between the peek height and the full content height.

**Signals:** `toggled(bool)` — emitted with the new expanded state on every `set_expanded` that changes state.

## Notes

- `MdBottomSheet` is the modal variant: a scrim (opacity 0.32) covers the host, a scrim click (when dismissible) or Escape dismisses, and the panel slides in over ~`MEDIUM2` duration with the emphasized easing curve. It implements its own scrim and slide rather than deriving from the `ModalOverlay` base used by [./dialog.md](./dialog.md), so it has no focus trap or `rejected` signal.
- Escape always dismisses when `is_dismissible` is true; scrim clicks are likewise gated by the same flag.
- `MdStandardBottomSheet` is the persistent (non-modal) variant: no scrim or overlay. Place it last in a `QVBoxLayout`; it toggles between a 28 px peek height (drag handle only) and its full content height, and clicking the handle strip (top 28 px) toggles it.
- The panel uses `surface-container-low`, level-1 elevation, and extra-large (28 px) rounded top corners; the drag handle is a 32×4 px rounded bar in `on-surface-variant` at 40% alpha.
- `max_height_ratio` caps the modal panel height as a fraction of the host (Flutter's `scrollControlDisabledMaxHeightRatio`).
- When `show_drag_handle=False`, the panel's reserved top space shrinks from 28 px to the normal 16 px padding.
- The modal sheet tracks parent resizes via an event filter and repositions while visible.
- For a resizable, scroll-coupled bottom sheet, see [./draggable-sheet.md](./draggable-sheet.md).
