"""Material 3 progress indicators for QtWidgets.

Ports Material Web's ``progress/`` — :class:`MdLinearProgress` and
:class:`MdCircularProgress`, each in determinate (``value`` 0..1) and
indeterminate (continuous animation) modes. Active indicator is ``primary`` on a
``surface-container-highest`` track, 4px thick. Indeterminate animations loop via
a :class:`QVariantAnimation` that is stopped when the widget is hidden or
destroyed, so no timer leaks after teardown.
"""

from __future__ import annotations

import math

from PySide6.QtCore import QRectF, QSize, Qt, QVariantAnimation
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...tokens.color import ColorRole
from ...theme.theme_manager import ThemeManager

_THICK = 4
_CIRCULAR_SIZE = 48
_LINEAR_MIN_W = 80
_INDETERMINATE_MS = 1600


class _ProgressBase(MaterialWidgetMixin, QWidget):
    def __init__(self, parent: QWidget | None = None, *, value: float = 0.0,
                 indeterminate: bool = False) -> None:
        super().__init__(parent)
        self._value = max(0.0, min(1.0, value))
        self._indeterminate = bool(indeterminate)
        self._phase = 0.0
        self._anim: QVariantAnimation | None = None
        self._init_material(shape=None, ripple=False, focus_ring=False)
        if self._indeterminate:
            self._start_anim()

    # -- properties --------------------------------------------------------

    @property
    def value(self) -> float:
        return self._value

    def set_value(self, value: float) -> None:
        self._value = max(0.0, min(1.0, float(value)))
        self.update()

    @property
    def indeterminate(self) -> bool:
        return self._indeterminate

    def set_indeterminate(self, value: bool) -> None:
        value = bool(value)
        if value == self._indeterminate:
            return
        self._indeterminate = value
        if value:
            self._start_anim()
        else:
            self._stop_anim()
        self.update()

    # -- animation ---------------------------------------------------------

    def _start_anim(self) -> None:
        from ...core.motion import MOTION_ENABLED

        if not MOTION_ENABLED or self._anim is not None:
            return
        anim = QVariantAnimation(self)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(_INDETERMINATE_MS)
        anim.setLoopCount(-1)
        anim.valueChanged.connect(self._set_phase)
        anim.start()
        self._anim = anim

    def _stop_anim(self) -> None:
        if self._anim is not None:
            self._anim.stop()
            self._anim.deleteLater()
            self._anim = None

    def _set_phase(self, value) -> None:
        self._phase = float(value)
        self.update()

    def hideEvent(self, event) -> None:  # noqa: N802
        self._stop_anim()
        super().hideEvent(event)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        if self._indeterminate:
            self._start_anim()


class MdLinearProgress(_ProgressBase):
    """A 4px linear progress bar (determinate or indeterminate)."""

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(240, _THICK)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(_LINEAR_MIN_W, _THICK)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        theme = ThemeManager.instance()
        w = self.width()
        cy = self.height() / 2.0
        track = QRectF(0, cy - _THICK / 2.0, w, _THICK)
        r = _THICK / 2.0
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(theme.color(ColorRole.SURFACE_CONTAINER_HIGHEST))
        painter.drawRoundedRect(track, r, r)

        painter.setBrush(theme.color(ColorRole.PRIMARY))
        if self._indeterminate:
            # A bar of ~40% width sweeping left->right.
            bar_w = w * 0.4
            x = (w + bar_w) * self._phase - bar_w
            x0 = max(0.0, x)
            x1 = min(w, x + bar_w)
            if x1 > x0:
                painter.drawRoundedRect(QRectF(x0, track.top(), x1 - x0, _THICK), r, r)
        else:
            painter.drawRoundedRect(QRectF(0, track.top(), w * self._value, _THICK), r, r)


class MdCircularProgress(_ProgressBase):
    """A circular progress ring (determinate or indeterminate)."""

    def __init__(self, parent: QWidget | None = None, *, value: float = 0.0,
                 indeterminate: bool = False, size: int = _CIRCULAR_SIZE) -> None:
        self._size = int(size)
        super().__init__(parent, value=value, indeterminate=indeterminate)

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(self._size, self._size)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return self.sizeHint()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        theme = ThemeManager.instance()
        margin = _THICK / 2.0 + 1
        box = QRectF(
            margin, margin,
            self.width() - 2 * margin, self.height() - 2 * margin,
        )

        track_pen = QPen(theme.color(ColorRole.SURFACE_CONTAINER_HIGHEST))
        track_pen.setWidthF(_THICK)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(box, 0, 360 * 16)

        pen = QPen(theme.color(ColorRole.PRIMARY))
        pen.setWidthF(_THICK)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        if self._indeterminate:
            # Rotating arc whose span breathes between ~20 and ~300 degrees.
            start = -self._phase * 360.0 * 2.0
            span = 60.0 + 240.0 * abs(math.sin(self._phase * math.pi))
            painter.drawArc(box, int(start * 16), int(-span * 16))
        else:
            # Determinate: start at 12 o'clock, sweep clockwise.
            painter.drawArc(box, 90 * 16, int(-self._value * 360 * 16))


__all__ = ["MdCircularProgress", "MdLinearProgress"]
