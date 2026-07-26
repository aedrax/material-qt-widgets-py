# Dialog

Modal surface for focused tasks and decisions.

**Classes:** `MdDialog` · **Source:** `src/material_qt/widgets/dialog/`
**Spec:** https://m3.material.io/components/dialogs. Ports Material Web's `dialog/` component.

## Usage

```python
from PySide6.QtWidgets import QApplication, QWidget
from material_qt import MdDialog

app = QApplication([])
window = QWidget()
window.resize(560, 420)

dlg = MdDialog(
    window,
    icon="delete",
    headline="Delete file?",
    supporting_text="This will permanently remove the file. "
    "This action cannot be undone.",
)
dlg.add_action("Cancel", accept=False)
dlg.add_action("Delete", accept=True)
dlg.accepted.connect(lambda: print("Deleted"))
dlg.rejected.connect(lambda: print("Cancelled"))

window.show()
dlg.open()
app.exec()
```

Run the demo: `python -m material_qt.widgets.dialog.demo`.

## API

### MdDialog

```python
MdDialog(
    parent: QWidget,
    *,
    headline: str = "",
    icon: str = "",
    supporting_text: str = "",
    barrier_dismissible: bool = True,
)
```

`MdDialog` subclasses the shared [`ModalOverlay`](../architecture.md#modal-overlay) base, which supplies the scrim, the fade in/out, Escape and scrim-click dismissal, a keyboard focus trap, and focus restoration on close.

Inherited from `ModalOverlay`:

- `open()` — covers the parent, centers the panel, and fades in.
- `dismiss()` — rejects and closes (emits `rejected`, then `closed`).

Added by `MdDialog`:

- `add_content(widget)` — appends a widget to the body area below the supporting text.
- `add_option(text)` — adds a full-width, left-aligned tappable option row (Flutter's `SimpleDialogOption`) and returns the `QPushButton`. Selecting an option does not auto-close; call `close_dialog()` (or emit `accepted`) from the handler if desired.
- `add_action(text, *, accept: bool | None = None)` — adds a text-button action and returns the `MdTextButton`. `accept=True` emits `accepted` and closes; `accept=False` dismisses (emits `rejected`); `None` just returns the button for custom handling.
- `close_dialog()` — closes without rejecting (public alias for the base close).
- `barrier_dismissible` — property; whether a scrim click or Escape dismisses (Flutter's `barrierDismissible`).
- `set_barrier_dismissible(value)` — setter for the above.

**Signals:**

- `accepted` (no payload) — declared by `MdDialog`; emitted by an `accept=True` action before closing.
- `rejected` (no payload) — inherited from `ModalOverlay`; emitted on scrim click, Escape, or an `accept=False` action.
- `closed` (no payload) — inherited from `ModalOverlay`; emitted whenever the dialog closes, accepted or not.

## Notes

- The panel is `surface-container-high` with corner-extra-large shape and level-3 elevation; the headline uses `headline-small` and the supporting text `body-medium`.
- The panel width clamps between 280 px and 560 px, further limited to the parent width minus 48 px.
- With `barrier_dismissible=False`, scrim clicks are swallowed and Escape is ignored — only actions or `close_dialog()` close it. Accept actions still work.
- While open, Tab and Shift+Tab are confined to the dialog's focusable descendants (the base's focus trap); on close, focus returns to the widget focused before `open()`.
- The overlay deliberately avoids `QGraphicsOpacityEffect` (the panel already carries a drop-shadow effect; nesting effects makes Qt spam "painter not active" errors) — the base drives a scrim-alpha fade plus a subtle panel slide instead.
- For sheets anchored to an edge rather than centered, see [./bottom-sheet.md](./bottom-sheet.md) and [./side-sheet.md](./side-sheet.md).
