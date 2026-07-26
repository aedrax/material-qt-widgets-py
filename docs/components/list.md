# List

Vertical index of text and images.

**Classes:** `MdList`, `MdListItem` · **Source:** `src/material_qt/widgets/list/`
**Spec:** [m3.material.io/components/lists](https://m3.material.io/components/lists). Ports Material Web's `list/` — `MdList` is a surface container holding `MdListItem` rows.

## Usage

```python
from material_qt import MdIcon, MdList, MdListItem

lst = MdList(parent)
inbox = MdListItem("Inbox", supporting_text="3 new messages",
                   leading=MdIcon("inbox"), trailing_supporting_text="3")
lst.add_item(inbox)
lst.add_item(MdListItem("Starred", leading=MdIcon("star"),
                        trailing=MdIcon("chevron_right")), divider=True)
lst.add_item(MdListItem("Sent", leading=MdIcon("send")), divider=True)

inbox.clicked.connect(lambda: print("open inbox"))
```

Run the demo: `python -m material_qt.widgets.list.demo`.

## API

### MdList

```python
MdList(parent: QWidget | None = None)
```

- `add_item(item, *, divider=False)` — append an `MdListItem`; with `divider=True` an `MdDivider` is inserted before it (skipped when the list is still empty, so dividers only ever sit between items).
- `items` (property) — a copy of the list of added `MdListItem` widgets.

**Signals:** none. `MdList` is a passive surface container.

### MdListItem

```python
MdListItem(
    headline: str = "",
    parent: QWidget | None = None,
    *,
    supporting_text: str = "",
    trailing_supporting_text: str = "",
    leading: QWidget | None = None,
    trailing: QWidget | None = None,
    interactive: bool = True,
    selected: bool = False,
    enabled: bool = True,
)
```

- `item` (property) — the inner [`MdItem`](./item.md) layout primitive; use it to change headline, supporting text, or the leading/trailing slots after construction.
- `selected` (property) / `set_selected(value)` — whether the row paints its selected (tonal `secondary-container`) state.
- `enabled` (property) / `set_enabled(value)` — wraps Qt's `setEnabled`/`isEnabled`.
- `content_padding()` — the inner item's content margins as `(left, top, right, bottom)`.
- `set_content_padding(left, top, right, bottom)` — set the inner item's content margins (Flutter `contentPadding`).

**Signals:**

- `clicked = Signal()` — emitted on a left-button release inside the row, or on Return/Enter/Space, when the item is interactive and enabled.

## Notes

- `MdListItem` composes an `MdItem` for layout and adds interaction on top: ripple, focus ring, pointing-hand cursor, and the `clicked` signal. It enforces a 56 px minimum height.
- `interactive=False` builds a non-interactive row: no ripple, no focus ring, no cursor change, and `clicked` never fires. This is the form used inside [Reorderable list](./reorderable-list.md) and [Dismissible](./dismissible.md) rows.
- The selected state fills the row's clip path with `secondary-container`; unselected rows paint the normal `surface` material (with hover/pressed state layers from the shared mixin).
- `MdList` lays items out vertically with no spacing and 8 px top/bottom padding, painting a plain `surface` background. It applies no selection policy of its own — toggle `selected` on items yourself.
- Ownership: `add_item` reparents the item into the list's layout; `items` returns a copy, so mutating the returned list does not affect the widget.
- Theming for text and surface colors is covered in [../theming.md](../theming.md).
