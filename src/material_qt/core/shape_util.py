"""Shape utilities: rounded paths and dp/px conversions."""

from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainterPath

from ..tokens.shape import FULL_SENTINEL, CornerRadii

# Material tokens are authored in CSS px, which equal device-independent px.
# Qt's logical coordinate system is already DIP-based, so dp == px here.
_DP_PER_PX = 1.0


def dp(value: float) -> float:
    """Convert density-independent pixels to logical px (identity in Qt DIPs)."""
    return value * _DP_PER_PX


def px(value: float) -> float:
    """Convert logical px to dp (identity in Qt DIPs)."""
    return value / _DP_PER_PX


def resolve_radius(radius: float, rect: QRectF) -> float:
    """Resolve a corner radius for ``rect``, mapping the "full" sentinel.

    "full" (9999) becomes ``min(width, height) / 2`` (a pill/circle). Any radius
    is clamped so it never exceeds half the smaller dimension.
    """
    limit = min(rect.width(), rect.height()) / 2.0
    if radius >= FULL_SENTINEL:
        return limit
    return min(radius, limit)


def rounded_path(rect: QRectF, radii: CornerRadii) -> QPainterPath:
    """Build a closed rounded-rectangle path with per-corner radii.

    Corners are top-left, top-right, bottom-right, bottom-left. The "full"
    sentinel and over-large radii are resolved/clamped against ``rect``.
    """
    rect = QRectF(rect)
    tl = resolve_radius(radii.tl, rect)
    tr = resolve_radius(radii.tr, rect)
    br = resolve_radius(radii.br, rect)
    bl = resolve_radius(radii.bl, rect)

    x = rect.x()
    y = rect.y()
    w = rect.width()
    h = rect.height()

    path = QPainterPath()
    # Start after the top-left corner, go clockwise.
    path.moveTo(x + tl, y)
    path.lineTo(x + w - tr, y)
    if tr > 0:
        path.arcTo(x + w - 2 * tr, y, 2 * tr, 2 * tr, 90.0, -90.0)
    path.lineTo(x + w, y + h - br)
    if br > 0:
        path.arcTo(x + w - 2 * br, y + h - 2 * br, 2 * br, 2 * br, 0.0, -90.0)
    path.lineTo(x + bl, y + h)
    if bl > 0:
        path.arcTo(x, y + h - 2 * bl, 2 * bl, 2 * bl, 270.0, -90.0)
    path.lineTo(x, y + tl)
    if tl > 0:
        path.arcTo(x, y, 2 * tl, 2 * tl, 180.0, -90.0)
    path.closeSubpath()
    return path


__all__ = ["dp", "px", "resolve_radius", "rounded_path"]
