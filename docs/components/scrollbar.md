# Scrollbar

Rounded thumb that thickens on hover.

**Classes:** `MdScrollBar` · **Source:** `src/material_qt/widgets/scrollbar/`
**Spec:** <https://api.flutter.dev/flutter/material/Scrollbar-class.html> (Flutter-parity widget; not in the M3 component catalogue). Ports Flutter's `material/Scrollbar`: a rounded, overlay-style thumb on a transparent track — faint at rest, brighter and thicker (8 → 12px) on hover, brighter still while dragged. Constants and color opacities are pulled verbatim from `flutter/.../material/scrollbar.dart`.

## Usage

```python
from PySide6.QtWidgets import QScrollArea

from material_qt import use_material_scrollbars, install_material_scrollbars

# One scroll area:
sa = QScrollArea()
sa.setWidgetResizable(True)
sa.setWidget(content)
use_material_scrollbars(sa)

# ...or convert every scroll area under a window, once, after building it:
install_material_scrollbars(window)
```

## API

### MdScrollBar

Extends `QScrollBar` (vertical or horizontal), custom-painted. Normally installed via the helper functions rather than constructed directly.

```python
MdScrollBar(
    orientation: Qt.Orientation,
    parent: QWidget | None = None,
)
```

- Standard `QScrollBar` API applies (`value`, `setValue`, `pageStep`, `valueChanged`, ...); the subclass adds painting and interaction only, no new public methods.
- Clicking the thumb drags it; clicking the gutter pages toward the cursor (one `pageStep()` per click).
- When there is nothing to scroll (`minimum() >= maximum()`) nothing is painted.
- The bar is fixed at `GUTTER` (16px) wide (vertical) or tall (horizontal).

No custom signals (inherits `QScrollBar`'s).

### Module functions

All four functions are re-exported from `material_qt`; the painted constants below are importable from `material_qt.widgets.scrollbar.scrollbar`.

- `use_material_scrollbars(area: QAbstractScrollArea) -> QAbstractScrollArea` — install Material scrollbars on both axes of `area`; returns `area`.
- `install_material_scrollbars(root: QWidget) -> None` — convert every `QAbstractScrollArea` in `root`'s tree (including `root` itself if it is one). Idempotent: areas whose vertical bar is already an `MdScrollBar` are skipped, and areas with a bar policy of `ScrollBarAlwaysOff` simply never show the replacement, so a blanket sweep does no harm.
- `disable_horizontal_scroll(area: QAbstractScrollArea) -> QAbstractScrollArea` — genuinely lock `area` against horizontal scrolling by pinning the horizontal range to `(0, 0)` on every `rangeChanged`; returns `area`. `ScrollBarAlwaysOff` only *hides* the bar — the area can still be nudged by wheel/trackpad/keyboard. Opt-in: do not apply to areas that scroll horizontally by other means (e.g. a `QScroller`).
- `thumb_metrics(minimum, maximum, page_step, value, groove_len, min_thumb_len=MIN_THUMB_LENGTH) -> tuple[float, float]` — pure function returning the thumb `(offset, length)` along the groove in pixels; the testable seam the widget's painting and drag handling consume. Thumb length is proportional to the visible page within `range + page`, floored at `min_thumb_len` and capped at the groove; with nothing to scroll the thumb fills the groove.

### Painted constants

From `scrollbar.dart`: `THICKNESS = 8.0`, `THICKNESS_HOVER = 12.0`, `MARGIN = 2.0` (cross-axis gap from the viewport edge), `MIN_THUMB_LENGTH = 48.0`, `RADIUS = 8.0`, and `GUTTER = int(THICKNESS_HOVER + 2 * MARGIN)` = 16.

## Notes

- Fixed 16px gutter rationale: Flutter overlays its scrollbar over the content, but a Qt `QScrollBar` occupies layout space. The gutter is therefore reserved at the *hover* thickness (12 + 2·2 margin) so the thumb thickening on hover never reflows the scrolled content.
- Hover state animates over 200ms (Flutter's `_hoverAnimationController` duration); the animation is skipped and the state applied instantly when motion is disabled (`MOTION_ENABLED` is false).
- All colors derive from the `on-surface` role at the exact opacities Flutter's `_ScrollbarState` uses, differing by light vs dark theme: thumb idle 0.1/0.3, hover 0.5/0.65, drag 0.6/0.75; the track fill (0.03/0.05) and border (0.1/0.25) are only revealed on hover or drag.
- Releasing a drag with the cursor outside the bar collapses the hover state back to idle.
- The bar repaints on `valueChanged`, `rangeChanged`, and theme changes.
- The gallery uses `install_material_scrollbars` on the whole window; see [theming](../theming.md) for how the `on-surface` role resolves.
