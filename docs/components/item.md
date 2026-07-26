# Item

Content layout primitive with slots.

**Classes:** `MdItem` · **Source:** `src/material_qt/widgets/item/`
**Spec:** not in the M3 component catalogue — this ports Material Web's `labs/item`, a non-interactive layout building block that list items compose.

## Usage

```python
from material_qt import MdIcon, MdItem

simple = MdItem("One-line item")

detailed = MdItem(
    "Three-line item with trailing",
    supporting_text="Longer supporting text that may wrap across "
                    "multiple lines in the item body.",
    trailing_supporting_text="100+",
    leading=MdIcon("email"),
    trailing=MdIcon("chevron_right"),
)
```

Run the demo: `python -m material_qt.widgets.item.demo`.

## API

### MdItem

```python
MdItem(
    headline: str = "",
    parent: QWidget | None = None,
    *,
    supporting_text: str = "",
    trailing_supporting_text: str = "",
    leading: QWidget | None = None,
    trailing: QWidget | None = None,
)
```

- `set_headline(text)` — set the headline label.
- `set_supporting_text(text)` — set the supporting text; the label hides entirely when the text is empty.
- `set_trailing_supporting_text(text)` — set the small trailing text (e.g. a count or timestamp); hides when empty.
- `set_leading(widget)` — put a widget in the leading (start) slot; `None` empties and hides the slot.
- `set_trailing(widget)` — put a widget in the trailing (end) slot; `None` empties and hides the slot.

**Signals:** none. `MdItem` is deliberately non-interactive; wrap it (as [`MdListItem`](./list.md) does) to add ripple and click handling.

## Notes

- Five slots, laid out in one row: leading widget, then a text block of headline (`body-large`, `on-surface`) over supporting text (`body-medium`, `on-surface-variant`), then trailing supporting text (`label-small`, `on-surface-variant`), then the trailing widget. The text block takes all remaining width.
- Metrics: 16 px horizontal padding, 8 px vertical padding, 16 px gap between slots, 2 px gap between headline and supporting text. Headline and supporting text word-wrap.
- Text colors track the theme: each label re-applies its role color on every `themeChanged`, so items restyle live on a light/dark switch (see [../theming.md](../theming.md)).
- Ownership gotcha: replacing a slot widget via `set_leading`/`set_trailing` detaches **and deletes** the previous widget (`deleteLater`). Passing the widget already in the slot is safe (it is not deleted), but do not hold on to a replaced widget expecting to reuse it.
- The leading/trailing holders are hidden while empty so an item without those slots has no phantom spacing.
- `MdListItem` in [List](./list.md) exposes its inner `MdItem` via its `item` property; anything documented here can be driven through that.
