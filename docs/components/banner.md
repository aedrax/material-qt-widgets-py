# Banner

Prominent inline message with actions.

**Classes:** `MdBanner` · **Source:** `src/material_qt/widgets/banner/`
**Spec:** <https://api.flutter.dev/flutter/material/MaterialBanner-class.html>. Ports the Material 3 banner, i.e. Flutter's `MaterialBanner` (banners are not in the current m3.material.io component catalogue, so the Flutter API page is the reference).

## Usage

```python
from material_qt import MdBanner

banner = MdBanner(
    "Your photos are being backed up to the cloud.",
    icon="cloud_upload",
    parent=page,
)
turn_off = banner.add_action("Turn off")
open_btn = banner.add_action("Open")
turn_off.clicked.connect(disable_backup)
open_btn.clicked.connect(open_settings)
layout.addWidget(banner)
```

## API

### MdBanner

```python
MdBanner(
    text: str = "",
    parent: QWidget | None = None,
    *,
    icon: str = "",
    elevation: int = 0,
    background_role: ColorRole = ColorRole.SURFACE,
    divider_role: ColorRole = ColorRole.OUTLINE_VARIANT,
)
```

- `add_action(text)` — append a trailing text-button action and return the `MdTextButton`; connect the returned button's `clicked` yourself.
- `elevation` — property; the banner elevation level (Flutter `elevation`). `set_elevation(level)` is inherited from `MaterialWidgetMixin`.
- `background_role` / `set_background_role(role)` — container fill color role (Flutter `backgroundColor`).
- `divider_role` / `set_divider_role(role)` — bottom-edge divider color role (Flutter `dividerColor`).

**Signals:** none. Each action returns its `MdTextButton`; convenience signals are not used — connect the returned button's `clicked`.

## Notes

- Layout: an optional leading 24px `primary` icon (a Material Symbols ligature name), word-wrapped `body-medium` `on-surface` supporting text, a trailing row of text-button actions, and an `outline-variant` divider along the bottom edge.
- Banners are non-modal and inline: unlike a [snackbar](./snackbar.md), a banner stays until dismissed by an action — there is no timer and no built-in dismiss method. Hide or remove the widget from your own action handlers.
- The container is square-cornered (`ShapeScale.NONE`) on a `surface` fill by default, at elevation 0; all colors re-resolve on theme change.
- Actions use `MdTextButton` from [./button.md](./button.md); see [../theming.md](../theming.md) for `ColorRole`.
