"""Motion helpers: cached easing curves and one-shot property animations."""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QObject,
    QPointF,
    QPropertyAnimation,
)

from ..tokens.motion import Duration, Easing

MOTION_ENABLED = True
"""Module-level flag; when False, animations jump to their end value instantly."""

_curve_cache: dict[Easing, QEasingCurve] = {}


def easing_curve(easing: Easing) -> QEasingCurve:
    """Return a cached :class:`QEasingCurve` for a Material easing.

    Built as a ``BezierSpline`` with a single cubic segment from the token's
    two control points to (1, 1), matching CSS ``cubic-bezier``.
    """
    cached = _curve_cache.get(easing)
    if cached is not None:
        return cached
    (x1, y1), (x2, y2) = easing.control_points
    curve = QEasingCurve(QEasingCurve.Type.BezierSpline)
    curve.addCubicBezierSegment(QPointF(x1, y1), QPointF(x2, y2), QPointF(1.0, 1.0))
    _curve_cache[easing] = curve
    return curve


def duration_ms(duration: Duration | int) -> int:
    """Normalize a :class:`Duration` or raw int to milliseconds."""
    if isinstance(duration, Duration):
        return duration.ms
    return int(duration)


def animate(
    target: QObject,
    prop: bytes | str,
    end: object,
    *,
    duration: Duration | int,
    easing: Easing = Easing.STANDARD,
    start: object | None = None,
    on_finished: Callable[[], None] | None = None,
) -> QPropertyAnimation:
    """Create and start a one-shot :class:`QPropertyAnimation`.

    The animation deletes itself when stopped. When :data:`MOTION_ENABLED` is
    False it still runs but with zero duration so the end value is applied
    immediately (and ``on_finished`` still fires).
    """
    prop_name = prop.encode() if isinstance(prop, str) else prop
    anim = QPropertyAnimation(target, prop_name, target)
    anim.setDuration(duration_ms(duration) if MOTION_ENABLED else 0)
    anim.setEasingCurve(easing_curve(easing))
    if start is not None:
        anim.setStartValue(start)
    anim.setEndValue(end)
    if on_finished is not None:
        anim.finished.connect(on_finished)
    anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    return anim


__all__ = [
    "MOTION_ENABLED",
    "animate",
    "duration_ms",
    "easing_curve",
]
