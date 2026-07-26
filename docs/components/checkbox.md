# Checkbox

Select one or more items from a set.

**Classes:** `MdCheckbox` · **Source:** `src/material_qt/widgets/checkbox/`
**Spec:** [m3.material.io/components/checkbox](https://m3.material.io/components/checkbox). Ports Material Web's `md-checkbox`.

## Usage

```python
from material_qt import MdCheckbox

unchecked = MdCheckbox(parent)
checked = MdCheckbox(parent, checked=True)

mixed = MdCheckbox(parent)
mixed.set_indeterminate(True)

invalid = MdCheckbox(parent, checked=True, error=True)

checked.toggled.connect(lambda on: print("checked:", on))
```

Run the demo: `python -m material_qt.widgets.checkbox.demo`.

## API

### MdCheckbox

```python
MdCheckbox(
    parent: QWidget | None = None,
    *,
    checked: bool = False,
    indeterminate: bool = False,
    error: bool = False,
    label: str | None = None,
)
```

- `indeterminate` (property) — whether the dash (mixed) marker is shown.
- `set_indeterminate(value)` — show or clear the indeterminate dash.
- `error` (property) — whether the error variant is active.
- `set_error(value)` — switch between the error palette (`error`/`on-error`) and the normal one.
- `label` (property) / `set_label(label)` — accessible name (Material `semanticLabel`); maps to Qt's `accessibleName`, no visible text is drawn.
- Inherited from `QAbstractButton`: use `setChecked(bool)` / `isChecked()` / `toggle()` for the checked state — there is no snake_case wrapper for it, the Qt API is the canonical one here. Space activates the checkbox.

**Signals:**

- `toggled(bool)` — inherited from `QAbstractButton`; emitted on any checked-state change.
- `clicked(bool)` — inherited from `QAbstractButton`; emitted on user activation.

The widget defines no signals of its own.

## Notes

- Base class: `QAbstractButton` (checkable), with the shared `MaterialWidgetMixin` foundation supplying the ripple state layer and focus ring.
- Tri-state is modeled as a separate `indeterminate` flag, not Qt's `tristate`/`checkState` API. Any toggle resolves the mixed state: unchecking a checked-and-indeterminate box also drops the dash (`_on_toggled` clears `indeterminate`).
- Metrics: an 18 px box (2 px corner radius, 2 px outline) centered in a 40 px circular state-layer target; `sizeHint()` is 40×40. Disabled state uses `on-surface` at 0.38 opacity.
- The checkmark/dash draws in over 150 ms (`Duration.SHORT3`, standard easing); the animation is skipped (state snaps) when the widget is not visible or motion is disabled.
- The ripple color tracks state: `primary` when marked, `on-surface` when not, `error` when the error variant is set.
- See also [Radio](./radio.md) and [Switch](./switch.md); theming is covered in [../theming.md](../theming.md).
