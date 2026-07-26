# Range slider

Select a range between two values.

**Classes:** `MdRangeSlider` · **Source:** `src/material_qt/widgets/rangeslider/`
**Spec:** [m3.material.io/components/sliders](https://m3.material.io/components/sliders) (range slider variant). The module docstring names Flutter's [`RangeSlider`](https://api.flutter.dev/flutter/material/RangeSlider-class.html) as the upstream counterpart.

## Usage

```python
from material_qt import MdRangeSlider

basic = MdRangeSlider(parent, low=25, high=75)

# Discrete: pointer drags snap to multiples of step.
discrete = MdRangeSlider(parent, low=20, high=60, step=10)

# Value bubble over the dragged handle.
labeled = MdRangeSlider(parent, low=30, high=70, labeled=True)

basic.valuesChanged.connect(lambda low, high: print("range:", low, high))
```

## API

### MdRangeSlider

```python
MdRangeSlider(
    parent: QWidget | None = None,
    *,
    minimum: int = 0,
    maximum: int = 100,
    low: int = 0,
    high: int = 100,
    step: int = 0,
    labeled: bool = False,
    divisions: int = 0,
)
```

- `values()` — the current `(low, high)` tuple.
- `low` (read-only property) — the lower handle's value.
- `high` (read-only property) — the upper handle's value.
- `set_values(low, high)` — set both values; each is clamped, snapped (when `divisions` is set), and swapped into order if `low > high`. Emits `valuesChanged` only when something actually changed.
- `divisions` (property) — number of discrete intervals (`N` intervals → `N + 1` stops); `0` means continuous.
- `set_divisions(divisions)` — set the interval count and snap both handles; a value `> 0` shows tick marks and takes precedence over `step` when snapping (Flutter semantics).

**Signals:**

- `valuesChanged = Signal(int, int)` — defined on the widget; emitted as `valuesChanged(low, high)` whenever either value changes.

Because this widget is not a `QAbstractSlider`, there is no inherited `valueChanged` — connect to `valuesChanged` instead.

## Notes

- Base class: standalone `QWidget` (via `MaterialWidgetMixin`), **not** `QAbstractSlider`, which models a single value. The two-value state lives entirely in this class.
- The handles cannot cross: the dragged (or keyboard-stepped) handle stops at the other handle's value.
- Pointer presses grab the nearest handle; on a tie (coincident handles) the one that can move toward the press wins, so a range collapsed at either bound never gets stuck. Hover highlights only the handle nearest the cursor.
- Keyboard: arrows/PageUp/PageDown/Home/End move the *focused* handle — the one last pressed or dragged, `low` until a handle is touched. One step is a division interval when `divisions` is set, else `step`, else 1; Left/Right mirror under right-to-left. There is no wheel handling (unlike [`MdSlider`](./slider.md)).
- Tick marks are drawn only when `divisions > 0` — there is no `ticks` constructor argument here; `step` alone snaps without drawing ticks.
- `labeled=True` shows a value bubble over the handle being dragged and reserves 32 px of extra height (`sizeHint()` grows from 200×40 to 200×72).
- Metrics match `MdSlider`: 4 px track, 20 px handles, 40 px handle state layers, 20 px horizontal margin; disabled state uses `on-surface` at 0.38 opacity (0.12 for the inactive track).
- No `demo.py` ships in this package; the gallery (`material_qt.gallery`) has a "Range slider" page built from the same examples as the Usage snippet above.
