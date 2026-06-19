"""Material 3 carousel for QtWidgets.

Ports the Material 3 carousel (uncontained layout): a horizontally scrollable row
of equal-size items with extra-large rounded corners. Add arbitrary widgets with
:meth:`add_item`, or labelled color tiles with :meth:`add_tile`. The other M3
layouts (multi-browse, hero, full-screen) are deferred.

The carousel hosts its own horizontal scroll area, so drop it into a vertically
scrolling page without the two scroll directions fighting.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.shape import ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager

_ITEM_W = 150
_ITEM_H = 180
_GAP = 8


class _Tile(MaterialWidgetMixin, QWidget):
    """A default carousel tile: a ``primary-container`` rounded panel + label."""

    def __init__(self, label: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_material(
            shape=ShapeScale.EXTRA_LARGE,
            ripple=True,
            focus_ring=False,
            surface_role=ColorRole.PRIMARY_CONTAINER,
            ripple_role=ColorRole.ON_PRIMARY_CONTAINER,
        )
        self.setFixedSize(_ITEM_W, _ITEM_H)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        self._label = QLabel(label)
        self._label.setFont(font_for_role(TypescaleRole.TITLE_MEDIUM))
        self._label.setWordWrap(True)
        lay.addStretch(1)
        lay.addWidget(self._label)
        self._restyle()
        ThemeManager.instance().themeChanged.connect(self._restyle)

    def _restyle(self) -> None:
        c = ThemeManager.instance().color(ColorRole.ON_PRIMARY_CONTAINER).name()
        self._label.setStyleSheet(f"color: {c};")

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


class MdCarousel(QWidget):
    """A horizontally scrollable carousel of items."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._items: list[QWidget] = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._strip = QWidget()
        self._row = QHBoxLayout(self._strip)
        self._row.setContentsMargins(0, 0, 0, 0)
        self._row.setSpacing(_GAP)
        self._row.addStretch(1)
        self._scroll.setWidget(self._strip)
        self.setFixedHeight(_ITEM_H + 16)
        outer.addWidget(self._scroll)

    def add_item(self, widget: QWidget) -> None:
        self._row.insertWidget(self._row.count() - 1, widget)
        self._items.append(widget)

    def add_tile(self, label: str) -> _Tile:
        tile = _Tile(label)
        self.add_item(tile)
        return tile

    def count(self) -> int:
        return len(self._items)


__all__ = ["MdCarousel"]
