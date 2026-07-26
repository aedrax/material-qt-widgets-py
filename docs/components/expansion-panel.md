# Expansion panel

Header that expands to reveal content.

**Classes:** `MdExpansionPanel` · **Source:** `src/material_qt/widgets/expansionpanel/`
**Spec:** https://api.flutter.dev/flutter/material/ExpansionTile-class.html. The module docstring names Flutter's `ExpansionTile` as the counterpart.

## Usage

```python
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from material_qt import MdDivider, MdExpansionPanel

app = QApplication([])
window = QWidget()
lay = QVBoxLayout(window)
for i, (title, body) in enumerate([
    ("Trip details", "Flight, hotel, and rental car reservations."),
    ("Travelers", "2 adults, 1 child."),
]):
    panel = MdExpansionPanel(title, initially_expanded=(i == 0))
    text = QLabel(body)
    text.setWordWrap(True)
    panel.add_content(text)
    panel.toggled.connect(lambda open_, t=title: print(t, "open" if open_ else "closed"))
    lay.addWidget(panel)
    lay.addWidget(MdDivider())
lay.addStretch(1)
window.resize(420, 320)
window.show()
app.exec()
```

## API

### MdExpansionPanel

```python
MdExpansionPanel(
    title: str = "",
    parent: QWidget | None = None,
    *,
    subtitle: str = "",
    leading: QWidget | None = None,
    trailing: QWidget | None = None,
    show_trailing_icon: bool = True,
    initially_expanded: bool = False,
    background_role: ColorRole = ColorRole.SURFACE,
    expanded: bool | None = None,
)
```

- `add_content(widget)` — appends a widget to the collapsible content area.
- `set_title(title)` / `set_subtitle(subtitle)` — updates the header text; an empty subtitle hides the subtitle row.
- `background_role` — property; the theme color role painted behind the header (Flutter's `backgroundColor`).
- `set_background_role(role)` — setter for the above.
- `expanded` — property; whether the panel is currently expanded.
- `toggle()` — flips the expanded state (also triggered by clicking the header).
- `set_expanded(expanded, *, animated: bool = True)` — expands or collapses, animating the content height unless `animated=False`.

**Signals:** `toggled(bool)` — emitted with the new expanded state on every state change (in place of Flutter's `onExpansionChanged`).

## Notes

- The `expanded` constructor keyword is a back-compat alias for `initially_expanded`; when both are given, `expanded` wins.
- The header is a ripple-enabled strip with a 56 px minimum height: optional leading widget, `title-medium` title over an optional `body-medium` subtitle, optional trailing widget, and a chevron (`expand_more` / `expand_less`) that flips with the state. `show_trailing_icon=False` hides the chevron.
- The content's expanded height is measured at expand time — after layout has given the panel a real width — so wrapped-text content is not clipped.
- Height animations use the `MEDIUM2` duration with the emphasized easing curve. A new toggle cancels any in-flight animation first, so the terminal state always matches the last request (a finishing expand cannot unclamp a panel that was just collapsed).
- Panels are independent: exclusive-accordion grouping (Flutter's `ExpansionPanelList` with `ExpansionPanelRadio`) is deferred.
- Header text colors track the theme (`on-surface` title, `on-surface-variant` subtitle); see [../theming.md](../theming.md). A [./divider.md](./divider.md) between panels reproduces the stacked-list look.
