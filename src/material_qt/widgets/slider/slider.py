"""Material 3 slider for QtWidgets.

Ports Material Web's ``md-slider`` (single-value). A 4px track (active
``primary`` / inactive ``surface-container-highest``) with a 20px ``primary``
handle, a 40px handle state layer on hover/press, an optional value-label bubble
shown while interacting, and discrete tick marks when ``step`` is set with
``ticks=True``. Built on :class:`QAbstractSlider` so ``minimum``/``maximum``/
``value``/``valueChanged`` and keyboard stepping work as standard.

Range (two-handle) sliders are not yet implemented; see the package roadmap.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QFontMetrics, QPainter
from PySide6.QtWidgets import QAbstractSlider, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...tokens.color import ColorRole
from ...tokens.typography import TypescaleRole, spec_for
from ...core.typography_util import font_for
from ...tokens.state import StateLayer
from ...theme.theme_manager import ThemeManager

_TRACK_H = 4
_HANDLE = 20
_STATE_LAYER = 40
_BAND = 40  # vertical band housing the track, handle, and state layer
# Horizontal padding so the 40px state layer never clips at the track ends.
_MARGIN = _STATE_LAYER / 2.0
_LABEL_H = 28
_LABEL_GAP = 4
_DISABLED_OPACITY = 0.38


class MdSlider(MaterialWidgetMixin, QAbstractSlider):
    """A Material 3 single-value slider."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        minimum: int = 0,
        maximum: int = 100,
        value: int = 0,
        step: int = 0,
        ticks: bool = False,
        labeled: bool = False,
    ) -> None:
        super().__init__(parent)
        self._labeled = labeled
        self.setOrientation(Qt.Orientation.Horizontal)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)
        self._show_ticks = bool(ticks) and step > 0
        if step > 0:
            self.setSingleStep(step)
            self.setPageStep(step)
        self._dragging = False
        self._init_material(shape=None, ripple=False, focus_ring=False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self._label_font = font_for(spec_for(TypescaleRole.LABEL_LARGE))

    # -- geometry ----------------------------------------------------------

    def _reserve(self) -> float:
        """Vertical space reserved above the band for the value label."""
        return (_LABEL_H + _LABEL_GAP) if self._labeled else 0.0

    def _track_rect(self) -> QRectF:
        cy = self._reserve() + _BAND / 2.0
        return QRectF(
            _MARGIN, cy - _TRACK_H / 2.0, self.width() - 2 * _MARGIN, _TRACK_H
        )

    def _value_fraction(self) -> float:
        span = self.maximum() - self.minimum()
        if span <= 0:
            return 0.0
        return (self.value() - self.minimum()) / span

    def _handle_x(self) -> float:
        track = self._track_rect()
        return track.left() + track.width() * self._value_fraction()

    def _value_from_x(self, x: float) -> int:
        track = self._track_rect()
        if track.width() <= 0:
            return self.minimum()
        f = (x - track.left()) / track.width()
        f = max(0.0, min(1.0, f))
        span = self.maximum() - self.minimum()
        raw = self.minimum() + f * span
        step = self.singleStep()
        if step > 0:
            raw = self.minimum() + round((raw - self.minimum()) / step) * step
        return int(round(max(self.minimum(), min(self.maximum(), raw))))

    # -- sizing ------------------------------------------------------------

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(200, int(_BAND + self._reserve()))

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(80, int(_BAND + self._reserve()))

    # -- interaction -------------------------------------------------------

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            self._dragging = True
            self.setSliderDown(True)
            self.setValue(self._value_from_x(event.position().x()))
            self.update()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._dragging:
            self.setValue(self._value_from_x(event.position().x()))
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if self._dragging and event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.setSliderDown(False)
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

    def sliderChange(self, change) -> None:  # noqa: N802
        super().sliderChange(change)
        self.update()

    # -- painting ----------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        theme = ThemeManager.instance()
        enabled = self.isEnabled()
        track = self._track_rect()
        hx = self._handle_x()
        cy = track.center().y()
        r = _TRACK_H / 2.0

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
        # Inactive track (right of handle).
        painter.setBrush(inactive)
        painter.drawRoundedRect(
            QRectF(hx, track.top(), track.right() - hx, _TRACK_H), r, r
        )
        # Active track (left of handle).
        painter.setBrush(active)
        painter.drawRoundedRect(
            QRectF(track.left(), track.top(), hx - track.left(), _TRACK_H), r, r
        )

        # Tick marks (discrete).
        if self._show_ticks and self.singleStep() > 0:
            span = self.maximum() - self.minimum()
            n = span // self.singleStep()
            for i in range(n + 1):
                tx = track.left() + track.width() * (i / n if n else 0)
                on_active = tx <= hx
                tick = theme.color(
                    ColorRole.ON_PRIMARY if on_active else ColorRole.OUTLINE_VARIANT
                )
                painter.setBrush(tick)
                painter.drawEllipse(QPointF(tx, cy), 1.0, 1.0)

        # Handle state layer (hover/press).
        layer = None
        if enabled:
            if self._dragging:
                layer = StateLayer.PRESSED
            elif self.underMouse() or self.hasFocus():
                layer = StateLayer.HOVER if self.underMouse() else StateLayer.FOCUS
        if layer is not None:
            sl = theme.color(ColorRole.PRIMARY)
            sl.setAlphaF(layer.opacity)
            painter.setBrush(sl)
            rr = _STATE_LAYER / 2.0
            painter.drawEllipse(QPointF(hx, cy), rr, rr)

        # Handle.
        painter.setBrush(handle_color)
        painter.drawEllipse(QPointF(hx, cy), _HANDLE / 2.0, _HANDLE / 2.0)

        # Value label while interacting (opt-in via ``labeled``).
        if self._dragging and enabled and self._labeled:
            self._paint_value_label(painter, hx, cy, theme)

    def _paint_value_label(self, painter: QPainter, hx: float, cy: float, theme) -> None:
        text = str(self.value())
        painter.setFont(self._label_font)
        metrics = QFontMetrics(self._label_font)
        tw = metrics.horizontalAdvance(text) + 16
        th = _LABEL_H
        bx = hx - tw / 2.0
        by = cy - _HANDLE / 2.0 - th - _LABEL_GAP
        rect = QRectF(bx, by, tw, th)
        painter.setBrush(theme.color(ColorRole.PRIMARY))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, th / 2.0, th / 2.0)
        painter.setPen(theme.color(ColorRole.ON_PRIMARY))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)


__all__ = ["MdSlider"]
