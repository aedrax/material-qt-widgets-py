# Slider

Select a value from a range.

**Classes:** `MdSlider` · **Source:** `src/material_qt/widgets/slider/`
**Spec:** [m3.material.io/components/sliders](https://m3.material.io/components/sliders). Ports Material Web's `md-slider` (single-value).

## Usage

```python
from material_qt import MdSlider

continuous = MdSlider(parent, value=40)

# Discrete: snap to a step and show tick marks.
discrete = MdSlider(parent, value=60, step=10, ticks=True)

# Flutter-style divisions: 5 intervals -> 6 stops, with a value bubble.
divided = MdSlider(parent, value=40, divisions=5, labeled=True)

continuous.valueChanged.connect(lambda v: print("value:", v))
```

Run the demo: `python -m material_qt.widgets.slider.demo`.

## API

### MdSlider

```python
MdSlider(
    parent: QWidget | None = None,
    *,
    minimum: int = 0,
    maximum: int = 100,
    value: int = 0,
    step: int = 0,
    ticks: bool = False,
    labeled: bool = False,
    divisions: int = 0,
)
```

- `divisions` (property) — number of discrete intervals (`N` intervals → `N + 1` stops); `0` means continuous.
- `set_divisions(divisions)` — set the interval count and snap the current value; a value `> 0` shows tick marks and takes precedence over `step` when snapping (Flutter semantics).
- `setValue(value)` — overridden to snap to a division stop *before* delegating, so `valueChanged` emits exactly one, already-snapped value per change.
- Inherited from `QAbstractSlider`: `value()`, `minimum()`/`maximum()`/`setRange()`, `setSingleStep()`/`setPageStep()`, `sliderDown` state. These are the canonical value APIs — the widget adds no snake_case wrappers for them.

**Signals:**

- `valueChanged(int)` — inherited from `QAbstractSlider`; emitted on every value change (already snapped when `divisions` is set).
- `sliderPressed()` / `sliderReleased()` — inherited from `QAbstractSlider`; emitted around pointer drags (the widget drives them via `setSliderDown`).

The widget defines no signals of its own.

## Notes

- Base class: `QAbstractSlider`, horizontal orientation only (set in the constructor). Values are integers, as in Qt.
- `step` maps to Qt's `singleStep`/`pageStep` and snaps pointer drags; `ticks=True` only draws tick marks when `step > 0`. `divisions` (when `> 0`) always shows ticks and wins over `step` for snapping; keyboard and wheel then move by whole division stops so uneven spans (e.g. 100/3) still land exactly on a stop.
- `labeled=True` shows a value bubble above the handle while dragging and reserves 32 px of extra height for it (`sizeHint()` grows from 200×40 to 200×72).
- Metrics: 4 px track, 20 px handle, 40 px handle state layer; 20 px horizontal margin keeps the state layer from clipping at the track ends. Disabled state uses `on-surface` at 0.38 opacity (0.12 for the inactive track).
- Focus halo is keyboard-only (Tab/Backtab/Shortcut focus reasons), per the library convention shared with the ripple and focus ring; mouse focus paints no halo.
- Right-to-left layouts mirror the track, handle position, and Left/Right arrow keys.
- Two-handle range selection is a separate widget — see [Range slider](./range-slider.md).
