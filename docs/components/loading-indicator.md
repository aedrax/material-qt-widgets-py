# Loading indicator

Morphing shape for short waits.

**Classes:** `MdLoadingIndicator` · **Source:** `src/material_qt/widgets/loadingindicator/`
**Spec:** <https://m3.material.io/components/loading-indicator>. Ports the Material 3 Expressive loading indicator: an indeterminate activity indicator whose active shape loops through a morph sequence while rotating, distinct from the circular progress spinner (see [./progress.md](./progress.md)).

## Usage

```python
from material_qt import MdLoadingIndicator

indicator = MdLoadingIndicator(parent=page)          # default 48px
large = MdLoadingIndicator(parent=page, size=64)

indicator.stop()   # stop until start() is called again
indicator.start()  # resume
```

The gallery shows the default and a 64px variant side by side:

```python
row.addWidget(MdLoadingIndicator())
row.addWidget(MdLoadingIndicator(size=64))
```

## API

### MdLoadingIndicator

```python
MdLoadingIndicator(
    parent: QWidget | None = None,
    *,
    size: int = 48,
)
```

- `start()` — run the animation; while hidden it stays parked until shown.
- `stop()` — stop the animation; it will not restart on show until `start()` is called again.
- `is_running` — property; whether the underlying animation is currently in the `Running` state.
- `get_t()` / `set_t(value)` — the loop phase in 0..1 (wraps modulo 1); also exposed as the Qt `Property` `t`, drivable for testing.
- `size` is constructor-only; the widget is fixed at `size` by `size` pixels, and `sizeHint()` reports the same square.

**Signals:** none.

## Notes

- The widget starts in the active state and animates whenever it becomes visible; the animation is started/stopped from show/hide events — never in the constructor — so a never-shown indicator does not tick at frame rate forever. Hiding pauses it; re-showing resumes automatically unless `stop()` was called.
- This is a deliberate approximation of the upstream indicator: instead of the true spring-based morph between the seven canonical M3 shapes (which is deferred), it rotates a filled `primary` rounded "cookie" shape whose lobe count cycles through the sequence 4, 7, 5, 6, 8 over one 4000ms loop.
- Per the module docstring, this indicator is best for short processes (200ms–5s); for longer or measurable work use a progress indicator instead.
- The animation is a looping `QVariantAnimation` (`setLoopCount(-1)`); with `core.motion.MOTION_ENABLED = False` (the test setting) `start()` does nothing, so the shape renders frozen at its current `t`. Tests drive the `t` property directly instead.
- The shape fill is `ColorRole.PRIMARY`, re-resolved on every theme change; see [../theming.md](../theming.md).
