"""Material 3 loading indicator (Expressive) for QtWidgets.

Ports the Material 3 Expressive loading indicator: an indeterminate activity
indicator whose active shape is a looping morph through a sequence of Material 3
shapes while rotating (distinct from the circular progress spinner). Best for
short processes (200ms-5s).

This scaffold approximates the morph by rotating a filled ``primary`` rounded
"cookie" shape whose number of lobes cycles through a small sequence over the
loop. The true spring-based morph between the seven canonical M3 shapes is
deferred. ``start()`` / ``stop()`` control the animation; ``is_running``
reports state. The ``t`` property (0..1) is drivable for testing.
"""

from __future__ import annotations

import math

from PySide6.QtCore import Property, QSize, Qt, QVariantAnimation
from PySide6.QtGui import QPainter, QPainterPath
from PySide6.QtWidgets import QWidget

from ...core.motion import MOTION_ENABLED
from ...tokens.color import ColorRole
from ...theme.theme_manager import ThemeManager

_SIZE = 48
# Lobe counts to morph between over one loop (approximating the M3 shape set).
_LOBES = [4, 7, 5, 6, 8]


class MdLoadingIndicator(QWidget):
    """An indeterminate Material 3 Expressive loading indicator."""

    def __init__(self, parent: QWidget | None = None, *, size: int = _SIZE) -> None:
        super().__init__(parent)
        self._size = size
        self._t = 0.0
        self.setFixedSize(size, size)
        self._anim = QVariantAnimation(self)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setDuration(4000)
        self._anim.setLoopCount(-1)  # loop forever — a one-shot would freeze
        self._anim.valueChanged.connect(self._set_t)
        ThemeManager.instance().themeChanged.connect(self.update)
        # Run whenever visible (unless the user calls stop()). The animation is
        # started/stopped from show/hide events — never in the constructor — so
        # a never-shown indicator does not tick at frame rate forever.
        self._active = True

    # -- drivable state (testable) -----------------------------------------

    def get_t(self) -> float:
        return self._t

    def set_t(self, value) -> None:
        self._t = float(value) % 1.0
        self.update()

    t = Property(float, get_t, set_t)

    @property
    def is_running(self) -> bool:
        return self._anim.state() == QVariantAnimation.State.Running

    def start(self) -> None:
        """Run the animation; while hidden it stays parked until shown."""
        self._active = True
        if MOTION_ENABLED and self.isVisible():
            self._anim.start()

    def stop(self) -> None:
        """Stop the animation; it will not restart on show until start()."""
        self._active = False
        self._anim.stop()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        if self._active:
            self.start()

    def hideEvent(self, event) -> None:  # noqa: N802
        # Pause (don't clear _active) so re-showing resumes automatically.
        self._anim.stop()
        super().hideEvent(event)

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(self._size, self._size)

    # -- painting ----------------------------------------------------------

    def _shape_path(self, cx: float, cy: float, r: float, lobes: int,
                    depth: float) -> QPainterPath:
        """A rounded "cookie" — a circle radius-modulated by ``lobes`` bumps."""
        path = QPainterPath()
        steps = max(64, lobes * 16)
        for i in range(steps + 1):
            a = 2 * math.pi * i / steps
            rad = r * (1.0 - depth + depth * (0.5 + 0.5 * math.cos(lobes * a)))
            x = cx + rad * math.cos(a)
            y = cy + rad * math.sin(a)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        path.closeSubpath()
        return path

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        cx, cy = self.width() / 2.0, self.height() / 2.0
        r = min(cx, cy) - 2

        # Cycle lobe count over the loop; rotate continuously.
        seg = self._t * len(_LOBES)
        lobes = _LOBES[int(seg) % len(_LOBES)]
        painter.translate(cx, cy)
        painter.rotate(self._t * 360.0)
        painter.translate(-cx, -cy)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(ThemeManager.instance().color(ColorRole.PRIMARY))
        painter.drawPath(self._shape_path(cx, cy, r, lobes, 0.18))

    def _set_t(self, value) -> None:
        self.set_t(value)


__all__ = ["MdLoadingIndicator"]
