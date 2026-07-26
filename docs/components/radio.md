# Radio button

Select one option from a set.

**Classes:** `MdRadio` · **Source:** `src/material_qt/widgets/radio/`
**Spec:** [m3.material.io/components/radio-button](https://m3.material.io/components/radio-button). Ports Material Web's `md-radio`.

## Usage

```python
from PySide6.QtWidgets import QButtonGroup
from material_qt import MdRadio

# Radios sharing a direct parent are exclusive automatically (autoExclusive).
# When each radio sits in its own row/container widget, group them explicitly:
group = QButtonGroup(parent)
for i, name in enumerate(("Apple", "Banana", "Cherry")):
    radio = MdRadio(parent, checked=(i == 0), label=name)
    group.addButton(radio)
    layout.addWidget(radio)

group.buttonToggled.connect(lambda btn, on: on and print(btn.label))
```

Run the demo: `python -m material_qt.widgets.radio.demo`.

## API

### MdRadio

```python
MdRadio(
    parent: QWidget | None = None,
    *,
    checked: bool = False,
    toggleable: bool = False,
    label: str | None = None,
)
```

- `toggleable` (property) / `set_toggleable(value)` — when true, clicking (or Space-activating) the already-selected radio deselects it (Material `toggleable`). Exclusivity is temporarily lifted so Qt's own click machinery performs the deselect and still emits `clicked`/`toggled`.
- `label` (property) / `set_label(label)` — accessible name (Material `semanticLabel`); maps to `accessibleName`, no visible text is drawn.
- `click()` — overridden so a programmatic click honors `toggleable` deselection; otherwise identical to `QAbstractButton.click()`.
- Inherited from `QAbstractButton`: `setChecked(bool)` / `isChecked()` for the selected state (no snake_case wrapper exists; use the Qt API).

**Signals:**

- `toggled(bool)` — inherited from `QAbstractButton`; emitted on any selected-state change.
- `clicked(bool)` — inherited from `QAbstractButton`; emitted on user activation.

The widget defines no signals of its own.

## Notes

- Base class: `QAbstractButton` with `setCheckable(True)` and `setAutoExclusive(True)`; the `MaterialWidgetMixin` foundation supplies the ripple state layer and focus ring.
- Exclusivity mirrors the web single-selection controller: radios that share a parent widget are mutually exclusive via `autoExclusive`. If radios are wrapped in per-row containers (different parents), add them to a `QButtonGroup` — the package demo does exactly this.
- Metrics: a 20 px circle (2 px ring) inside a 40 px circular state-layer target; the inner dot is 10 px; `sizeHint()` is 40×40. Disabled state uses `on-surface` at 0.38 opacity.
- The inner dot scale-in animates over 150 ms (`Duration.SHORT3`, standard easing) and snaps without animation when the widget is not visible or motion is disabled.
- The ripple color tracks selection: `primary` while selected, `on-surface` otherwise.
- Space-key deselection for `toggleable` is routed through `keyReleaseEvent` because Qt's C++ click path bypasses the Python `click()` override.
- See also [Checkbox](./checkbox.md) and [Switch](./switch.md).
