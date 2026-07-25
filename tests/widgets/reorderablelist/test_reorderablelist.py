"""Tests for MdReorderableList."""

from __future__ import annotations

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QLabel

from material_qt.widgets.reorderablelist import (
    MdReorderableList,
    reorder_target_index,
)

# Three rows, 56px tall, 8px top gutter -> centres at 36, 92, 148.
_CENTERS = [36.0, 92.0, 148.0]


def test_target_index_drag_to_bottom():
    # Drag row 0 well past the last centre -> it lands at the end (n-1).
    assert reorder_target_index(_CENTERS, 0, 200.0) == 2


def test_target_index_drag_to_top():
    # Drag row 2 above every other centre -> it lands at the start.
    assert reorder_target_index(_CENTERS, 2, 0.0) == 0


def test_target_index_no_op_drop_back():
    # Cursor still over row 1's own slot -> result equals its current index.
    assert reorder_target_index(_CENTERS, 1, 92.0) == 1


def test_target_index_into_middle():
    # Drag row 2 to between rows 0 and 1 -> final index 1.
    assert reorder_target_index(_CENTERS, 2, 50.0) == 1


def test_commit_reorder_applies_and_emits(qtbot):
    lst = MdReorderableList()
    qtbot.addWidget(lst)
    a, b, c = QLabel("a"), QLabel("b"), QLabel("c")
    for w in (a, b, c):
        lst.add_item(w)

    emitted: list[tuple[int, int]] = []
    lst.reordered.connect(lambda o, n: emitted.append((o, n)))

    lst.move_item(0, 2)  # a -> end

    assert [w.text() for w in lst.items] == ["b", "c", "a"]
    assert emitted == [(0, 2)]


def test_commit_reorder_noop_does_not_emit(qtbot):
    lst = MdReorderableList()
    qtbot.addWidget(lst)
    for t in ("a", "b", "c"):
        lst.add_item(QLabel(t))

    emitted: list[tuple[int, int]] = []
    lst.reordered.connect(lambda o, n: emitted.append((o, n)))

    lst.move_item(1, 1)  # drop onto itself

    assert [w.text() for w in lst.items] == ["a", "b", "c"]
    assert emitted == []


def test_commit_reorder_clamps_out_of_range(qtbot):
    lst = MdReorderableList()
    qtbot.addWidget(lst)
    for t in ("a", "b", "c"):
        lst.add_item(QLabel(t))
    lst.move_item(0, 99)  # clamps to n-1
    assert [w.text() for w in lst.items] == ["b", "c", "a"]


def _dragged_list(qtbot):
    lst = MdReorderableList()
    qtbot.addWidget(lst)
    for t in ("a", "b", "c"):
        lst.add_item(QLabel(t))
    lst.resize(lst.sizeHint())  # snug height: the bottom clamp actually bites
    lst.show()
    emitted: list[tuple[int, int]] = []
    lst.reordered.connect(lambda o, n: emitted.append((o, n)))
    return lst, emitted


def _drag(lst: MdReorderableList, row_index: int, to_y: int) -> None:
    row = lst._rows[row_index]
    lst._begin_drag(row, lst.mapToGlobal(QPoint(10, row.y() + 5)))
    lst._drag_move(lst.mapToGlobal(QPoint(10, to_y)))
    lst._end_drag()


def test_drag_past_bottom_edge_lands_in_last_slot(qtbot):
    # Regression: the commit used the *clamped* row geometry while the preview
    # used the raw cursor, so a drag past the bottom edge previewed the last
    # slot but committed one short.
    lst, emitted = _dragged_list(qtbot)
    _drag(lst, 0, lst.height() + 60)
    assert [w.text() for w in lst.items] == ["b", "c", "a"]
    assert emitted == [(0, 2)]


def test_drag_past_top_edge_lands_in_first_slot(qtbot):
    lst, emitted = _dragged_list(qtbot)
    _drag(lst, 2, -60)
    assert [w.text() for w in lst.items] == ["c", "a", "b"]
    assert emitted == [(2, 0)]


def test_drag_below_threshold_does_not_reorder(qtbot):
    lst, emitted = _dragged_list(qtbot)
    row = lst._rows[0]
    lst._begin_drag(row, lst.mapToGlobal(QPoint(10, row.y() + 5)))
    lst._drag_move(lst.mapToGlobal(QPoint(10, row.y() + 7)))  # 2px < threshold
    lst._end_drag()
    assert [w.text() for w in lst.items] == ["a", "b", "c"]
    assert emitted == []


def test_count_and_items_order(qtbot):
    lst = MdReorderableList()
    qtbot.addWidget(lst)
    for t in ("one", "two"):
        lst.add_item(QLabel(t))
    assert lst.count() == 2
    assert [w.text() for w in lst.items] == ["one", "two"]
