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

import math

from PySide6.QtCore import QEvent, QObject, Property, Qt, Signal
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


def weighted_geometry(
    p: float, n: int, weights: list[int], width: float
) -> list[tuple[int, float, float]]:
    """Geometry for a weighted (multi-browse / hero) carousel at scroll ``p``.

    ``weights`` give the relative widths of the visible slots (e.g. ``[3, 2, 1]``
    => the leading item fills 3/6 of ``width``). ``p`` is the continuous leading
    index: at integer ``p == m`` item ``m`` fills slot 0, item ``m+1`` slot 1,
    etc.; fractional ``p`` linearly interpolates between those two tilings. Each
    item grows toward the leading (largest) slot and shrinks out at the edges.

    Returns ``(index, left, width)`` for every item wide enough to show. The
    widths always sum to ``width`` (the construction lerps between two exact
    tilings), so items tile with no gaps or overlaps.
    """
    k = len(weights)
    s = sum(weights)
    sw = [width * w / s for w in weights]
    sl = [0.0] * k
    for j in range(1, k):
        sl[j] = sl[j - 1] + sw[j - 1]

    def slot(j: int) -> tuple[float, float]:
        if j < 0:
            return (0.0, 0.0)  # collapsed off the leading (left) edge
        if j >= k:
            return (float(width), 0.0)  # collapsed off the trailing (right) edge
        return (sl[j], sw[j])

    m = math.floor(p)
    f = p - m
    out: list[tuple[int, float, float]] = []
    for j in range(0, k + 1):
        i = m + j
        if i < 0 or i >= n:
            continue
        l0, w0 = slot(j)
        l1, w1 = slot(j - 1)
        left = l0 + (l1 - l0) * f
        w = w0 + (w1 - w0) * f
        if w >= 1.0:
            out.append((i, left, w))
    return out


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


_FLEX_COLORS = [
    (ColorRole.PRIMARY_CONTAINER, ColorRole.ON_PRIMARY_CONTAINER),
    (ColorRole.SECONDARY_CONTAINER, ColorRole.ON_SECONDARY_CONTAINER),
    (ColorRole.TERTIARY_CONTAINER, ColorRole.ON_TERTIARY_CONTAINER),
]


