"""Long-press support for Material button widgets.

Flutter's button family exposes an ``onLongPress`` callback. QtWidgets'
``QAbstractButton`` has no native long-press mechanism, so :class:`LongPressMixin`
adds an idiomatic ``longPressed`` Signal driven by a :class:`QTimer` armed on
press and cancelled on release, leave, or movement beyond a small slop radius.

Mix it in *before* the ``QAbstractButton`` base. The mixin owns
``mouseMoveEvent`` (its only job is the slop-cancel); call :meth:`_arm_long_press`
from ``mousePressEvent`` and, at the top of ``mouseReleaseEvent``, call
:meth:`_consume_long_press_release` — if it returns ``True`` a long press already
fired, so the widget must ``return`` *before* ``super().mouseReleaseEvent`` to
suppress the ``clicked`` signal (mirroring Flutter, where ``onLongPress``
suppresses ``onTap``). Also call :meth:`_cancel_long_press` from ``leaveEvent``.

The class declaring this mixin must also declare ``longPressed = Signal()`` (a
``Signal`` cannot be defined on a plain mixin and inherited reliably across the
QObject metaclass).
"""

from __future__ import annotations

from PySide6.QtCore import QPoint, QTimer

# Matches Android's default long-press timeout.
LONG_PRESS_MS = 500
# Movement (px) beyond which a press is treated as a drag, not a long press.
_SLOP = 12


class LongPressMixin:
    """Adds a ``longPressed`` Signal to a ``QAbstractButton`` subclass."""

    def _ensure_long_press_timer(self) -> QTimer:
        timer = getattr(self, "_long_press_timer", None)
        if timer is None:
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.setInterval(LONG_PRESS_MS)
            timer.timeout.connect(self._emit_long_press)
            self._long_press_timer = timer
            self._long_press_origin = QPoint()
            self._long_press_fired = False
        return timer

    def _arm_long_press(self, event) -> None:
        if not self.isEnabled():
            return
        timer = self._ensure_long_press_timer()
        self._long_press_origin = event.position().toPoint()
        self._long_press_fired = False
        timer.start()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        super().mouseMoveEvent(event)
        timer = getattr(self, "_long_press_timer", None)
        if timer is None or not timer.isActive():
            return
        delta = event.position().toPoint() - self._long_press_origin
        if abs(delta.x()) > _SLOP or abs(delta.y()) > _SLOP:
            timer.stop()

    def _cancel_long_press(self) -> None:
        timer = getattr(self, "_long_press_timer", None)
        if timer is not None:
            timer.stop()

    def _consume_long_press_release(self) -> bool:
        """Stop the timer; return ``True`` if a long press already fired.

        When ``True`` the caller must skip ``super().mouseReleaseEvent`` so the
        release does not also emit ``clicked`` — a long press suppresses the tap.
        The button's pressed (``down``) state is reset here so it doesn't stick.
        """
        self._cancel_long_press()
        if getattr(self, "_long_press_fired", False):
            self._long_press_fired = False
            self.setDown(False)
            return True
        return False

    def _emit_long_press(self) -> None:
        self._long_press_fired = True
        self.longPressed.emit()


__all__ = ["LONG_PRESS_MS", "LongPressMixin"]
