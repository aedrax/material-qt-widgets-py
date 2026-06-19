"""Tests for MdDataTable."""

from __future__ import annotations

from material_qt.widgets.datatable import MdDataTable


def _table(qtbot, **kw) -> MdDataTable:
    t = MdDataTable(**kw)
    qtbot.addWidget(t)
    return t


def test_columns_and_rows(qtbot):
    t = _table(qtbot)
    t.set_columns(["Name", "Calories"], numeric=[False, True])
    t.add_row(["Frozen yogurt", 159])
    t.add_row(["Eclair", 262])
    assert t._rows == [["Frozen yogurt", "159"], ["Eclair", "262"]]


def test_sort_string_toggles_direction(qtbot):
    t = _table(qtbot)
    t.set_columns(["Name"])
    for n in ["Cupcake", "Apple", "Banana"]:
        t.add_row([n])
    t._sort_by(0)  # asc
    assert [r[0] for r in t._rows] == ["Apple", "Banana", "Cupcake"]
    t._sort_by(0)  # desc
    assert [r[0] for r in t._rows] == ["Cupcake", "Banana", "Apple"]


def test_sort_numeric_is_value_order_not_lexical(qtbot):
    t = _table(qtbot)
    t.set_columns(["N"], numeric=[True])
    for n in [9, 100, 20]:
        t.add_row([n])
    t._sort_by(0)
    # Numeric: 9 < 20 < 100 (lexical would give 100, 20, 9).
    assert [r[0] for r in t._rows] == ["9", "20", "100"]


def test_sort_changed_signal(qtbot):
    t = _table(qtbot)
    t.set_columns(["A", "B"])
    seen = []
    t.sortChanged.connect(lambda c, asc: seen.append((c, asc)))
    t._sort_by(1)
    assert seen[-1] == (1, True)
    t._sort_by(1)
    assert seen[-1] == (1, False)


def test_selection(qtbot):
    t = _table(qtbot, selectable=True)
    t.set_columns(["Name"])
    for n in ["a", "b", "c"]:
        t.add_row([n])
    t._row_checks[1].setChecked(True)
    assert t.selected_rows() == [1]
    t._select_all.setChecked(True)
    assert t.selected_rows() == [0, 1, 2]


def test_renders(qtbot):
    t = _table(qtbot, selectable=True)
    t.set_columns(["Dessert", "Calories"], numeric=[False, True])
    t.add_row(["Frozen yogurt", 159])
    t.add_row(["Eclair", 262])
    t.resize(t.sizeHint())
    t.grab()
