"""Paints a state-layer overlay: a role color at the active state opacity."""

from __future__ import annotations

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPainterPath

from ..tokens.color import ColorRole
from ..tokens.state import StateLayer
from ..theme.theme_manager import ThemeManager


class StateLayerPainter:
    """Composites a themed state layer over a host's shape.

    The color is read from the active :class:`ThemeManager` scheme each paint so
    theme switches require no per-instance invalidation beyond a repaint.
    """

    def __init__(self, *, color_role: ColorRole = ColorRole.ON_SURFACE) -> None:
        self.color_role = color_role

    def color_at(self, layer: StateLayer | None):
        """Return the role color at the layer's opacity (alpha applied)."""
        if layer is None:
            return None
        color = ThemeManager.instance().color(self.color_role)
        color.setAlphaF(layer.opacity)
        return color

    def paint(
        self,
        painter: QPainter,
        rect: QRectF,
        layer: StateLayer | None,
        *,
        clip: QPainterPath | None = None,
    ) -> None:
        """Fill ``rect`` (optionally clipped to ``clip``) with the state layer."""
        color = self.color_at(layer)
        if color is None:
            return
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        if clip is not None:
            painter.setClipPath(clip)
            painter.fillPath(clip, color)
        else:
            painter.fillRect(rect, color)
        painter.restore()


__all__ = ["StateLayerPainter"]
