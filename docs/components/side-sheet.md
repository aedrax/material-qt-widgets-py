# Side sheet

Side panel for supporting content.

**Classes:** `MdSideSheet`, `MdStandardSideSheet` · **Source:** `src/material_qt/widgets/sidesheet/`
**Spec:** https://m3.material.io/components/side-sheets. The module docstring names no external upstream; it mirrors this library's own `MdBottomSheet` (scrim + slide) but slides horizontally.

## Usage

```python
from PySide6.QtWidgets import QApplication, QLabel, QWidget
from material_qt import MdSideSheet

app = QApplication([])
window = QWidget()
window.resize(640, 480)

sheet = MdSideSheet(window, title="Filters")
for text in ["Category", "Price range", "Rating", "Availability"]:
    sheet.add_content(QLabel(text))
sheet.add_action("Reset")
apply_btn = sheet.add_action("Apply")
apply_btn.clicked.connect(sheet.dismiss)
sheet.closed.connect(lambda: print("closed"))

window.show()
sheet.open()
app.exec()
```

## API

### MdSideSheet

```python
MdSideSheet(parent: QWidget, *, title: str = "", side: str = "right")
```

- `add_content(widget)` — appends a widget to the scrollable content area below the header.
- `add_action(text)` — appends a trailing action button (an `MdTextButton`, returned) and shows a divider above the action row.
- `open()` — covers the parent, then slides the panel in from the chosen edge.
- `dismiss()` — slides the panel out and hides; `closed` fires when the close finishes. A no-op if already hidden.

**Signals:** `closed` (no payload) — emitted when the sheet finishes closing. (Like `MdBottomSheet`, this is a standalone overlay, not a `ModalOverlay` subclass — no `rejected` or `accepted`.)

### MdStandardSideSheet

```python
MdStandardSideSheet(
    parent: QWidget | None = None,
    *,
    title: str = "",
    side: str = "right",
    expanded: bool = True,
)
```

- `add_content(widget)` — appends a widget to the content area.
- `add_action(text)` — appends a trailing `MdTextButton` (returned) and shows the divider above the action row.
- `expanded` — property; whether the sheet is currently expanded.
- `expand()` / `collapse()` — convenience wrappers around `set_expanded`. The built-in close icon button calls `collapse()`.
- `set_expanded(expanded, *, animated: bool = True)` — animates the fixed width between 0 and 320 px.

**Signals:** `toggled(bool)` — emitted with the new expanded state on every `set_expanded` that changes state.

## Notes

- `MdSideSheet` is the modal variant: a full-height panel that slides in over a scrim (opacity 0.32). It dismisses on a scrim click, the header's close button, or Escape — there is no dismissibility flag; the modal side sheet is always dismissible.
- `side` accepts `"right"` (default) or `"left"`; any other value falls back to `"right"`. Only the leading (inner) corners are rounded at 28 px; the outer edge is flush.
- The panel is a fixed 320 px wide (clamped to the host width), `surface-container-low`, level-1 elevation; the header shows the title in `title-large` plus a close `MdIconButton`.
- `MdStandardSideSheet` is the persistent (non-modal) variant: no scrim or overlay. Place it in a `QHBoxLayout`; it toggles by animating its width between 0 and 320 px, so neighbouring content reflows.
- Slide animations use the `MEDIUM2` duration with the emphasized easing curve, matching [./bottom-sheet.md](./bottom-sheet.md).
- The modal sheet tracks parent resizes via an event filter and repositions while visible.
