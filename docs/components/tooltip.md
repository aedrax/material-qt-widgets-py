# Tooltip

Brief label shown on hover or focus.

**Classes:** `MdTooltip` · **Source:** `src/material_qt/widgets/tooltip/`
**Spec:** <https://m3.material.io/components/tooltips>. Ports the Material 3 plain tooltip (cf. Flutter's `Tooltip` / `_TooltipDefaultsM3`).

## Usage

```python
from material_qt import MdOutlinedButton, MdTooltip

btn = MdOutlinedButton("Favorite", parent=page)
MdTooltip.attach(btn, "Add to favorites")

# Custom delays and placement below the target:
tip = MdTooltip.attach(btn, "Add to favorites", wait_ms=200, show_ms=0,
                       prefer_below=True)
tip.set_text("Remove from favorites")
```

## API

### MdTooltip

A plain tooltip attached to a target widget: a small `inverse-surface` label (`body-small` `inverse-on-surface` text, 4px corners, 8x4 padding) shown on hover above the target.

```python
MdTooltip(
    target: QWidget,
    text: str = "",
    *,
    wait_ms: int = 500,
    show_ms: int = 1500,
    prefer_below: bool = False,
    margin: int = 0,
)
```

- `MdTooltip.attach(target, text, **kwargs)` — classmethod; attach a tooltip to `target` and return it.
- `set_text(text)` — change the tooltip label.
- `prefer_below` / `set_prefer_below(value)` — whether the tooltip prefers to sit below the target (Flutter `preferBelow`).
- `margin` / `set_margin(value)` — inset kept from the window edges when positioning (Flutter `margin`).
- `hide_tooltip()` — stop the timers and hide immediately.

**Signals:** none.

## Notes

- Delays match Flutter's M3 defaults: the tooltip appears after `wait_ms` (500 ms) of hovering and auto-hides after `show_ms` (1500 ms). With `show_ms <= 0` there is no auto-hide; the tooltip stays until the pointer leaves.
- It also hides when the target is hidden, is pressed (mouse button down), or is destroyed; a destroyed target stops the pending timers so no callback fires against a dead C++ object.
- The tooltip is parented to the target's top-level window rather than being a separate native popup — the repo deliberately avoids top-level overlay windows. It reparents to the target's current window each time it shows, so attaching before the target is placed in its window is fine.
- Placement: centered horizontally over the target, above by default with an 8px gap, flipping to the other side when the preferred side would clip the window; `prefer_below=True` inverts the preference. The x/y are clamped to the window minus `margin`.
- The tooltip is mouse-transparent (`WA_TransparentForMouseEvents`), so it never steals hover from the target.
- Hover tracking installs an event filter on the target and sets `WA_Hover` on it; entering the target starts the wait timer, and leaving cancels or hides.
- The label color re-resolves on every theme change (`ThemeManager.themeChanged`), so tooltips follow light/dark switches; see [theming](../theming.md).
- The default delay constants live in the module as `_DEFAULT_WAIT = 500` and `_DEFAULT_SHOW = 1500` (milliseconds).
- Buttons can also pass `tooltip="..."` at construction (see [button](./button.md)); this class is the standalone form for arbitrary widgets.