class _FlexTile(MaterialWidgetMixin, QWidget):
    """A variable-width carousel tile, positioned by the weighted carousel.

    Transparent to mouse events so the carousel receives the drag (weighted
    tiles therefore have no ripple).
    """

    def __init__(self, label: str, index: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._container, self._fg = _FLEX_COLORS[index % len(_FLEX_COLORS)]
        self._init_material(
            shape=ShapeScale.EXTRA_LARGE,
            ripple=False,
            focus_ring=False,
            surface_role=self._container,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        self._label = QLabel(label)
        self._label.setFont(font_for_role(TypescaleRole.TITLE_MEDIUM))
        lay.addStretch(1)
        lay.addWidget(self._label)
        self._restyle()
        ThemeManager.instance().themeChanged.connect(self._restyle)

    def _restyle(self) -> None:
        self._label.setStyleSheet(
            f"color: {ThemeManager.instance().color(self._fg).name()};"
        )

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


class MdWeightedCarousel(QWidget):
    """A Material 3 weighted (multi-browse / hero) carousel.

    Items resize as they scroll: ``weights`` defines the visible slot widths
    (e.g. ``[3, 2, 1]`` multi-browse, ``[6, 1]`` hero). Drag/swipe or wheel to
    scroll; releases snap so an item fills the leading slot. ``indexChanged(int)``
    reports the leading item and ``itemTapped(int)`` fires on a click (vs drag).

    Layout is driven by :func:`weighted_geometry` against a continuous scroll
    value ``p``; children are positioned manually (no QLayout), so this hosts no
    scroll area. Scroll is clamped so the viewport stays full (the last item ends
    in the smallest slot rather than scrolling into blank space).
    """

    indexChanged = Signal(int)  # noqa: N815  (Qt-style signal name)
    itemTapped = Signal(int)  # noqa: N815

    _PAD_H = 16
    _PAD_V = 8
    _DRAG_THRESHOLD = 4

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        weights: list[int] = [3, 2, 1],  # noqa: B006  (read-only default)
    ) -> None:
        super().__init__(parent)
        self._weights = list(weights)
        self._items: list[QWidget] = []
        self._p = 0.0
        self._index = 0
        self._anim = None
        self._press_x = 0.0
        self._press_p = 0.0
        self._moved = False
        self.setFixedHeight(_ITEM_H + 2 * self._PAD_V)
        self.setMouseTracking(True)

    # -- items -------------------------------------------------------------

    def add_item(self, widget: QWidget) -> None:
        widget.setParent(self)
        self._items.append(widget)
        self._relayout()

    def add_tile(self, label: str) -> _FlexTile:
        tile = _FlexTile(label, len(self._items))
        self.add_item(tile)
        return tile

    def count(self) -> int:
        return len(self._items)

    @property
    def current_index(self) -> int:
        return self._index

    def _max_p(self) -> float:
        # Keep the viewport full: the last item settles in the smallest slot.
        return float(max(0, len(self._items) - len(self._weights)))

    # -- p property (drives layout; animatable) ----------------------------

    def get_p(self) -> float:
        return self._p

    def set_p(self, value) -> None:
        self._p = max(0.0, min(float(value), self._max_p()))
        self._relayout()
        idx = round(self._p)
        if idx != self._index:
            self._index = idx
            self.indexChanged.emit(idx)

    p = Property(float, get_p, set_p)

    # -- layout ------------------------------------------------------------

    def _content_width(self) -> float:
        return max(1.0, self.width() - 2 * self._PAD_H)

    def _relayout(self) -> None:
        geoms = weighted_geometry(
            self._p, len(self._items), self._weights, self._content_width()
        )
        shown = set()
        h = self.height() - 2 * self._PAD_V
        for i, left, w in geoms:
            item = self._items[i]
            item.setGeometry(
                int(left) + self._PAD_H, self._PAD_V, max(1, int(w) - _GAP), h
            )
            item.show()
            item.raise_()
            shown.add(i)
        for j, item in enumerate(self._items):
            if j not in shown:
                item.hide()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._relayout()

    # -- input -------------------------------------------------------------

    def _leading_slot_width(self) -> float:
        return self._content_width() * self._weights[0] / sum(self._weights)

    def _stop_anim(self) -> None:
        # animate() uses DeleteWhenStopped, so a finished animation's C++ object
        # is already gone even though we still hold the wrapper — guard the stop.
        if self._anim is not None:
            try:
                self._anim.stop()
            except RuntimeError:
                pass
            self._anim = None

    def _animate_to(self, index: float) -> None:
        target = max(0.0, min(float(index), self._max_p()))
        self._stop_anim()
        self._anim = animate(self, b"p", target, duration=Duration.SHORT4,
                             easing=Easing.EMPHASIZED, start=self._p,
                             on_finished=self._clear_anim)

    def _clear_anim(self) -> None:
        self._anim = None

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._stop_anim()
            self._press_x = event.position().x()
            self._press_p = self._p
            self._moved = False

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if event.buttons() & Qt.MouseButton.LeftButton:
            dx = event.position().x() - self._press_x
            if abs(dx) > self._DRAG_THRESHOLD:
                self._moved = True
            self.set_p(self._press_p - dx / self._leading_slot_width())

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            return
        if self._moved:
            self._animate_to(round(self._p))
        else:
            i = self._item_at(event.position().x())
            if i is not None:
                self.itemTapped.emit(i)

    def _item_at(self, x: float) -> int | None:
        for i, item in enumerate(self._items):
            if not item.isHidden() and item.x() <= x <= item.x() + item.width():
                return i
        return None

    def wheelEvent(self, event) -> None:  # noqa: N802
        delta = event.angleDelta().y() or event.angleDelta().x()
        self._animate_to(round(self._p) + (1 if delta < 0 else -1))


__all__ = ["MdCarousel", "MdWeightedCarousel", "weighted_geometry"]
