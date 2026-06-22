"""Material 3 scrollbar for QtWidgets.

Ports Flutter's ``material/Scrollbar`` (cf.
https://api.flutter.dev/flutter/material/Scrollbar-class.html): a rounded,
overlay-style thumb painted on a transparent track. The thumb is faint at rest,
brightens and thickens (8 -> 12px) on hover — revealing a faint track + border —
and brightens further while dragged. All colors derive from the ``on-surface``
role at the exact opacities Flutter's ``_ScrollbarState`` uses (light vs dark).

Constants and color opacities are pulled verbatim from
``flutter/packages/flutter/lib/src/material/scrollbar.dart``:
thickness 8 (12 with track), cross-axis margin 2, min thumb length 48, radius 8,
hover animation 200ms.

The thumb geometry is the pure, windowless function :func:`thumb_metrics` (the
testable seam); the widget's ``paintEvent`` and drag handling just consume it.
Use :func:`use_material_scrollbars` to install it on a single scroll area, or
:func:`install_material_scrollbars` to convert an entire widget tree.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QAbstractScrollArea, QScrollBar, QWidget

from ...core.motion import MOTION_ENABLED
from ...tokens.color import ColorRole
from ...theme.theme_manager import ThemeManager

# From scrollbar.dart.
THICKNESS = 8.0
THICKNESS_HOVER = 12.0
MARGIN = 2.0  # _kScrollbarMargin (cross-axis gap from the viewport edge)
MIN_THUMB_LENGTH = 48.0  # _kScrollbarMinLength
RADIUS = 8.0  # _kScrollbarRadius
_HOVER_MS = 200  # _hoverAnimationController duration

# Reserve a fixed gutter sized for the *hover* thickness so the thumb growing on
# hover never reflows the scrolled content (Flutter overlays; a Qt QScrollBar
# occupies layout space, so we make that space constant).
GUTTER = int(THICKNESS_HOVER + 2 * MARGIN)  # 16


def thumb_metrics(
    minimum: int,
    maximum: int,
    page_step: int,
    value: int,
    groove_len: float,
    min_thumb_len: float = MIN_THUMB_LENGTH,
) -> tuple[float, float]:
    """Thumb ``(offset, length)`` along the groove, in pixels.

    Mirrors the classic scrollbar sizing: the thumb length is proportional to
    the visible page within the whole content (``range + page``), floored at
    ``min_thumb_len`` and capped at the groove; the offset is proportional to
    how far ``value`` sits within ``[minimum, maximum]``. With nothing to scroll
    (``maximum <= minimum``) the thumb fills the groove.
    """
    span = maximum - minimum
    if span <= 0 or groove_len <= 0:
        return 0.0, float(max(0.0, groove_len))
    content = span + page_step
    raw = groove_len * page_step / content if content > 0 else groove_len
    thumb_len = min(float(groove_len), max(float(min_thumb_len), raw))
    travel = groove_len - thumb_len
    frac = (value - minimum) / span
    frac = 0.0 if frac < 0.0 else 1.0 if frac > 1.0 else frac
    return travel * frac, thumb_len


class MdScrollBar(QScrollBar):
    """A custom-painted Material scrollbar (vertical or horizontal)."""

    def __init__(
        self, orientation: Qt.Orientation, parent: QWidget | None = None
    ) -> None:
        super().__init__(orientation, parent)
        self._hover = 0.0  # 0..1 idle->hover (color + thickness)
        self._dragging = False
        self._drag_grab = 0.0  # mouse-to-thumb-start offset while dragging
        self.setMouseTracking(True)
        if orientation == Qt.Orientation.Vertical:
            self.setFixedWidth(GUTTER)
        else:
            self.setFixedHeight(GUTTER)
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(_HOVER_MS)
        self._anim.valueChanged.connect(self._set_hover)
        # Repaint as the thumb travels / the range changes.
        self.valueChanged.connect(self.update)
        self.rangeChanged.connect(lambda *_: self.update())
        ThemeManager.instance().themeChanged.connect(self.update)

    # -- state -------------------------------------------------------------

    def _set_hover(self, value: object) -> None:
        self._hover = float(value)  # type: ignore[arg-type]
        self.update()

    def _animate_hover(self, target: float) -> None:
        if not MOTION_ENABLED:
            self._set_hover(target)
            return
        self._anim.stop()
        self._anim.setStartValue(self._hover)
        self._anim.setEndValue(target)
        self._anim.start()

    @property
    def _vertical(self) -> bool:
        return self.orientation() == Qt.Orientation.Vertical

    def _groove_len(self) -> float:
        return float(self.height() if self._vertical else self.width())

    def _thickness(self) -> float:
        return THICKNESS + (THICKNESS_HOVER - THICKNESS) * self._hover

    def _thumb_rect(self) -> QRectF:
        pos, length = thumb_metrics(
            self.minimum(), self.maximum(), self.pageStep(),
            self.value(), self._groove_len(),
        )
        thickness = self._thickness()
        if self._vertical:
            x = self.width() - MARGIN - thickness
            return QRectF(x, pos, thickness, length)
        y = self.height() - MARGIN - thickness
        return QRectF(pos, y, length, thickness)

    # -- colors (from scrollbar.dart, light vs dark) -----------------------

    def _thumb_color(self) -> QColor:
        dark = ThemeManager.instance().is_dark
        color = QColor(ThemeManager.instance().color(ColorRole.ON_SURFACE))
        if self._dragging:
            alpha = 0.75 if dark else 0.6
        else:
            idle = 0.3 if dark else 0.1
            hover = 0.65 if dark else 0.5
            alpha = idle + (hover - idle) * self._hover
        color.setAlphaF(alpha)
        return color

    def _track_colors(self) -> tuple[QColor, QColor]:
        """``(fill, border)`` for the track — only visible on hover/drag."""
        dark = ThemeManager.instance().is_dark
        on = ThemeManager.instance().color(ColorRole.ON_SURFACE)
        reveal = max(self._hover, 1.0 if self._dragging else 0.0)
        fill = QColor(on)
        fill.setAlphaF((0.05 if dark else 0.03) * reveal)
        border = QColor(on)
        border.setAlphaF((0.25 if dark else 0.1) * reveal)
        return fill, border

    # -- paint -------------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        if self.minimum() >= self.maximum():
            return  # nothing to scroll -> nothing to paint
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        fill, border = self._track_colors()
        if fill.alphaF() > 0 or border.alphaF() > 0:
            thickness = self._thickness()
            if self._vertical:
                track = QRectF(
                    self.width() - MARGIN - thickness, 0, thickness, self.height()
                )
            else:
                track = QRectF(
                    0, self.height() - MARGIN - thickness, self.width(), thickness
                )
            tr = thickness / 2.0
            if border.alphaF() > 0:
                painter.setPen(border)
            else:
                painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(fill)
            painter.drawRoundedRect(track, tr, tr)

        rect = self._thumb_rect()
        radius = min(RADIUS, min(rect.width(), rect.height()) / 2.0)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._thumb_color())
        painter.drawRoundedRect(rect, radius, radius)

    # -- interaction -------------------------------------------------------

    def enterEvent(self, event) -> None:  # noqa: N802
        self._animate_hover(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802
        if not self._dragging:
            self._animate_hover(0.0)
        super().leaveEvent(event)

    def _pos_along(self, point: QPointF) -> float:
        return point.y() if self._vertical else point.x()

    def _value_for_thumb_pos(self, pos: float) -> int:
        _, length = thumb_metrics(
            self.minimum(), self.maximum(), self.pageStep(),
            self.value(), self._groove_len(),
        )
        travel = self._groove_len() - length
        if travel <= 0:
            return self.minimum()
        frac = pos / travel
        frac = 0.0 if frac < 0.0 else 1.0 if frac > 1.0 else frac
        span = self.maximum() - self.minimum()
        return self.minimum() + round(frac * span)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return
        rect = self._thumb_rect()
        along = self._pos_along(event.position())
        if rect.contains(event.position()):
            self._dragging = True
            self._drag_grab = along - (rect.y() if self._vertical else rect.x())
            self._hover = 1.0
            self.update()
        else:
            # Click in the gutter pages toward the cursor.
            thumb_start = rect.y() if self._vertical else rect.x()
            step = self.pageStep() if along > thumb_start else -self.pageStep()
            self.setValue(self.value() + step)
        event.accept()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._dragging:
            along = self._pos_along(event.position())
            self.setValue(self._value_for_thumb_pos(along - self._drag_grab))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if self._dragging:
            self._dragging = False
            # Collapse the hover state if the cursor left during the drag.
            if not self.rect().contains(event.position().toPoint()):
                self._animate_hover(0.0)
            else:
                self.update()
            event.accept()
            return
        super().mouseReleaseEvent(event)


def use_material_scrollbars(area: QAbstractScrollArea) -> QAbstractScrollArea:
    """Install Material scrollbars on both axes of ``area``; returns ``area``."""
    area.setVerticalScrollBar(MdScrollBar(Qt.Orientation.Vertical, area))
    area.setHorizontalScrollBar(MdScrollBar(Qt.Orientation.Horizontal, area))
    return area


def disable_horizontal_scroll(area: QAbstractScrollArea) -> QAbstractScrollArea:
    """Genuinely lock ``area`` against horizontal scrolling; returns ``area``.

    ``ScrollBarAlwaysOff`` only *hides* the bar — the area can still be nudged
    horizontally by wheel/trackpad/keyboard. When fixed-width content sits in a
    vertically-scrolling area, the vertical bar's gutter narrows the viewport
    just below the content width, leaving a few pixels of horizontal "play".
    Pinning the horizontal range to zero removes it. Opt-in (do *not* apply to
    areas that scroll horizontally by other means, e.g. a ``QScroller``).
    """
    bar = area.horizontalScrollBar()

    def pin() -> None:
        if bar.minimum() != 0 or bar.maximum() != 0:
            bar.setRange(0, 0)  # re-emits rangeChanged once, then settles

    bar.rangeChanged.connect(lambda *_: pin())
    pin()
    return area


def install_material_scrollbars(root: QWidget) -> None:
    """Convert every scroll area in ``root``'s tree to Material scrollbars.

    Idempotent and safe to call once after building a window: scroll areas that
    keep a bar policy of ``ScrollBarAlwaysOff`` (e.g. the carousel) simply never
    show the replacement, so a blanket sweep does no harm.
    """
    areas = list(root.findChildren(QAbstractScrollArea))
    if isinstance(root, QAbstractScrollArea):
        areas.insert(0, root)
    for area in areas:
        if isinstance(area.verticalScrollBar(), MdScrollBar):
            continue  # already converted
        use_material_scrollbars(area)


__all__ = [
    "GUTTER",
    "MARGIN",
    "MIN_THUMB_LENGTH",
    "MdScrollBar",
    "RADIUS",
    "THICKNESS",
    "THICKNESS_HOVER",
    "disable_horizontal_scroll",
    "install_material_scrollbars",
    "thumb_metrics",
    "use_material_scrollbars",
]
