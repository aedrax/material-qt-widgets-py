# Sliders — Flutter ↔ material_qt parity

Status legend: ✅ verified · ➕ added this pass · 🆕 built this pass · ⛔ N/A (rationale)

Both single-value and range sliders already existed in the port; this pass
verified their properties and added Flutter's `divisions` (count-of-intervals)
semantics with discrete tick marks to both, plus a pure snap seam under test.

## Slider (slider.dart) → MdSlider (widgets/slider) — covered ✅

`MdSlider` is a custom-painted `QAbstractSlider`, so `minimum`/`maximum`/
`value`/`valueChanged`/`sliderPressed`/`sliderReleased` and keyboard stepping
come from Qt natively.

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `value` / `onChanged` | `value()` / `setValue()` + `valueChanged` Signal (from `QAbstractSlider`) | ✅ |
| `onChangeStart` | `sliderPressed` Signal (native `QAbstractSlider`, fires on press) | ✅ |
| `onChangeEnd` | `sliderReleased` Signal (native `QAbstractSlider`, fires on release) | ✅ |
| `min` | `minimum()` / `setMinimum()` + `minimum=` kwarg | ✅ |
| `max` | `maximum()` / `setMaximum()` + `maximum=` kwarg | ✅ |
| `divisions` (N intervals → N+1 stops) | `divisions` @property / `set_divisions(n)` / `divisions=` kwarg; snaps via pure `_snap()`, drives ticks | ➕ |
| `label` (value indicator text) | value-label bubble painted while dragging when `labeled=True` (shows `str(value)`) | ✅ |
| `showValueIndicator` | `labeled=` kwarg gates the bubble | ✅ |
| `activeColor` | theme role `PRIMARY` (active track + handle) | ✅ |
| `inactiveColor` | theme role `SURFACE_CONTAINER_HIGHEST` (inactive track) | ✅ |
| `thumbColor` | theme role `PRIMARY` | ✅ |
| `overlayColor` | theme `PRIMARY` at `StateLayer` opacity (hover/focus/press) | ✅ |
| `secondaryTrackValue` / `secondaryActiveColor` | — | ⛔ Buffer/secondary track is not part of the M3 Web `md-slider` this port follows; out of scope. |
| `mouseCursor` / `focusNode` / `autofocus` / `allowedInteraction` | — | ⛔ Qt focus/cursor handled by the widget framework; not a 1:1 prop. |

Notes:
- `divisions` takes precedence over the port's pre-existing `step`/`ticks`
  kwargs for snapping and tick display when set (both kept additively so the
  gallery/demo keep working). Stops are computed in float space then rounded to
  int (Python round-half-to-even), so uneven spans (e.g. 3 divisions over
  0..100 → 0/33/67/100) round correctly without relying on a lossy integer
  `singleStep`.
- Snapping is applied on every input path: constructor, `set_divisions`,
  mouse drag (`_value_from_x`), and keyboard/wheel/page input (re-snapped in
  `sliderChange`). With divisions set, `singleStep`/`pageStep` are sized to one
  interval so arrow keys advance one stop at a time.

- [x] all properties verified or added

## RangeSlider (range_slider.dart) → MdRangeSlider (widgets/rangeslider) — covered ✅

`MdRangeSlider` is a custom-painted `QWidget` (not a `QAbstractSlider`, which
models a single value). It exposes `low`/`high` and emits `valuesChanged`.

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `values` / `onChanged` | `values()` / `set_values(low, high)`, `low`/`high` @property + `valuesChanged(low, high)` Signal | ✅ |
| `onChangeStart` / `onChangeEnd` | — | ⛔ No dedicated drag-start/end Signals; `valuesChanged` covers the change. Could add `slider_pressed`/`slider_released` Signals later — see Coordinator follow-up. |
| `min` | `minimum=` kwarg (`self._min`) | ✅ |
| `max` | `maximum=` kwarg (`self._max`) | ✅ |
| `divisions` (N intervals → N+1 stops) | `divisions` @property / `set_divisions(n)` / `divisions=` kwarg; snaps both handles via pure `_snap()`, draws ticks | ➕ |
| `labels` (RangeLabels for both handles) | value-label bubble painted for the active handle while dragging when `labeled=True` (shows `str(value)`) | ✅ |
| `activeColor` | theme role `PRIMARY` (active span + handles) | ✅ |
| `inactiveColor` | theme role `SURFACE_CONTAINER_HIGHEST` | ✅ |
| `overlayColor` | theme `PRIMARY` at `StateLayer` opacity | ✅ |
| `semanticFormatterCallback` | — | ⛔ Accessibility-text hook; no Qt analog wired in this port. |

Notes:
- Handles cannot cross (dragged handle clamps at the other) — verified by
  existing tests.
- `divisions` snaps both endpoints (and clamps to bounds) in `set_values`, so
  constructor, programmatic `set_values`, `set_divisions`, and drag all snap.
- Tick marks added to the range track (none existed before): inside the active
  span use `ON_PRIMARY`, the rest `OUTLINE_VARIANT`.

- [x] all properties verified or added
- [ ] Coordinator follow-up: optionally add `slider_pressed`/`slider_released`
  Signals to `MdRangeSlider` for `onChangeStart`/`onChangeEnd` parity (low
  priority; `valuesChanged` already conveys changes). No shared-file wiring is
  required for the `divisions` additions — gallery/demo work unchanged.
