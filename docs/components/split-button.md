# Split button

Primary action plus a dropdown.

**Classes:** `MdSplitButton`, `SplitButtonColor` · **Source:** `src/material_qt/widgets/splitbutton/`
**Spec:** <https://m3.material.io/components/split-button>. Ports the experimental `labs/gb` split button from Material Web: a connected pair of a leading action button and a smaller trailing button that typically opens a menu.

## Usage

```python
from material_qt import MdSplitButton, SplitButtonColor, MdMenu, MdMenuItem

sb = MdSplitButton("Save", page, color=SplitButtonColor.FILLED, icon="save")
sb.clicked.connect(on_save)

menu = MdMenu(sb)
for label in ("Save as draft", "Save and close", "Save a copy"):
    menu.add_item(MdMenuItem(label))
menu.selected.connect(on_save_variant)
sb.set_menu(menu)
```

Run the demo: `python -m material_qt.widgets.splitbutton.demo`.

## API

### MdSplitButton

A plain `QWidget` composing two internal button segments: the leading label/icon half and the trailing arrow half. The halves share the container color, have corner-full outer ends, and are separated by a 1px divider gap; each has its own ripple and focus ring.

```python
MdSplitButton(
    text: str = "",
    parent: QWidget | None = None,
    *,
    color: SplitButtonColor = SplitButtonColor.FILLED,
    icon: str = "",
    trailing_icon: str = "arrow_drop_down",
)
```

- `icon` and `trailing_icon` are Material Symbols ligature names (e.g. `"save"`), never `QIcon`s.
- `set_menu(menu)` — attach an `MdMenu` that the trailing button opens (via `menu.open_at(trailing)`). Without a menu, the trailing button still emits `trailingClicked`.
- `set_text(text)` / `text()` — the leading label. Because `MdSplitButton` is a composite `QWidget` (not a `QAbstractButton`), use these snake_case methods; there is no inherited `setText`.
- `setEnabled(enabled)` — overridden to forward to both halves; always disable through the composite, not by reaching into it. (There is no snake_case `set_enabled`.)

**Signals:**

- `clicked = Signal()` — the leading (primary action) button was activated. Note: no `bool` payload, unlike `QAbstractButton.clicked`.
- `trailingClicked = Signal()` — the trailing (dropdown) button was activated; emitted before the attached menu opens.

### SplitButtonColor

Color variants mirroring the common button family: `FILLED` (primary container, the default), `ELEVATED` (surface-container-low, rests at elevation 1), `TONAL` (secondary container), `OUTLINED` (transparent with a 1px `outline` border).

## Notes

- Metrics: each half is 40px tall with radius-20 outer corners; the trailing half is a fixed 40px wide with a 24px dropdown glyph; the leading half sizes to its text with 24px padding (16px on the icon side), 18px icon, 8px icon–label gap, `label-large` text.
- The widget insets its layout by a computed shadow margin so the halves' drop shadow (largest at hover elevation) is not clipped, and fixes its own height to 40px plus twice that margin — so the composite is taller than a plain `MdButton`; align by center in rows.
- The 1px spacing between halves shows the surface behind as the divider; place the widget on a plain surface background.
- Filled/tonal lift to elevation 1 on hover, elevated rests at 1 and lifts to 2, outlined never lifts; disabled halves repaint with on-surface at 12% (container/outline) / 38% (label) opacity and drop to elevation 0.
- There is no `longPressed` signal on the split button, unlike the [common buttons](./button.md).
- See also [buttons](./button.md) for the standalone variants and [theming](../theming.md) for color roles.
