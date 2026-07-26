# Snackbar

Brief message with an optional action.

**Classes:** `MdSnackbar` · **Source:** `src/material_qt/widgets/snackbar/`
**Spec:** <https://m3.material.io/components/snackbar>. Follows Flutter's snackbar semantics per the module docstring — the 4000ms default matches Flutter's `_snackBarDisplayDuration`, and the docstring documents a deliberate divergence from Flutter's `ScaffoldMessenger` queueing (see Notes).

## Usage

```python
from material_qt import MdSnackbar

def show_snackbar():
    host = page.window()
    sb = MdSnackbar(host, "Photo deleted from album", action_label="Undo")
    sb.action.connect(undo_delete)           # action click
    sb.dismissed.connect(sb.deleteLater)     # transient: don't accumulate
    sb.open()

show_button.clicked.connect(show_snackbar)
```

## API

### MdSnackbar

```python
MdSnackbar(
    parent: QWidget,
    text: str = "",
    *,
    action_label: str = "",
    duration: int = 4000,
    behavior: str = "floating",
    show_close_icon: bool = False,
)
```

`parent` is required — it is the host widget the snackbar pins itself to and slides up from.

- `open()` — show the snackbar: slides up from the host's bottom edge, starts the auto-dismiss timer, and replaces any snackbar already shown on the same host.
- `dismiss()` — dismiss early, animating back below the edge before hiding and emitting `dismissed`.
- `behavior` — read-only property; `"floating"` (inset, rounded, default) or `"fixed"` (flush full-width against the bottom edge), mirroring Flutter's `SnackBarBehavior`. Invalid values fall back to `"floating"`.

**Signals:**

- `action = Signal()` — emitted when the action label is clicked (the snackbar then dismisses itself).
- `dismissed = Signal()` — emitted when the snackbar closes, for any reason.

## Notes

- Styling is the M3 inverse scheme: an `inverse-surface` container with `body-medium` `inverse-on-surface` text, an `inverse-primary` text action, 4px corners (extra-small shape), and level-3 elevation.
- `duration` defaults to 4000ms; the timer starts on `open()`. A duration of 0 or less disables auto-dismiss entirely — the snackbar stays until dismissed by the action, the close icon, or `dismiss()`.
- Replace-on-open: unlike Flutter's `ScaffoldMessenger`, which queues snackbars, opening a snackbar here replaces any snackbar currently shown on the same host — the older one is hidden immediately with no exit animation and emits `dismissed` before the new one appears. A module-level weak registry keyed by host tracks the currently-shown snackbar per host.
- Snackbars are transient and one-shot — connect `dismissed` to `deleteLater` to avoid accumulating hidden instances if you create one per message.
- `show_close_icon=True` adds a trailing 20px close icon that dismisses without emitting `action`.
- The enter/exit transition is a pure slide (200ms, emphasized easing); no opacity effect is used because nesting `QGraphicsOpacityEffect` with the elevation drop shadow makes Qt spam "painter not active". With `core.motion.MOTION_ENABLED = False` (the test setting) the snackbar snaps to its resting or hidden position instantly.
- The snackbar tracks host resizes while visible and re-centers itself; width is clamped between 344px and 600px in floating mode.
- See [./banner.md](./banner.md) for persistent inline messages, and [../theming.md](../theming.md) for the color roles used here.
