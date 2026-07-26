# Navigation tab

A single navigation destination.

**Classes:** `MdNavigationTab` · **Source:** `src/material_qt/widgets/navigationtab/`
**Spec:** https://m3.material.io/components/navigation-bar (a navigation bar destination) — ports Material Web's `labs/navigationtab`.

## Usage

Normally you get tabs from `MdNavigationBar.add_destination`, but they can be used standalone with your own `QButtonGroup`.

```python
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QWidget
from material_qt import MdNavigationTab

holder = QWidget()
bar = QHBoxLayout(holder)
bar.setSpacing(0)
group = QButtonGroup(holder)
for i, (label, icon) in enumerate(
    [("Home", "home"), ("Search", "search"), ("Saved", "bookmark")]
):
    tab = MdNavigationTab(label, icon=icon)
    if i == 0:
        tab.setChecked(True)
    group.addButton(tab)
    bar.addWidget(tab)

tab.set_badge("3")           # count pill; "" for a dot, None to hide
tab.set_label_behavior("selected")
```

Run the demo: `python -m material_qt.widgets.navigationtab.demo`.

## API

### MdNavigationTab

```python
MdNavigationTab(label="", parent=None, *, icon="", active_icon="")
```

- `set_label_behavior(behavior)` — `"always"` / `"selected"` / `"hide"`; when no label shows, the icon centres vertically in the 64 px tab.
- `set_badge(value)` — `""` shows a dot, a string shows a count pill, `None` hides the badge.
- Inherited `QAbstractButton` API applies: `setChecked`/`isChecked` for selection, `text()`/`setText()` for the label.

**Signals:**

- No signals of its own; use the inherited `QAbstractButton` signals — `toggled(bool)` and `clicked` — for selection changes. `MdNavigationBar` wraps these into its `changed(int)`.

## Notes

- Built on a checkable `QAbstractButton`. It is the destination widget used by [navigation-bar](./navigation-bar.md); selection exclusivity is your responsibility when used standalone (use a `QButtonGroup`).
- Metrics from source constants: tab height 64, icon 24 px, pill active indicator 64x32 (fully rounded), 4 px gap to the `label-medium` label, badge height 16.
- Active state fills the indicator with `secondary-container`; the icon uses `on-secondary-container` and is drawn with the filled Material Symbols axis; the label uses `on-surface`. Inactive icon and label use `on-surface-variant`.
- `active_icon` substitutes a different ligature glyph while checked; it defaults to `icon` when empty.
- Badge colors: dot and pill use the `error` role; pill text uses `on-error` at `label-small`.
- Icons are Material Symbols ligature-name strings (e.g. `"home"`), never `QIcon`.
- The ripple is clipped to the pill indicator shape.
- See [../theming.md](../theming.md) for color roles.
