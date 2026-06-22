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
    t.sort_by(0)  # asc
    assert [r[0] for r in t._rows] == ["Apple", "Banana", "Cupcake"]
    t.sort_by(0)  # desc
    assert [r[0] for r in t._rows] == ["Cupcake", "Banana", "Apple"]


def test_sort_numeric_is_value_order_not_lexical(qtbot):
    t = _table(qtbot)
    t.set_columns(["N"], numeric=[True])
    for n in [9, 100, 20]:
        t.add_row([n])
    t.sort_by(0)
    # Numeric: 9 < 20 < 100 (lexical would give 100, 20, 9).
    assert [r[0] for r in t._rows] == ["9", "20", "100"]


def test_sort_changed_signal(qtbot):
    t = _table(qtbot)
    t.set_columns(["A", "B"])
    seen = []
    t.sortChanged.connect(lambda c, asc: seen.append((c, asc)))
    t.sort_by(1)
    assert seen[-1] == (1, True)
    t.sort_by(1)
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


def test_sort_state_accessors(qtbot):
    t = _table(qtbot)
    t.set_columns(["A", "B"])
    assert t.sort_column_index is None
    t.sort_by(1)
    assert t.sort_column_index == 1
    assert t.sort_ascending is True
    t.sort_by(1)  # toggles
    assert t.sort_ascending is False


def test_sort_by_explicit_direction(qtbot):
    t = _table(qtbot)
    t.set_columns(["N"], numeric=[True])
    for n in [3, 1, 2]:
        t.add_row([n])
    t.sort_by(0, ascending=False)
    assert [r[0] for r in t._rows] == ["3", "2", "1"]
    assert t.sort_ascending is False


def test_sort_by_out_of_range_ignored(qtbot):
    t = _table(qtbot)
    t.set_columns(["A"])
    t.sort_by(5)
    assert t.sort_column_index is None


def test_column_spacing(qtbot):
    t = _table(qtbot, column_spacing=12)
    t.set_columns(["A", "B"])
    assert t.column_spacing == 12
    t.column_spacing = 32
    assert t.column_spacing == 32


def test_select_all_changed_signal(qtbot):
    t = _table(qtbot, selectable=True)
    t.set_columns(["Name"])
    for n in ["a", "b"]:
        t.add_row([n])
    seen = []
    t.selectAllChanged.connect(seen.append)
    t._select_all.setChecked(True)
    assert seen == [True]
    assert t.selected_rows() == [0, 1]
