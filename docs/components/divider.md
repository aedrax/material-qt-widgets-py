# Divider

Thin line that groups content.

**Classes:** `MdDivider` · **Source:** `src/material_qt/widgets/divider/`
**Spec:** https://m3.material.io/components/divider. Ports Material Web's `md-divider` (source of truth: `divider/internal/_divider.scss` and the divider tokens).

## Usage

```python
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from material_qt import MdDivider

app = QApplication([])
window = QWidget()
lay = QVBoxLayout(window)
lay.addWidget(QLabel("Item one"))
lay.addWidget(MdDivider())
lay.addWidget(QLabel("Item two"))
inset = MdDivider()
inset.inset = True  # 16 px padding on both sides
lay.addWidget(inset)
lay.addWidget(QLabel("Item three"))
window.show()
app.exec()
```

Run the demo: `python -m material_qt.widgets.divider.demo`.

## API

### MdDivider

```python
MdDivider(
    parent: QWidget | None = None,
    *,
    orientation: Qt.Orientation = Qt.Orientation.Horizontal,
    thickness: int = THICKNESS_PX,
    indent: int = 0,
    end_indent: int = 0,
    color_role: ColorRole = ColorRole.OUTLINE_VARIANT,
)
```

- `orientation()` — returns the current `Qt.Orientation`.
- `set_orientation(orientation)` — switches between horizontal and vertical, releasing the old fixed extent and re-applying the size policy.
- `thickness` — read/write property; line thickness in pixels (the divider's fixed cross-axis size). Negative values clamp to 0.
- `color_role` — read/write property; the theme color role used to paint the line. `set_color_role(role)` is an equivalent setter method.
- `indent` — read/write property; leading-edge inset in pixels (Flutter `indent`).
- `end_indent` — read/write property; trailing-edge inset in pixels (Flutter `endIndent`).
- `inset` — read/write bool property; indents the divider with equal padding on both sides.
- `inset_start` — read/write bool property; indents the divider with padding on the leading side.
- `inset_end` — read/write bool property; indents the divider with padding on the trailing side.

**Signals:** none.

Module constants: `THICKNESS_PX = 1` and `INSET_PX = 16`, matching the web tokens `--md-divider-thickness: 1px` and the 16 px inset padding.

## Notes

- The default is a full-width 1 px line in the `outline-variant` color, matching the web `--md-divider-color` default. The color is resolved from the theme at paint time, so theme switches repaint correctly.
- Boolean insets (`inset`, `inset_start`, `inset_end`) each contribute a fixed 16 px; the numeric `indent` / `end_indent` values stack on top of them.
- The web component primarily lays out horizontally; this port also supports `Qt.Orientation.Vertical`, where the line runs top-to-bottom and insets apply to the top (leading) and bottom (trailing) edges.
- For horizontal dividers, leading and trailing respect the widget's layout direction: in right-to-left layouts the leading inset applies to the right edge.
- The widget is decorative: it takes no focus (`NoFocus`) and is transparent to mouse events.
- Horizontal dividers use an `Expanding`/`Fixed` size policy (fixed height = thickness); vertical dividers the reverse. Give a vertical divider a bounded height in unbounded layouts (the demo uses `setFixedHeight(48)`).
