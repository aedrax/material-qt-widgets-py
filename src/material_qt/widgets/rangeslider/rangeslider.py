"""Material 3 range slider for QtWidgets.

Ports the Material 3 range (two-handle) slider (cf. Flutter's ``RangeSlider``):
a 4px track with the active span between the two ``primary`` handles filled
``primary`` and the rest ``surface-container-highest``, two 20px ``primary``
handles with a 40px state layer on hover/press, and value-label bubbles while
dragging. The handles cannot cross — the dragged handle stops at the other.

Unlike :class:`MdSlider` this is not a ``QAbstractSlider`` (which models a single
value); it exposes ``low``/``high`` and emits ``valuesChanged(low, high)``.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QFontMetrics, QPainter
from PySide6.QtWidgets import QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...core.typography_util import font_for
from ...tokens.color import ColorRole
from ...tokens.state import StateLayer
from ...tokens.typography import TypescaleRole, spec_for
from ...theme.theme_manager import ThemeManager

_TRACK_H = 4
_HANDLE = 20
_STATE_LAYER = 40
_WIDGET_H = 40
_DISABLED_OPACITY = 0.38


class MdRangeSlider(MaterialWidgetMixin, QWidget):
    """A Material 3 two-handle range slider."""

    valuesChanged = Signal(int, int)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        minimum: int = 0,
        maximum: int = 100,
        low: int = 0,
        high: int = 100,
        step: int = 0,
    ) -> None:
        super().__init__(parent)
        self._min = minimum
        self._max = maximum
        self._step = step
        self._low = minimum
        self._high = maximum
        self._active: str | None = None  # 'low' | 'high' while dragging
        self._init_material(shape=None, ripple=False, focus_ring=False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self._label_font = font_for(spec_for(TypescaleRole.LABEL_LARGE))
        self.set_values(low, high)

    # -- values ------------------------------------------------------------

    def values(self) -> tuple[int, int]:
        return self._low, self._high

    @property
    def low(self) -> int:
        return self._low

    @property
    def high(self) -> int:
        return self._high

    def _clamp(self, v: int) -> int:
        return int(max(self._min, min(self._max, v)))

    def set_values(self, low: int, high: int) -> None:
        low, high = self._clamp(low), self._clamp(high)
        if low > high:
            low, high = high, low
        changed = (low, high) != (self._low, self._high)
        self._low, self._high = low, high
        if changed:
            self.valuesChanged.emit(low, high)
        self.update()

    # -- geometry ----------------------------------------------------------

    def _track_rect(self) -> QRectF:
        margin = _HANDLE / 2.0
        cy = self.height() / 2.0
        return QRectF(margin, cy - _TRACK_H / 2.0, self.width() - 2 * margin, _TRACK_H)

    def _fraction(self, value: int) -> float:
        span = self._max - self._min
        return 0.0 if span <= 0 else (value - self._min) / span

    def _handle_x(self, value: int) -> float:
        track = self._track_rect()
        return track.left() + track.width() * self._fraction(value)

    def _value_from_x(self, x: float) -> int:
        track = self._track_rect()
        if track.width() <= 0:
            return self._min
        f = max(0.0, min(1.0, (x - track.left()) / track.width()))
        raw = self._min + f * (self._max - self._min)
        if self._step > 0:
            raw = self._min + round((raw - self._min) / self._step) * self._step
        return self._clamp(int(round(raw)))

    def _nearest_handle(self, x: float) -> str:
        """Whichever handle is closer to ``x`` (ties favor 'low')."""
        return "low" if abs(x - self._handle_x(self._low)) <= abs(
            x - self._handle_x(self._high)
        ) else "high"

    def _set_active_from_x(self, x: float) -> None:
        v = self._value_from_x(x)
        if self._active == "low":
            self.set_values(min(v, self._high), self._high)
        elif self._active == "high":
            self.set_values(self._low, max(v, self._low))

    # -- sizing ------------------------------------------------------------

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(200, _WIDGET_H)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(80, _WIDGET_H)

    # -- interaction -------------------------------------------------------

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            x = event.position().x()
            self._active = self._nearest_handle(x)
            self._set_active_from_x(x)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._active is not None:
            self._set_active_from_x(event.position().x())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if self._active is not None and event.button() == Qt.MouseButton.LeftButton:
            self._active = None
            self.update()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def enterEvent(self, event) -> None:  # noqa: N802
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: N802
        super().leaveEvent(event)
        self.update()

    # -- painting ----------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        theme = ThemeManager.instance()
        enabled = self.isEnabled()
        track = self._track_rect()
        cy = track.center().y()
        r = _TRACK_H / 2.0
        lx, hx = self._handle_x(self._low), self._handle_x(self._high)

        active = theme.color(ColorRole.PRIMARY)
        inactive = theme.color(ColorRole.SURFACE_CONTAINER_HIGHEST)
        handle_color = theme.color(ColorRole.PRIMARY)
        if not enabled:
            active = theme.color(ColorRole.ON_SURFACE)
            active.setAlphaF(_DISABLED_OPACITY)
            inactive = theme.color(ColorRole.ON_SURFACE)
            inactive.setAlphaF(0.12)
            handle_color = theme.color(ColorRole.ON_SURFACE)
            handle_color.setAlphaF(_DISABLED_OPACITY)

        painter.setPen(Qt.PenStyle.NoPen)
        # Inactive track (full width), then the active span between handles.
        painter.setBrush(inactive)
        painter.drawRoundedRect(
            QRectF(track.left(), track.top(), track.width(), _TRACK_H), r, r
        )
        painter.setBrush(active)
        painter.drawRoundedRect(QRectF(lx, track.top(), hx - lx, _TRACK_H), r, r)

        # Handle state layers (hover/press) + handles.
        for which, x in (("low", lx), ("high", hx)):
            if enabled and (self._active == which or self.underMouse()):
                layer = StateLayer.PRESSED if self._active == which else StateLayer.HOVER
                sl = theme.color(ColorRole.PRIMARY)
                sl.setAlphaF(layer.opacity)
                painter.setBrush(sl)
                painter.drawEllipse(QPointF(x, cy), _STATE_LAYER / 2.0, _STATE_LAYER / 2.0)
            painter.setBrush(handle_color)
            painter.drawEllipse(QPointF(x, cy), _HANDLE / 2.0, _HANDLE / 2.0)

        if self._active is not None and enabled:
            value = self._low if self._active == "low" else self._high
            self._paint_value_label(painter, self._handle_x(value), cy, value, theme)

    def _paint_value_label(self, painter, hx, cy, value, theme) -> None:
        text = str(value)
        painter.setFont(self._label_font)
        tw = QFontMetrics(self._label_font).horizontalAdvance(text) + 16
        th = 28
        rect = QRectF(hx - tw / 2.0, cy - _HANDLE / 2.0 - th - 4, tw, th)
        painter.setBrush(theme.color(ColorRole.PRIMARY))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, th / 2.0, th / 2.0)
        painter.setPen(theme.color(ColorRole.ON_PRIMARY))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)


__all__ = ["MdRangeSlider"]
