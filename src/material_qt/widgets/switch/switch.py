"""Material 3 switch for QtWidgets.

Ports Material Web's ``md-switch``. A 52x32 pill track with a circular handle
that animates position and size as it toggles: unselected handle 16px
(``on-surface-variant``) on a ``surface-container-highest`` track with a 2px
``outline`` border; selected handle 24px (``on-primary``) on a ``primary`` track;
the handle grows to 28px while pressed. A 40px state layer is painted around the
handle on hover/press. Built on :class:`QAbstractButton` (checkable).
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QAbstractButton, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...core.motion import MOTION_ENABLED, duration_ms, easing_curve
from ...tokens.color import ColorRole
from ...tokens.motion import Duration, Easing
from ...tokens.shape import ShapeScale
from ...tokens.state import StateLayer
from ...theme.theme_manager import ThemeManager
from ..icon.icon import material_symbols_font

_TRACK_W = 52
_TRACK_H = 32
_WIDGET_H = 40  # room for the 40px handle state layer
_OUTLINE_WIDTH = 2.0
_HANDLE_UNSELECTED = 16.0
_HANDLE_SELECTED = 24.0
_HANDLE_PRESSED = 28.0
_STATE_LAYER = 40.0
_ICON_SIZE = 16  # M3 thumb icon size
_DISABLED_OPACITY = 0.38
_ANIM = Duration.SHORT4  # 200ms


class MdSwitch(MaterialWidgetMixin, QAbstractButton):
    """A Material 3 switch (on/off toggle)."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        checked: bool = False,
        thumb_icon_on: str | None = None,
        thumb_icon_off: str | None = None,
        label: str | None = None,
    ) -> None:
        super().__init__(parent)
        self.setCheckable(True)
        self._t = 1.0 if checked else 0.0
        # thumbIcon: ligature names shown on the handle, resolved by state.
        # ``off`` is shown while unselected, ``on`` while selected (mirrors
        # Flutter's inactive/active Icon resolution). Either may be None.
        self._thumb_icon_on = thumb_icon_on
        self._thumb_icon_off = thumb_icon_off
        if label is not None:
            self.setAccessibleName(label)
        # One persistent animation, reused per toggle (avoids stale C++ object
        # on repeated clicks once an animation has finished).
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(duration_ms(_ANIM))
        self._anim.setEasingCurve(easing_curve(Easing.EMPHASIZED))
        self._anim.valueChanged.connect(self._set_t)
        self._init_material(
            shape=ShapeScale.FULL,
            ripple=False,  # custom moving handle state layer instead
            focus_ring=True,
        )
        if checked:
            self.setChecked(True)
        self.toggled.connect(self._on_toggled)

    # -- state -------------------------------------------------------------

    def _on_toggled(self, checked: bool) -> None:
        target = 1.0 if checked else 0.0
        self._anim.stop()
        if not MOTION_ENABLED or not self.isVisible():
            self._t = target
            self.update()
            return
        self._anim.setStartValue(self._t)
        self._anim.setEndValue(target)
        self._anim.start()

    def _set_t(self, value) -> None:
        self._t = float(value)
        self.update()

    # -- properties --------------------------------------------------------

    @property
    def thumb_icon_on(self) -> str | None:
        """Ligature name drawn on the handle while selected (or ``None``)."""
        return self._thumb_icon_on

    @property
    def thumb_icon_off(self) -> str | None:
        """Ligature name drawn on the handle while unselected (or ``None``)."""
        return self._thumb_icon_off

    def set_thumb_icon(
        self, on: str | None = None, off: str | None = None
    ) -> None:
        """Set the handle icons (Material ``thumbIcon``).

        ``on`` is shown while the switch is selected, ``off`` while unselected.
        Pass ``None`` for a state to show no icon there.
        """
        self._thumb_icon_on = on
        self._thumb_icon_off = off
        self.update()

    @property
    def label(self) -> str:
        """Accessible name (Material ``semanticLabel``)."""
        return self.accessibleName()

    def set_label(self, label: str | None) -> None:
        self.setAccessibleName(label or "")

    # -- sizing ------------------------------------------------------------

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(_TRACK_W, _WIDGET_H)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return self.sizeHint()

    # -- repaint / enable --------------------------------------------------

    def enterEvent(self, event) -> None:  # noqa: N802
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: N802
        super().leaveEvent(event)
        self.update()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        super().mousePressEvent(event)
        self.update()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        super().mouseReleaseEvent(event)
        self.update()

    def changeEvent(self, event) -> None:  # noqa: N802
        super().changeEvent(event)
        self.update()

    # -- geometry ----------------------------------------------------------

    def _handle_diameter(self) -> float:
        base = _HANDLE_UNSELECTED + (_HANDLE_SELECTED - _HANDLE_UNSELECTED) * self._t
        if self.isDown() and self.isEnabled():
            return _HANDLE_PRESSED
        return base

    def _handle_center(self) -> tuple[float, float]:
        track_x = (self.width() - _TRACK_W) / 2.0
        cy = self.height() / 2.0
        left = track_x + _TRACK_W * 0.0 + 16.0
        right = track_x + _TRACK_W - 16.0
        cx = left + (right - left) * self._t
        return cx, cy

    # -- painting ----------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        theme = ThemeManager.instance()
        enabled = self.isEnabled()
        t = self._t

        track_x = (self.width() - _TRACK_W) / 2.0
        track_y = (self.height() - _TRACK_H) / 2.0
        track = QRectF(track_x, track_y, _TRACK_W, _TRACK_H)
        radius = _TRACK_H / 2.0

        # Track fill: crossfade surface-container-highest -> primary.
        off_track = theme.color(ColorRole.SURFACE_CONTAINER_HIGHEST)
        on_track = theme.color(ColorRole.PRIMARY)
        track_color = _blend(off_track, on_track, t)
        if not enabled:
            base = theme.color(ColorRole.SURFACE_CONTAINER_HIGHEST)
            base.setAlphaF(0.12)
            track_color = base
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(track, radius, radius)

        # Outline (only meaningful while unselected; fades out as t->1).
        if t < 1.0:
            outline = theme.color(ColorRole.ON_SURFACE if not enabled else ColorRole.OUTLINE)
            outline.setAlphaF((_DISABLED_OPACITY if not enabled else 1.0) * (1.0 - t))
            pen = QPen(outline)
            pen.setWidthF(_OUTLINE_WIDTH)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            inset = _OUTLINE_WIDTH / 2.0
            painter.drawRoundedRect(
                track.adjusted(inset, inset, -inset, -inset),
                radius - inset,
                radius - inset,
            )

        cx, cy = self._handle_center()

        # Handle state layer (hover/press), a 40px circle around the handle.
        layer = None
        if enabled:
            if self.isDown():
                layer = StateLayer.PRESSED
            elif self.underMouse():
                layer = StateLayer.HOVER
        if layer is not None:
            sl = theme.color(ColorRole.PRIMARY if t >= 0.5 else ColorRole.ON_SURFACE)
            sl.setAlphaF(layer.opacity)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(sl)
            r = _STATE_LAYER / 2.0
            painter.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))

        # Handle.
        dia = self._handle_diameter()
        off_handle = theme.color(ColorRole.OUTLINE)
        on_handle = theme.color(ColorRole.ON_PRIMARY)
        handle_color = _blend(off_handle, on_handle, t)
        if not enabled:
            handle_color = theme.color(ColorRole.ON_SURFACE)
            handle_color.setAlphaF(_DISABLED_OPACITY)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(handle_color)
        hr = dia / 2.0
        painter.drawEllipse(QRectF(cx - hr, cy - hr, 2 * hr, 2 * hr))

        # Thumb icon (Material thumbIcon): off shown unselected, on selected.
        icon = self._thumb_icon_on if t >= 0.5 else self._thumb_icon_off
        if icon:
            self._draw_thumb_icon(painter, icon, cx, cy, enabled)

    def _draw_thumb_icon(
        self, painter: QPainter, name: str, cx: float, cy: float, enabled: bool
    ) -> None:
        font = material_symbols_font(_ICON_SIZE)
        if font is None:
            return
        theme = ThemeManager.instance()
        color = theme.color(ColorRole.ON_PRIMARY_CONTAINER)
        if not enabled:
            color = theme.color(ColorRole.ON_SURFACE)
            color.setAlphaF(_DISABLED_OPACITY)
        painter.save()
        painter.setFont(font)
        painter.setPen(color)
        box = QRectF(cx - _ICON_SIZE, cy - _ICON_SIZE, 2 * _ICON_SIZE, 2 * _ICON_SIZE)
        painter.drawText(box, Qt.AlignmentFlag.AlignCenter, name)
        painter.restore()


def _blend(a: QColor, b: QColor, t: float) -> QColor:
    t = max(0.0, min(1.0, t))
    return QColor(
        round(a.red() + (b.red() - a.red()) * t),
        round(a.green() + (b.green() - a.green()) * t),
        round(a.blue() + (b.blue() - a.blue()) * t),
        round(a.alpha() + (b.alpha() - a.alpha()) * t),
    )


__all__ = ["MdSwitch"]
