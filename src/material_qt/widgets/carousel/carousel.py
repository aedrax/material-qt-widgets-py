"""Material 3 carousel for QtWidgets.

Ports the Material 3 carousel / Flutter ``CarouselView`` (uncontained layout): a
horizontally scrollable row of equal-size items with extra-large rounded corners.
Unlike a plain scroll area it behaves like a carousel:

* **drag / swipe** to scroll (kinetic, via :class:`QScroller`) — works by
  dragging anywhere on the items, while a plain click still activates an item;
* **item snapping** — releasing a drag (or a wheel notch) settles on an item's
  leading edge;
* **wheel** advances one item at a time;
* ``indexChanged(int)`` reports the leading visible item (Flutter's
  ``onIndexChanged``).

Add arbitrary widgets with :meth:`add_item`, or labelled tiles with
:meth:`add_tile`. The weighted multi-browse / hero / full-screen layouts are
deferred. The carousel hosts its own horizontal scroll area, so it drops into a
vertically scrolling page without the two directions fighting.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QScroller,
    QVBoxLayout,
    QWidget,
)

from ...core.material_widget import MaterialWidgetMixin
from ...core.motion import animate
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.motion import Duration, Easing
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
    """A horizontally scrollable, snapping carousel of items."""

    indexChanged = Signal(int)  # noqa: N815  (Qt-style signal name)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._items: list[QWidget] = []
        self._positions: list[float] = []
        self._index = 0

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        # Drag/swipe + wheel are the affordances; no scrollbars.
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._strip = QWidget()
        self._row = QHBoxLayout(self._strip)
        self._row.setContentsMargins(0, 0, 0, 0)
        self._row.setSpacing(_GAP)
        self._row.addStretch(1)
        self._scroll.setWidget(self._strip)
        self.setFixedHeight(_ITEM_H + 16)
        outer.addWidget(self._scroll)

        # Kinetic drag-to-scroll over the items (a click still activates a tile).
        QScroller.grabGesture(
            self._scroll.viewport(),
            QScroller.ScrollerGestureType.LeftMouseButtonGesture,
        )
        self._scroller = QScroller.scroller(self._scroll.viewport())
        self._scroll.viewport().installEventFilter(self)  # wheel -> one item
        self._scroll.horizontalScrollBar().valueChanged.connect(self._on_scroll)

    # -- items -------------------------------------------------------------

    def add_item(self, widget: QWidget) -> None:
        self._row.insertWidget(self._row.count() - 1, widget)
        self._items.append(widget)
        self._update_snap()

    def add_tile(self, label: str) -> _Tile:
        tile = _Tile(label)
        self.add_item(tile)
        return tile

    def count(self) -> int:
        return len(self._items)

    @property
    def current_index(self) -> int:
        return self._index

    # -- snapping ----------------------------------------------------------

    @staticmethod
    def _item_width(item: QWidget) -> int:
        # Fixed-size items (e.g. tiles) carry their width in min == max, which
        # sizeHint() does not reflect; fall back to sizeHint otherwise.
        if item.minimumWidth() and item.minimumWidth() == item.maximumWidth():
            return item.minimumWidth()
        return max(item.sizeHint().width(), 0)

    def _update_snap(self) -> None:
        """Recompute item leading-edge positions (content coords) and register
        them as snap points."""
        positions: list[float] = []
        x = 0.0
        for item in self._items:
            positions.append(x)
            x += self._item_width(item) + _GAP
        self._positions = positions
        self._scroller.setSnapPositionsX(positions)

    def _nearest_index(self, value: float) -> int:
        if not self._positions:
            return 0
        return min(
            range(len(self._positions)),
            key=lambda i: abs(self._positions[i] - value),
        )

    def _on_scroll(self, value: int) -> None:
        idx = self._nearest_index(value)
        if idx != self._index:
            self._index = idx
            self.indexChanged.emit(idx)

    def _scroll_to_index(self, index: int) -> None:
        bar = self._scroll.horizontalScrollBar()
        index = max(0, min(index, len(self._positions) - 1))
        target = int(max(bar.minimum(), min(bar.maximum(), self._positions[index])))
        animate(bar, b"value", target, duration=Duration.SHORT4,
                easing=Easing.EMPHASIZED, start=bar.value())

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if obj is self._scroll.viewport() and event.type() == QEvent.Type.Wheel:
            delta = event.angleDelta().y() or event.angleDelta().x()
            step = 1 if delta < 0 else -1  # wheel-down advances to the next item
            self._scroll_to_index(self._index + step)
            return True
        return False


__all__ = ["MdCarousel"]
