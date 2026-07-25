"""Material 3 reorderable list for QtWidgets.

Ports Flutter's ``ReorderableListView`` (``material/reorderable_list.dart``) — a
vertical list whose rows the user can drag to reorder. Each row carries a drag
handle (Flutter's desktop ``buildDefaultDragHandles``); pressing the handle and
dragging lifts the row, opens a gap at the prospective drop slot, and on release
commits the move.

Unlike Flutter, this widget **owns its order**: it applies the move internally
and emits :attr:`MdReorderableList.reordered` ``(old_index, new_index)`` purely
as a notification, where ``new_index`` is the item's *final resting index* in
the reordered list. There is no Flutter-style pre-removal ``newIndex`` to
correct for — a ``(2 → 5)`` signal means "the item now sits at index 5".

The drop slot is computed by the pure, unit-testable :func:`reorder_target_index`.

Deferred (vs Flutter): animated gap reflow (rows snap to their new slots
instantly rather than tweening), auto-scroll while dragging near an edge, and a
true drop shadow that extends past the list's top/bottom edges (an 8px gutter
cushions it; the lift uses a :class:`QGraphicsDropShadowEffect`).
"""

from __future__ import annotations

from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QHBoxLayout, QWidget

from ...core.elevation import apply_elevation
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...theme.theme_manager import ThemeManager
from ..icon import MdIcon

_MIN_ROW = 56
_GUTTER = 8  # vertical cushion so the lifted row's shadow isn't clipped
_DRAG_THRESHOLD = 4  # px of movement before a press becomes a drag


def reorder_target_index(
    centers: list[float], dragged_index: int, cursor_y: float
) -> int:
    """Final resting index for the dragged row whose centre sits at ``cursor_y``.

    ``centers`` are the resting centre-y of every row in current data order.
    The result uses post-removal semantics — it is the index the dragged item
    occupies *after* the move, in ``[0, len(centers) - 1]`` — so it can be
    handed straight to a list ``insert`` and emitted as-is. It equals the number
    of *other* rows whose centre lies above the cursor.
    """
    above = 0
    for i, c in enumerate(centers):
        if i == dragged_index:
            continue
        if c < cursor_y:
            above += 1
    return above


class _DragHandle(QWidget):
    """A grab-cursor handle that drives its owning list's drag lifecycle.

    Deliberately stores no reference to its row or list (they are derived from
    the parent chain): a Python back-reference to an ancestor makes the whole
    widget tree cyclic garbage, and the cycle collector may then destroy it at
    an arbitrary moment — including mid-paint, which crashes Qt.
    """

    def __init__(self, row: _Row) -> None:
        super().__init__(row)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setFixedSize(40, 40)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(
            MdIcon("drag_indicator", color_role=ColorRole.ON_SURFACE_VARIANT),
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

    def _row_and_list(self) -> tuple[_Row, MdReorderableList] | None:
        row = self.parentWidget()
        lst = row.parentWidget() if row is not None else None
        if isinstance(row, _Row) and isinstance(lst, MdReorderableList):
            return row, lst
        return None

    def mousePressEvent(self, event) -> None:  # noqa: N802
        owners = self._row_and_list()
        if owners is not None and event.button() == Qt.MouseButton.LeftButton:
            row, lst = owners
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            lst._begin_drag(row, event.globalPosition().toPoint())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        owners = self._row_and_list()
        if owners is not None:
            owners[1]._drag_move(event.globalPosition().toPoint())
        event.accept()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        owners = self._row_and_list()
        if owners is not None:
            owners[1]._end_drag()
        event.accept()


class _Row(QWidget):
    """Wraps a user content widget plus a trailing drag handle.

    In whole-row-drag mode (no handle) the row itself drives the list's drag
    lifecycle. The list is always derived from ``parentWidget()`` — see the
    no-back-references note on :class:`_DragHandle`.
    """

    def __init__(
        self, lst: MdReorderableList, content: QWidget, *, handle: bool
    ) -> None:
        super().__init__(lst)
        self._content = content
        self._whole_row_drag = not handle
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(content, 1)
        if handle:
            lay.addWidget(
                _DragHandle(self), alignment=Qt.AlignmentFlag.AlignVCenter
            )

    @property
    def content(self) -> QWidget:
        return self._content

    def _list(self) -> MdReorderableList | None:
        lst = self.parentWidget()
        return lst if isinstance(lst, MdReorderableList) else None

    def mousePressEvent(self, event) -> None:  # noqa: N802
        lst = self._list() if self._whole_row_drag else None
        if lst is not None and event.button() == Qt.MouseButton.LeftButton:
            lst._begin_drag(self, event.globalPosition().toPoint())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        lst = self._list() if self._whole_row_drag else None
        if lst is not None:
            lst._drag_move(event.globalPosition().toPoint())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        lst = self._list() if self._whole_row_drag else None
        if lst is not None:
            lst._end_drag()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, event) -> None:  # noqa: N802
        # An opaque base so a row floating above with a shadow composites
        # cleanly; content widgets paint their own surface on top.
        painter = QPainter(self)
        painter.fillRect(self.rect(), ThemeManager.instance().color(ColorRole.SURFACE))
        painter.end()


