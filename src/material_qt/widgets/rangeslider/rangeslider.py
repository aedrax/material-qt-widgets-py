"""Material 3 range slider for QtWidgets.

Ports the Material 3 range (two-handle) slider (cf. Flutter's ``RangeSlider``):
a 4px track with the active span between the two ``primary`` handles filled
``primary`` and the rest ``surface-container-highest``, two 20px ``primary``
handles with a 40px state layer on hover/press, and value-label bubbles while
dragging. The handles cannot cross — the dragged handle stops at the other.

Unlike :class:`MdSlider` this is not a ``QAbstractSlider`` (which models a single
value); it exposes ``low``/``high`` and emits ``valuesChanged(low, high)``.

Keyboard: arrows/PageUp/PageDown/Home/End move the *focused* handle — the one
last pressed or dragged (``low`` until a handle is touched). Steps match
:class:`MdSlider`: one division interval when ``divisions`` is set, else
``step`` (1 when continuous); Left/Right mirror under right-to-left.
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
_BAND = 40  # vertical band housing the track, handles, and state layers
# Horizontal padding so the 40px state layer never clips at the track ends.
_MARGIN = _STATE_LAYER / 2.0
_LABEL_H = 28
_LABEL_GAP = 4
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
        labeled: bool = False,
        divisions: int = 0,
    ) -> None:
        super().__init__(parent)
        self._labeled = labeled
        self._min = minimum
        self._max = maximum
        self._step = step
        # ``divisions`` (Flutter semantics): N intervals → N+1 discrete stops,
        # snap interval ``(max-min)/N``. When > 0 it takes precedence over
        # ``step`` for snapping and shows tick marks.
        self._divisions = max(0, int(divisions))
        self._low = minimum
        self._high = maximum
        self._active: str | None = None  # 'low' | 'high' while dragging
        self._hover: str | None = None  # handle nearest the cursor
        self._focus_handle = "low"  # keyboard target: last pressed handle
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

    @property
    def divisions(self) -> int:
        """Number of discrete intervals (N → N+1 stops); 0 = continuous."""
        return self._divisions

    def set_divisions(self, divisions: int) -> None:
        """Set the number of discrete intervals and snap both handles.

        Flutter semantics: ``divisions = N`` yields ``N + 1`` evenly spaced
        stops. Setting this (> 0) shows tick marks and takes precedence over
        ``step`` when snapping.
        """
        self._divisions = max(0, int(divisions))
        self.set_values(self._low, self._high)
        self.update()

    def _snap(self, value: int) -> int:
        """Snap ``value`` to the nearest division stop (clamped to bounds)."""
        value = self._clamp(value)
        span = self._max - self._min
        if self._divisions > 0 and span > 0:
            interval = span / self._divisions
            idx = round((value - self._min) / interval)
            value = self._clamp(int(round(self._min + idx * interval)))
        return value

    def set_values(self, low: int, high: int) -> None:
        low, high = self._snap(low), self._snap(high)
        if low > high:
            low, high = high, low
        changed = (low, high) != (self._low, self._high)
        self._low, self._high = low, high
        if changed:
            self.valuesChanged.emit(low, high)
        self.update()

    # -- geometry ----------------------------------------------------------

    def _reserve(self) -> float:
        """Vertical space reserved above the band for the value label."""
        return (_LABEL_H + _LABEL_GAP) if self._labeled else 0.0

    def _track_rect(self) -> QRectF:
        cy = self._reserve() + _BAND / 2.0
        return QRectF(_MARGIN, cy - _TRACK_H / 2.0, self.width() - 2 * _MARGIN, _TRACK_H)

    def _fraction(self, value: int) -> float:
        span = self._max - self._min
        return 0.0 if span <= 0 else (value - self._min) / span

    def _handle_x(self, value: int) -> float:
        # Mirror under right-to-left (minimum at the right edge) so the
        # visuals agree with the mirrored arrow keys.
        track = self._track_rect()
        f = self._fraction(value)
        if self.isRightToLeft():
            f = 1.0 - f
        return track.left() + track.width() * f

    def _value_from_x(self, x: float) -> int:
        track = self._track_rect()
        if track.width() <= 0:
            return self._min
        f = max(0.0, min(1.0, (x - track.left()) / track.width()))
        if self.isRightToLeft():
            f = 1.0 - f
        raw = self._min + f * (self._max - self._min)
        if self._divisions > 0:
            return self._snap(int(round(raw)))
        if self._step > 0:
            raw = self._min + round((raw - self._min) / self._step) * self._step
        return self._clamp(int(round(raw)))

    def _nearest_handle(self, x: float) -> str:
        """Whichever handle is closer to ``x``.

        On a tie (typically coincident handles) pick the one that can move
        toward the press — 'high' when the press maps past the handles,
        'low' when it maps before them — so a range collapsed at either
        bound never gets stuck.
        """
        d_low = abs(x - self._handle_x(self._low))
        d_high = abs(x - self._handle_x(self._high))
        if d_low != d_high:
            return "low" if d_low < d_high else "high"
        return "high" if self._value_from_x(x) >= self._high else "low"

    def _set_active_from_x(self, x: float) -> None:
        v = self._value_from_x(x)
        if self._active == "low":
            self.set_values(min(v, self._high), self._high)
        elif self._active == "high":
            self.set_values(self._low, max(v, self._low))

    def _single_step(self) -> int:
        """One keyboard step: a division interval, else ``step``, else 1."""
        span = self._max - self._min
        if self._divisions > 0 and span > 0:
            return max(1, int(round(span / self._divisions)))
        return self._step if self._step > 0 else 1

    def _set_focused_value(self, value: int) -> None:
        """Move the keyboard-focused handle; handles cannot cross."""
        if self._focus_handle == "low":
            self.set_values(min(self._snap(value), self._high), self._high)
        else:
            self.set_values(self._low, max(self._snap(value), self._low))

    # -- sizing ------------------------------------------------------------

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(200, int(_BAND + self._reserve()))

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(80, int(_BAND + self._reserve()))

    # -- interaction -------------------------------------------------------

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            x = event.position().x()
            self._active = self._nearest_handle(x)
            self._focus_handle = self._active  # keyboard follows the pointer
            self._set_active_from_x(x)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._active is not None:
            self._set_active_from_x(event.position().x())
            event.accept()
            return
        hover = self._nearest_handle(event.position().x())
        if hover != self._hover:
            self._hover = hover
            self.update()
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
        self._hover = None
        super().leaveEvent(event)
        self.update()

    def keyPressEvent(self, event) -> None:  # noqa: N802
        # Step the focused handle (last pressed; 'low' initially). Steps
        # match MdSlider: page == single step; Left/Right mirror under
        # right-to-left; Home/End go to the extremes (stopping at the other
        # handle). ``set_values`` snaps and emits valuesChanged.
        key = event.key()
        step = self._single_step()
        value = self._low if self._focus_handle == "low" else self._high
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            add = (key == Qt.Key.Key_Right) != self.isRightToLeft()
            self._set_focused_value(value + (step if add else -step))
        elif key in (Qt.Key.Key_Up, Qt.Key.Key_PageUp):
            self._set_focused_value(value + step)
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_PageDown):
            self._set_focused_value(value - step)
        elif key == Qt.Key.Key_Home:
            self._set_focused_value(self._min)
        elif key == Qt.Key.Key_End:
            self._set_focused_value(self._max)
        else:
            super().keyPressEvent(event)
            return
        event.accept()

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
        # Inactive track (full width), then the active span between handles
        # (under right-to-left the low handle sits to the right of the high).
        span_l, span_r = min(lx, hx), max(lx, hx)
        painter.setBrush(inactive)
        painter.drawRoundedRect(
            QRectF(track.left(), track.top(), track.width(), _TRACK_H), r, r
        )
        painter.setBrush(active)
        painter.drawRoundedRect(
            QRectF(span_l, track.top(), span_r - span_l, _TRACK_H), r, r
        )

        # Tick marks (discrete) when ``divisions`` is set. Ticks inside the
        # active span use ``on-primary``; the rest use ``outline-variant``.
        if self._divisions > 0:
            for i in range(self._divisions + 1):
                tx = track.left() + track.width() * (i / self._divisions)
                on_active = span_l <= tx <= span_r
                tick = theme.color(
                    ColorRole.ON_PRIMARY if on_active else ColorRole.OUTLINE_VARIANT
                )
                painter.setBrush(tick)
                painter.drawEllipse(QPointF(tx, cy), 1.0, 1.0)

        # Handle state layers (press on the dragged handle, hover only on
        # the handle nearest the cursor) + handles.
        for which, x in (("low", lx), ("high", hx)):
            layer = None
            if enabled:
                if self._active == which:
                    layer = StateLayer.PRESSED
                elif self._active is None and self._hover == which and self.underMouse():
                    layer = StateLayer.HOVER
            if layer is not None:
                sl = theme.color(ColorRole.PRIMARY)
                sl.setAlphaF(layer.opacity)
                painter.setBrush(sl)
                painter.drawEllipse(QPointF(x, cy), _STATE_LAYER / 2.0, _STATE_LAYER / 2.0)
            painter.setBrush(handle_color)
            painter.drawEllipse(QPointF(x, cy), _HANDLE / 2.0, _HANDLE / 2.0)

        if self._active is not None and enabled and self._labeled:
            value = self._low if self._active == "low" else self._high
            self._paint_value_label(painter, self._handle_x(value), cy, value, theme)

    def _paint_value_label(self, painter, hx, cy, value, theme) -> None:
        text = str(value)
        painter.setFont(self._label_font)
        tw = QFontMetrics(self._label_font).horizontalAdvance(text) + 16
        th = _LABEL_H
        rect = QRectF(hx - tw / 2.0, cy - _HANDLE / 2.0 - th - _LABEL_GAP, tw, th)
        painter.setBrush(theme.color(ColorRole.PRIMARY))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, th / 2.0, th / 2.0)
        painter.setPen(theme.color(ColorRole.ON_PRIMARY))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)


__all__ = ["MdRangeSlider"]
