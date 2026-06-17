"""Material 3 card (labs) for QtWidgets.

Ports Material Web's ``labs/card`` — a content container in three variants:
elevated (``surface-container-low`` + level1 shadow), filled
(``surface-container-highest``) and outlined (``surface`` + 1px
``outline-variant`` border). Corner-medium (12px) shape. Add child widgets to
the card's content layout via :meth:`add_widget` / :meth:`content_layout`.
"""

from __future__ import annotations

from enum import Enum

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...core.shape_util import rounded_path
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...tokens.shape import ShapeScale
from ...theme.theme_manager import ThemeManager

_OUTLINE_WIDTH = 1.0
_PAD = 16


class CardVariant(Enum):
    ELEVATED = "elevated"
    FILLED = "filled"
    OUTLINED = "outlined"


_SPEC = {
    # variant -> (surface role, elevation, outline role or None)
    CardVariant.ELEVATED: (ColorRole.SURFACE_CONTAINER_LOW, ElevationLevel.LEVEL1, None),
    CardVariant.FILLED: (
        ColorRole.SURFACE_CONTAINER_HIGHEST,
        ElevationLevel.LEVEL0,
        None,
    ),
    CardVariant.OUTLINED: (
        ColorRole.SURFACE,
        ElevationLevel.LEVEL0,
        ColorRole.OUTLINE_VARIANT,
    ),
}


class MdCard(MaterialWidgetMixin, QWidget):
    """A Material 3 card container."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        variant: CardVariant = CardVariant.ELEVATED,
    ) -> None:
        super().__init__(parent)
        surface, elevation, outline = _SPEC[variant]
        self._variant = variant
        self._outline_role = outline
        self._init_material(
            shape=ShapeScale.MEDIUM,
            elevation=elevation,
            ripple=False,
            focus_ring=False,
            surface_role=surface,
        )
        self._content = QVBoxLayout(self)
        self._content.setContentsMargins(_PAD, _PAD, _PAD, _PAD)
        self._content.setSpacing(8)

    @property
    def variant(self) -> CardVariant:
        return self._variant

    def content_layout(self) -> QVBoxLayout:
        return self._content

    def add_widget(self, widget: QWidget) -> None:
        self._content.addWidget(widget)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)
        if self._outline_role is not None:
            inset = _OUTLINE_WIDTH / 2.0
            rect = QRectF(self.rect()).adjusted(inset, inset, -inset, -inset)
            pen = QPen(ThemeManager.instance().color(self._outline_role))
            pen.setWidthF(_OUTLINE_WIDTH)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(rounded_path(rect, self._radii))


__all__ = ["CardVariant", "MdCard"]