class MdReorderableList(QWidget):
    """A vertical list of drag-to-reorder rows.

    Rows are laid out by manual geometry (no QLayout) so a dragged row can float
    free of its slot. Emits :attr:`reordered` ``(old_index, new_index)`` after a
    drag commits a move, with ``new_index`` the final resting index.
    """

    reordered = Signal(int, int)

    def __init__(self, parent: QWidget | None = None, *, drag_handles: bool = True) -> None:
        super().__init__(parent)
        self._drag_handles = bool(drag_handles)
        self._rows: list[_Row] = []
        # drag state
        self._drag_index: int | None = None
        self._dragging = False
        self._grab_offset = 0
        self._press_y = 0
        self._drop_target = 0
        self.setMouseTracking(True)

    # -- content -----------------------------------------------------------

    def add_item(self, content: QWidget) -> None:
        """Append a content widget as a new reorderable row."""
        row = _Row(self, content, handle=self._drag_handles)
        row.show()
        self._rows.append(row)
        self._relayout()
        self.updateGeometry()

    @property
    def items(self) -> list[QWidget]:
        """The content widgets in current (possibly reordered) order."""
        return [r.content for r in self._rows]

    def count(self) -> int:
        return len(self._rows)

    def move_item(self, old_index: int, new_index: int) -> None:
        """Programmatically move a row, emitting :attr:`reordered` if it changes."""
        self._commit_reorder(old_index, new_index)

    # -- geometry ----------------------------------------------------------

    def _row_height(self, index: int) -> int:
        return max(_MIN_ROW, self._rows[index].sizeHint().height())

    def _resting_centers(self) -> list[float]:
        centers: list[float] = []
        y = _GUTTER
        for i in range(len(self._rows)):
            h = self._row_height(i)
            centers.append(y + h / 2)
            y += h
        return centers

    def _relayout(self) -> None:
        w = self.width()
        y = _GUTTER
        for i, row in enumerate(self._rows):
            h = self._row_height(i)
            row.setGeometry(0, y, w, h)
            y += h

    def sizeHint(self) -> QSize:  # noqa: N802
        w = max((r.sizeHint().width() for r in self._rows), default=0)
        h = sum(self._row_height(i) for i in range(len(self._rows))) + 2 * _GUTTER
        return QSize(w, h)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return self.sizeHint()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        if not self._dragging:
            self._relayout()

    # -- drag lifecycle ----------------------------------------------------

    def _begin_drag(self, row: _Row, global_pos: QPoint) -> None:
        self._drag_index = self._rows.index(row)
        local_y = self.mapFromGlobal(global_pos).y()
        self._grab_offset = local_y - row.y()
        self._press_y = local_y
        self._drop_target = self._drag_index
        self._dragging = False

    def _drag_move(self, global_pos: QPoint) -> None:
        if self._drag_index is None:
            return
        local_y = self.mapFromGlobal(global_pos).y()
        if not self._dragging:
            if abs(local_y - self._press_y) < _DRAG_THRESHOLD:
                return
            self._dragging = True
            row = self._rows[self._drag_index]
            apply_elevation(row, ElevationLevel.LEVEL3)
            row.raise_()
        dragged = self._drag_index
        target = self._target_for(dragged, local_y)
        self._drop_target = target
        self._layout_during_drag(dragged, local_y, target)

    def _end_drag(self) -> None:
        if self._drag_index is None:
            return
        old = self._drag_index
        was_dragging = self._dragging
        row = self._rows[old]
        self._drag_index = None
        self._dragging = False
        if was_dragging:
            apply_elevation(row, ElevationLevel.LEVEL0)
            # Commit the slot the preview showed. Recomputing from the row's
            # geometry would disagree with the preview near the bottom edge:
            # the floating row's top is clamped, so its centre can only ever
            # *equal* the last resting centre and the strict `<` in
            # reorder_target_index would land it one slot short.
            self._commit_reorder(old, self._drop_target)
        else:
            self._relayout()

    def _target_for(self, dragged: int, cursor_local_y: int) -> int:
        h = self._row_height(dragged)
        center = (cursor_local_y - self._grab_offset) + h / 2
        return reorder_target_index(self._resting_centers(), dragged, center)

    def _layout_during_drag(self, dragged: int, cursor_local_y: int, target: int) -> None:
        n = len(self._rows)
        order = [i for i in range(n) if i != dragged]
        order.insert(target, dragged)
        w = self.width()
        y = _GUTTER
        for idx in order:
            h = self._row_height(idx)
            row = self._rows[idx]
            if idx == dragged:
                top = cursor_local_y - self._grab_offset
                top = max(_GUTTER, min(top, self.height() - _GUTTER - h))
                row.setGeometry(0, int(top), w, h)
                row.raise_()
                y += h  # reserve the gap the row will drop into
            else:
                row.setGeometry(0, y, w, h)
                y += h

    def _commit_reorder(self, old: int, new: int) -> None:
        n = len(self._rows)
        if not (0 <= old < n):
            return
        new = max(0, min(new, n - 1))
        if new == old:
            self._relayout()
            return
        row = self._rows.pop(old)
        self._rows.insert(new, row)
        self._relayout()
        self.reordered.emit(old, new)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.fillRect(self.rect(), ThemeManager.instance().color(ColorRole.SURFACE))
        painter.end()


__all__ = ["MdReorderableList", "reorder_target_index"]
