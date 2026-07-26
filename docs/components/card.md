# Card

Container for related content and actions.

**Classes:** `MdCard`, `CardVariant` · **Source:** `src/material_qt/widgets/card/`
**Spec:** https://m3.material.io/components/cards. Ports Material Web's `labs/card` component.

## Usage

```python
from PySide6.QtWidgets import QApplication, QLabel
from material_qt import CardVariant, MdCard

app = QApplication([])
card = MdCard(variant=CardVariant.OUTLINED)
card.add_widget(QLabel("Headline"))
card.add_widget(QLabel("Supporting line of card content."))
card.resize(240, 140)
card.show()
app.exec()
```

Run the demo: `python -m material_qt.widgets.card.demo`.

## API

### MdCard

```python
MdCard(
    parent: QWidget | None = None,
    *,
    variant: CardVariant = CardVariant.ELEVATED,
)
```

- `variant` — read-only property returning the `CardVariant` chosen at construction (there is no setter; pick the variant up front).
- `content_layout()` — returns the card's internal `QVBoxLayout` for direct layout access.
- `add_widget(widget)` — appends a child widget to the content layout.

**Signals:** none.

### CardVariant

An `Enum` with three members:

- `CardVariant.ELEVATED` (`"elevated"`)
- `CardVariant.FILLED` (`"filled"`)
- `CardVariant.OUTLINED` (`"outlined"`)

## Notes

- Variant styling follows the Material Web mapping: elevated uses `surface-container-low` with level-1 elevation; filled uses `surface-container-highest` with no elevation; outlined uses `surface` with a 1 px `outline-variant` border.
- The shape is corner-medium (12 px), applied via the shared material surface machinery.
- The content layout has 16 px margins on all sides and 8 px spacing between children.
- The card is a plain container: ripple and focus ring are disabled, and it does not handle clicks itself. Put interactive widgets inside it instead.
- The outline (for `OUTLINED`) is repainted from the current theme on every paint, so theme switches recolor it automatically. See [../theming.md](../theming.md).
