# Dismissible

Swipe a row aside to dismiss it.

**Classes:** `MdDismissible`, `DismissDirection` · **Source:** `src/material_qt/widgets/dismissible/`
**Spec:** Flutter API — [`Dismissible`](https://api.flutter.dev/flutter/widgets/Dismissible-class.html). Ports Flutter's `widgets/dismissible.dart`: wrap a content widget, and a drag past a threshold flings it off-screen, collapses its extent to zero (reflowing the host layout), then notifies you.

## Usage

```python
from material_qt import DismissDirection, MdDismissible, MdIcon, MdListItem

item = MdListItem("Swipe to delete", leading=MdIcon("mail"), interactive=False)
row = MdDismissible(
    item,
    direction=DismissDirection.HORIZONTAL,
    background=archive_panel,            # shown behind a start-to-end swipe
    secondary_background=delete_panel,   # shown behind an end-to-start swipe
)
row.dismissed.connect(lambda direction: print("dismissed:", direction))
layout.addWidget(row)
```

Run the demo: `python -m material_qt.widgets.dismissible.demo`.

## API

### MdDismissible

```python
MdDismissible(
    content: QWidget,
    parent: QWidget | None = None,
    *,
    direction: DismissDirection = DismissDirection.HORIZONTAL,
    background: QWidget | None = None,
    secondary_background: QWidget | None = None,
    threshold: float = 0.4,
    confirm: Callable[[DismissDirection], bool] | None = None,
)
```

- `content` (property) — the wrapped content widget.
- `direction` (property) — the allowed swipe direction(s).
- `dismiss(direction=None)` — programmatically dismiss, running the same fling/collapse animation before emitting `dismissed`. With `direction=None` it defaults to `END_TO_START` for `HORIZONTAL`, `UP` for `VERTICAL`, and the configured direction otherwise. Ignored if a dismissal is already in flight.
- `offset` and `collapse` (Qt `Property(float)`, via `get_offset`/`set_offset` and `get_collapse`/`set_collapse`) — the animatable drag offset and 1→0 cross-axis collapse fraction; normally driven by the widget itself.

**Signals:**

- `dismissed = Signal(object)` — carries the resolved `DismissDirection`. Fired exactly once, after the fling and collapse animations finish and the widget has hidden itself.

### DismissDirection

Mirrors Flutter's `DismissDirection`:

- `HORIZONTAL` — either left or right.
- `VERTICAL` — either up or down.
- `START_TO_END` — drag right (LTR).
- `END_TO_START` — drag left (LTR).
- `UP`
- `DOWN`

The drop decision is the pure helper `resolve_dismiss(direction, dx, dy, extent_x, extent_y, threshold)` — it returns the concrete `START_TO_END`/`END_TO_START`/`UP`/`DOWN` when the drag reaches `threshold` (a fraction of the widget extent) in an allowed sign, else `None` (spring back). Importable from `material_qt` directly.

## Notes

- **The widget owns its lifecycle.** `dismissed` is a pure notification: by the time it fires the widget has already hidden itself, and you remove the item from your model at leisure. There is no Flutter "a dismissed Dismissible is still in the tree / you must remove it" footgun, and no required `key`.
- `background` shows while the content is dragged toward the end (`offset > 0`); `secondary_background` shows while dragged toward the start (`offset < 0`). Both are reparented into the dismissible and sized to fill it behind the content.
- `confirm` is a **synchronous** callback: it receives the resolved direction and returns `bool`. Returning `False` springs the content back. A modal `dialog.exec()` composes naturally; Flutter's async `confirmDismiss` has no direct equivalent.
- A press only becomes a swipe after 8 px of movement along the allowed axis, so buttons and ripples inside the content still receive plain clicks. Once claimed, the child under the finger gets a synthetic far-away release so it does not stay stuck pressed (mirroring Flutter's gesture cancel).
- Directional clamping: with `START_TO_END`, `END_TO_START`, `UP`, or `DOWN`, drags in the disallowed sign are clamped to zero; `HORIZONTAL`/`VERTICAL` allow both signs.
- A release short of `threshold` (default 0.4 of the width/height) animates the content back into place. Past it, the content flings off-screen, then the perpendicular extent collapses to zero (reflowing the host layout), then `dismissed` fires.
- Limitation: the drag is an event-filter layer installed over the content subtree at construction — children added to the content *after* construction are not covered by it.
- Deferred (vs Flutter): async `confirmDismiss`, per-direction thresholds (a single `threshold` here), and `crossAxisEndOffset`.
- Typical content is a non-interactive list row — see [List](./list.md).
