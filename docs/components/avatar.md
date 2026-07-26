# Avatar

Circular image or initials for a person.

**Classes:** `MdCircleAvatar` · **Source:** `src/material_qt/widgets/avatar/`
**Spec:** <https://api.flutter.dev/flutter/material/CircleAvatar-class.html> (Flutter-parity widget; not in the M3 component catalogue). Ports Flutter's `CircleAvatar` — a round container showing either an image or short fallback content such as initials.

## Usage

```python
from material_qt import MdCircleAvatar
from material_qt.tokens.color import ColorRole

ab = MdCircleAvatar(text="AB")                      # 40px circle with initials
mj = MdCircleAvatar(text="MJ",
                    background_role=ColorRole.TERTIARY_CONTAINER,
                    foreground_role=ColorRole.ON_TERTIARY_CONTAINER)
qt = MdCircleAvatar(text="QT", radius=28)           # 56px circle
photo = MdCircleAvatar(image="portrait.png")        # image clipped to the circle
```

## API

### MdCircleAvatar

Extends `QWidget`. The widget is fixed-size: `radius * 2` square.

```python
MdCircleAvatar(
    parent: QWidget | None = None,
    *,
    text: str = "",
    image: QPixmap | str | None = None,
    radius: int = 20,
    background_role: ColorRole = ColorRole.PRIMARY_CONTAINER,
    foreground_role: ColorRole = ColorRole.ON_PRIMARY_CONTAINER,
)
```

- `radius` — read/write property (also `set_radius(value)`); half the diameter in pixels, clamped to at least 0. Changing it resizes the fixed widget size.
- `text` — read/write property (also `set_text(value)`); fallback text (e.g. initials) shown when no image is set.
- `set_image(image)` — set the avatar image from a `QPixmap` or a file path. Passing `None` (or an unloadable path/null pixmap) clears the image, falling back to the text content.
- `pixmap` — read-only property; the current `QPixmap`, or `None` when showing text.
- `background_role` — read/write property; theme color role for the circle fill.
- `foreground_role` — read/write property; theme color role for the fallback text.

No signals.

## Notes

- Precedence: when a loadable image is set it is drawn clipped to the circle and takes precedence over `text`; the text only paints when `pixmap` is `None`. An unloadable image (null `QPixmap` or bad path) is treated as no image.
- The image is scaled with `KeepAspectRatioByExpanding` and smooth transformation, centered, and clipped to the circle — a cover fit, so non-square images are cropped rather than letterboxed.
- Sizing is expressed as a `radius` (half the diameter), matching Flutter: the default 20 yields a 40px circle.
- Flutter's `minRadius`/`maxRadius` (animated constraint pair) and the image error callbacks are not ported — a single `radius` covers the sizing need, and Qt surfaces image-load failure synchronously via `QPixmap.isNull`.
- Fallback text uses the `TITLE_MEDIUM` typescale font, set as the widget font at construction; both fill and text colors resolve from theme roles and repaint on `themeChanged`. See [theming](../theming.md) for the role catalogue.
- Because the size is fixed via `setFixedSize`, the avatar never stretches in layouts; place it with alignment flags rather than stretch factors.
- The background circle is always painted, even under an image — visible only until the pixmap covers it, since the cover-fit image fills the clip circle.
- For an icon inside a circle (rather than a photo or initials), compose an [icon](./icon.md) over a container instead; the avatar renders only text or an image.
