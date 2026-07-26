# Refresh indicator

Pull-to-refresh spinner over content.

**Classes:** `MdRefreshIndicator` · **Source:** `src/material_qt/widgets/refreshindicator/`
**Spec:** <https://api.flutter.dev/flutter/material/RefreshIndicator-class.html>. Ports Flutter's `RefreshIndicator`: a container that wraps a scrollable child and reveals a circular spinner descending from the top edge when the user pulls the content down past its top.

## Usage

```python
from material_qt import MdRefreshIndicator

content = build_scrollable_list()          # any QWidget
ri = MdRefreshIndicator(content, parent=page)

def on_refresh():
    reload_data()      # run your work...
    ri.end()           # ...then dismiss the spinner

ri.refresh.connect(on_refresh)

ri.begin()    # or reveal the spinner programmatically (no signal)
ri.trigger()  # reveal the spinner and emit `refresh`
```

## API

### MdRefreshIndicator

```python
MdRefreshIndicator(
    child: QWidget | None = None,
    parent: QWidget | None = None,
    *,
    displacement: int = 40,
    color_role: ColorRole = ColorRole.PRIMARY,
)
```

- `set_child(child)` — set the scrollable child the indicator wraps; `child` is the matching read-only property.
- `displacement` / `set_displacement(value)` — resting offset of the spinner from the top edge (Flutter `displacement`).
- `color_role` / `set_color_role(role)` — theme role of the spinner (Flutter `color`).
- `is_refreshing` — property; whether the spinner is currently shown.
- `begin()` — reveal the spinner at its resting displacement without emitting `refresh`.
- `trigger()` — reveal the spinner and emit `refresh` (equivalent to a release past the pull threshold, or a manual refresh request).
- `end()` — dismiss the spinner; call when the refresh work has finished. `finish` is an alias for `end`.

**Signals:**

- `refresh = Signal()` — emitted when a refresh is triggered (release past threshold or `trigger()`). Connect this to start the refresh work.

## Notes

- Flutter's `onRefresh` future becomes a Qt signal: the widget never knows when your work completes, so you must call `end()` / `finish()` yourself to dismiss the spinner.
- The pull gesture is best-effort, implemented via an event filter on the child: a downward mouse drag reveals and tracks the spinner, and releasing after a pull of at least 64px triggers a refresh; a shorter release snaps the spinner back offscreen. Because a real touch drag is awkward to drive headlessly, the programmatic `begin()` / `trigger()` / `end()` methods mirror the gesture exactly.
- The spinner is an indeterminate 36px `MdCircularProgress` (see [./progress.md](./progress.md)), so it inherits that widget's looping visible-only animation handling.
- Reveal/dismiss slides are 200ms `QVariantAnimation`s; with `core.motion.MOTION_ENABLED = False` (the test setting) the spinner jumps instantly to its target position and the indeterminate ring renders frozen.
- Dragging is ignored while `is_refreshing` is true, so a running refresh cannot be re-triggered by another pull.
