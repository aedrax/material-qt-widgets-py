# Progress indicators

Linear and circular progress.

**Classes:** `MdLinearProgress`, `MdCircularProgress` · **Source:** `src/material_qt/widgets/progress/`
**Spec:** <https://m3.material.io/components/progress-indicators>. Ports Material Web's `progress/` package, with each indicator in determinate (`value` 0..1) and indeterminate (continuous animation) modes.

## Usage

```python
from material_qt import MdCircularProgress, MdLinearProgress

# Determinate: drive `value` between 0.0 and 1.0.
bar = MdLinearProgress(value=0.6, parent=page)
bar.set_value(0.75)

# Indeterminate: loops while the widget is visible.
busy_bar = MdLinearProgress(indeterminate=True, parent=page)
spinner = MdCircularProgress(indeterminate=True, parent=page)
```

Run the demo: `python -m material_qt.widgets.progress.demo`.

## API

Both classes share a common base; the shared constructor arguments and the shared methods below behave identically on each.

### MdLinearProgress

```python
MdLinearProgress(
    parent: QWidget | None = None,
    *,
    value: float = 0.0,
    indeterminate: bool = False,
    color_role: ColorRole = ColorRole.PRIMARY,
    track_role: ColorRole = ColorRole.SURFACE_CONTAINER_HIGHEST,
    min_height: float = 4,
    border_radius: float | None = None,
)
```

- `value` / `set_value(value)` — determinate progress, clamped to 0.0..1.0.
- `indeterminate` / `set_indeterminate(value)` — switch modes; enabling starts the looping animation (when visible), disabling stops it.
- `color_role` / `set_color_role(role)` — theme role of the active indicator (Flutter `color`/`valueColor`).
- `track_role` / `set_track_role(role)` — theme role of the track (Flutter `backgroundColor`).
- `min_height` / `set_min_height(value)` — bar thickness (Flutter `minHeight`).
- `border_radius` / `set_border_radius(value)` — corner radius; when unset it defaults to half the thickness, giving a fully rounded bar (Flutter `borderRadius`).

**Signals:** none.

### MdCircularProgress

```python
MdCircularProgress(
    parent: QWidget | None = None,
    *,
    value: float = 0.0,
    indeterminate: bool = False,
    size: int = 48,
    color_role: ColorRole = ColorRole.PRIMARY,
    track_role: ColorRole = ColorRole.SURFACE_CONTAINER_HIGHEST,
    stroke_width: float = 4,
)
```

- Shares `value`, `indeterminate`, `color_role`, and `track_role` with `MdLinearProgress` (see above).
- `size` — constructor-only diameter of the ring; also its `sizeHint()`.
- `stroke_width` / `set_stroke_width(value)` — ring thickness (Flutter `strokeWidth`).

**Signals:** none.

## Notes

- Determinate mode fills to `value`; the linear bar sweeps left to right, the circular ring starts at 12 o'clock and sweeps clockwise. Indeterminate mode animates a ~40% width bar (linear) or a rotating arc whose span breathes between roughly 20 and 300 degrees (circular).
- Defaults come from module constants: 4px thickness, 48px circular size, 80px linear minimum width, and a 1600ms indeterminate loop.
- Colors are the M3 defaults: `primary` active indicator on a `surface-container-highest` track, resolved live from the theme.
- The indeterminate animation is a looping `QPropertyAnimation`-style `QVariantAnimation` that runs only while the widget is visible — it starts on show and stops on hide/destroy, so no timer leaks after teardown and a never-shown widget never ticks.
- With `core.motion.MOTION_ENABLED = False` (the test setting), the indeterminate animation never starts, so the indicator renders frozen; determinate rendering is unaffected.
- See [../theming.md](../theming.md) for `ColorRole` and theme switching.
