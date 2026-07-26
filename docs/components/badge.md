# Badge

Small status indicator overlaid on an anchor.

**Classes:** `MdBadge`, `attach` · **Source:** `src/material_qt/widgets/badge/`
**Spec:** <https://m3.material.io/components/badges>. Matches Material Web's `labs/badge` component (a labs widget), with placement arguments mirroring Flutter's `Badge`.

## Usage

```python
from material_qt import MdBadge, attach

dot = MdBadge()                # empty value -> small 6px dot
dot.attach(icon_button)        # overlay on the host's top-right corner

count = MdBadge("99+")         # non-empty value -> large pill
attach(count, inbox_button)    # module-level helper, same effect

count.set_value("3")           # switch the displayed value live
count.set_label_visible(False) # hide without detaching
```

Run the demo: `python -m material_qt.widgets.badge.demo`.

## API

### MdBadge

```python
MdBadge(
    value: str = "",
    parent: QWidget | None = None,
    *,
    is_label_visible: bool = True,
    alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
    offset: QPoint | None = None,
    background_role: ColorRole = ColorRole.ERROR,
    text_role: ColorRole = ColorRole.ON_ERROR,
)
```

- `value` / `set_value(value)` — the displayed value; empty string means the small dot form, non-empty the large pill. `None` is coerced to `""`, other values to `str`.
- `is_large` — property; whether the badge renders the large (value) form.
- `is_label_visible` / `set_label_visible(visible)` — show/hide the badge entirely (Flutter `isLabelVisible`); when `False` the badge stays hidden on its host.
- `alignment` / `set_alignment(alignment)` — anchor corner on the host (Flutter `alignment`; default top-right).
- `offset` / `set_offset(offset)` — pixel offset from the anchor corner (Flutter `offset`).
- `background_role` / `set_background_role(role)` — fill color role (Flutter `backgroundColor`).
- `text_role` / `set_text_role(role)` — label color role (Flutter `textColor`).
- `attach(host)` — overlay this badge on `host`: the badge is reparented to `host` and repositions itself whenever the host is resized, moved, shown, or hidden. Re-attaching to a new host detaches from the old one first.

**Signals:** none.

### attach

```python
attach(badge: MdBadge, host: QWidget) -> None
```

Module-level convenience that overlays `badge` on `host`'s top-right corner; equivalent to `badge.attach(host)`.

## Notes

- Two forms, matching the web component: leaving `value` empty gives the small badge — a 6px error-colored dot; a non-empty `value` gives the large badge — a 16px-tall pill with 4px horizontal padding showing the value in `on-error` `label-small` typography. Sizes come from the `md-comp-badge` tokens.
- The pill shape is `corner-full` (radius equals half the height), and colors resolve live from `ThemeManager`, so the badge re-themes automatically.
- The badge is transparent to mouse events, takes no focus, and has a fixed size policy — a layout can never stretch it. It is intended as an overlay via `attach`, not as a layout child.
- Placement clamps the anchor corner to the host, then applies the (possibly negative) `offset` unclamped, matching Flutter's offset semantics.
- After `attach`, an internal event filter on the host keeps the badge positioned and mirrors host visibility: the badge shows with the host (when `is_label_visible`) and hides with it.
- The badge is static — no animation is involved, so it is unaffected by `core.motion.MOTION_ENABLED`.
- See [../theming.md](../theming.md) for `ColorRole` and typography roles.
