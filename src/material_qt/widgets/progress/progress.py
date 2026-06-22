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
                 indeterminate: bool = False,
                 color_role: ColorRole = ColorRole.PRIMARY,
                 track_role: ColorRole = ColorRole.SURFACE_CONTAINER_HIGHEST) -> None:
        super().__init__(parent)
        self._value = max(0.0, min(1.0, value))
        self._indeterminate = bool(indeterminate)
        self._color_role = color_role
        self._track_role = track_role
        self._phase = 0.0
        self._anim: QVariantAnimation | None = None
        self._init_material(shape=None, ripple=False, focus_ring=False)
        if self._indeterminate:
            self._start_anim()

    # -- properties --------------------------------------------------------

    @property
    def color_role(self) -> ColorRole:
        """Theme role of the active indicator (Flutter ``color``/``valueColor``)."""
        return self._color_role

    def set_color_role(self, role: ColorRole) -> None:
        self._color_role = role
        self.update()

    @property
    def track_role(self) -> ColorRole:
        """Theme role of the track (Flutter ``backgroundColor``)."""
        return self._track_role

    def set_track_role(self, role: ColorRole) -> None:
        self._track_role = role
        self.update()

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
    """A linear progress bar (determinate or indeterminate).

    ``min_height`` is the bar thickness (Flutter ``minHeight``) and
    ``border_radius`` the corner radius (Flutter ``borderRadius``); the latter
    defaults to half the thickness, giving a fully rounded bar.
    """

    def __init__(self, parent: QWidget | None = None, *, value: float = 0.0,
                 indeterminate: bool = False,
                 color_role: ColorRole = ColorRole.PRIMARY,
                 track_role: ColorRole = ColorRole.SURFACE_CONTAINER_HIGHEST,
                 min_height: float = _THICK,
                 border_radius: float | None = None) -> None:
        self._min_height = float(min_height)
        self._border_radius = border_radius
        super().__init__(parent, value=value, indeterminate=indeterminate,
                         color_role=color_role, track_role=track_role)

    @property
    def min_height(self) -> float:
        """Bar thickness (Flutter ``minHeight``)."""
        return self._min_height

    def set_min_height(self, value: float) -> None:
        self._min_height = float(value)
        self.updateGeometry()
        self.update()

    @property
    def border_radius(self) -> float:
        """Corner radius; defaults to half the thickness when unset."""
        return self._border_radius if self._border_radius is not None else self._min_height / 2.0

    def set_border_radius(self, value: float | None) -> None:
        self._border_radius = None if value is None else float(value)
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(240, round(self._min_height))

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(_LINEAR_MIN_W, round(self._min_height))

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        theme = ThemeManager.instance()
        w = self.width()
        thick = self._min_height
        cy = self.height() / 2.0
        track = QRectF(0, cy - thick / 2.0, w, thick)
        r = self.border_radius
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(theme.color(self._track_role))
        painter.drawRoundedRect(track, r, r)

        painter.setBrush(theme.color(self._color_role))
        if self._indeterminate:
            # A bar of ~40% width sweeping left->right.
            bar_w = w * 0.4
            x = (w + bar_w) * self._phase - bar_w
            x0 = max(0.0, x)
            x1 = min(w, x + bar_w)
            if x1 > x0:
                painter.drawRoundedRect(QRectF(x0, track.top(), x1 - x0, thick), r, r)
        else:
            painter.drawRoundedRect(QRectF(0, track.top(), w * self._value, thick), r, r)


class MdCircularProgress(_ProgressBase):
    """A circular progress ring (determinate or indeterminate)."""

    def __init__(self, parent: QWidget | None = None, *, value: float = 0.0,
                 indeterminate: bool = False, size: int = _CIRCULAR_SIZE,
                 color_role: ColorRole = ColorRole.PRIMARY,
                 track_role: ColorRole = ColorRole.SURFACE_CONTAINER_HIGHEST,
                 stroke_width: float = _THICK) -> None:
        self._size = int(size)
        self._stroke_width = float(stroke_width)
        super().__init__(parent, value=value, indeterminate=indeterminate,
                         color_role=color_role, track_role=track_role)

    @property
    def stroke_width(self) -> float:
        """Ring thickness (Flutter ``strokeWidth``)."""
        return self._stroke_width

    def set_stroke_width(self, value: float) -> None:
        self._stroke_width = float(value)
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(self._size, self._size)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return self.sizeHint()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        theme = ThemeManager.instance()
        sw = self._stroke_width
        margin = sw / 2.0 + 1
        box = QRectF(
            margin, margin,
            self.width() - 2 * margin, self.height() - 2 * margin,
        )

        track_pen = QPen(theme.color(self._track_role))
        track_pen.setWidthF(sw)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(box, 0, 360 * 16)

        pen = QPen(theme.color(self._color_role))
        pen.setWidthF(sw)
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
