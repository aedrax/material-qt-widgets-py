"""Elevation rendering: a simple drop-shadow effect and a dual-shadow painter."""

from __future__ import annotations

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget

from ..tokens.color import ColorRole
from ..tokens.elevation import (
    ElevationLevel,
    ShadowSpec,
    ambient_shadow,
    key_shadow,
)
from ..theme.theme_manager import ThemeManager


def apply_elevation(
    widget: QWidget,
    level: ElevationLevel | int,
    *,
    color_role: ColorRole = ColorRole.SHADOW,
) -> QGraphicsDropShadowEffect | None:
    """Apply a simple single drop shadow to ``widget`` for ``level``.

    Uses the ambient shadow geometry (the larger, softer of the two) as a
    reasonable single-effect approximation. Level 0 removes any shadow effect.
    Returns the effect (or None at level 0). For higher fidelity, paint with
    :class:`ElevationPainter` instead.
    """
    level = ElevationLevel(int(level))
    if level == ElevationLevel.LEVEL0:
        widget.setGraphicsEffect(None)
        return None

    spec = ambient_shadow(level)
    color = ThemeManager.instance().color(color_role)
    color.setAlphaF(spec.opacity)

    effect = QGraphicsDropShadowEffect(widget)
    effect.setOffset(spec.dx, spec.dy)
    # QGraphicsDropShadowEffect blur radius roughly corresponds to 2x CSS blur.
    effect.setBlurRadius(max(spec.blur * 2.0, 1.0))
    effect.setColor(color)
    widget.setGraphicsEffect(effect)
    return effect


class ElevationPainter:
    """High-fidelity dual-shadow painter (key + ambient) matching Material.

    Draws both the key (umbra, opacity 0.3) and ambient (penumbra, opacity 0.15)
    shadows by stacking translucent rounded shapes; the shadow color is read
    from the active theme each paint.
    """

    def __init__(self, *, color_role: ColorRole = ColorRole.SHADOW) -> None:
        self.color_role = color_role

    def _draw_one(
        self, painter: QPainter, shape: QPainterPath, spec: ShadowSpec
    ) -> None:
        if spec.opacity <= 0 or (spec.blur == 0 and spec.dx == 0 and spec.dy == 0):
            return
        base = ThemeManager.instance().color(self.color_role)
        transparent = QColor(0, 0, 0, 0)
        translated = QPainterPath(shape)
        translated.translate(QPointF(spec.dx, spec.dy))
        # Approximate a Gaussian blur by stacking concentric strokes whose width
        # grows toward the blur edge while alpha falls off, so the union sums to
        # roughly the spec opacity at the shape edge.
        steps = max(1, int(round(spec.blur)) + 1)
        painter.setBrush(transparent)
        for i in range(1, steps + 1):
            frac = i / steps
            color = QColor(base)
            color.setAlphaF(min(spec.opacity * (1.0 - frac) + spec.opacity / steps, 1.0))
            pen = QPen(color)
            pen.setWidthF(max(spec.blur * frac + spec.spread, 0.5))
            painter.setPen(pen)
            painter.drawPath(translated)

    def paint(
        self,
        painter: QPainter,
        shape: QPainterPath,
        level: ElevationLevel | int,
    ) -> None:
        """Paint key + ambient shadows for ``level`` behind ``shape``."""
        level = ElevationLevel(int(level))
        if level == ElevationLevel.LEVEL0:
            return
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        # Ambient first (wider, fainter), then key on top (tighter, darker).
        self._draw_one(painter, shape, ambient_shadow(level))
        self._draw_one(painter, shape, key_shadow(level))
        painter.restore()


__all__ = ["ElevationPainter", "apply_elevation"]
