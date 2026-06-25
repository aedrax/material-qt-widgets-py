"""Tests for MdDataTable."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from material_qt.widgets.datatable import MdDataTable


def _table(qtbot, **kw) -> MdDataTable:
    t = MdDataTable(**kw)
    qtbot.addWidget(t)
    return t


def test_columns_stay_aligned_at_narrow_width(qtbot):
    # Regression: rows with longer text used to push their columns past the
    # header's. Every column must share an identical, stretch-driven width, so
    # each data row's cell x-positions match the header's even when narrow.
    host = QWidget()
    lay = QVBoxLayout(host)
    t = MdDataTable()
    t.set_columns(["Dessert", "Calories", "Protein"], numeric=[False, True, True])
    t.set_rows([
        ["Frozen yogurt", "159", "4.0"],
        ["Ice cream sandwich is long", "237", "4.3"],
        ["Eclair", "262", "6.0"],
    ])
    lay.addWidget(t)
    qtbot.addWidget(host)
    host.resize(240, 300)  # narrow enough that long text would overflow
    host.show()
    qtbot.waitExposed(host)

    def xs(widget) -> list[int]:
        return [c.mapTo(t, c.rect().topLeft()).x()
                for c in widget.findChildren(QLabel)]

    header_xs = [c.mapTo(t, c.rect().topLeft()).x() for c in t._header_cells]
    header_row = t._header_cells[0].parentWidget()
    data_rows = [
        t._lay.itemAt(i).widget()
        for i in range(t._lay.count())
        if t._lay.itemAt(i).widget() is not None
        and t._lay.itemAt(i).widget() is not header_row
        and t._lay.itemAt(i).widget().findChildren(QLabel)
    ]
    assert len(data_rows) == 3
    for row in data_rows:
        assert xs(row) == header_xs


def test_long_cell_text_wraps_and_grows_its_row(qtbot):
    # Content should wrap to multiple lines (taller row) rather than vanish.
    from material_qt.widgets.datatable.datatable import _ROW_H

    host = QWidget()
    lay = QVBoxLayout(host)
    t = MdDataTable()
    t.set_columns(["Dessert", "Calories"], numeric=[False, True])
    t.set_rows([
        ["Short", "1"],
        ["A rather long multi word dessert description here", "2"],
    ])
    lay.addWidget(t)
    qtbot.addWidget(host)
    host.resize(220, 400)
    host.show()
    qtbot.waitExposed(host)

    header_row = t._header_cells[0].parentWidget()
    rows = [
        t._lay.itemAt(i).widget()
        for i in range(t._lay.count())
        if t._lay.itemAt(i).widget() is not None
        and t._lay.itemAt(i).widget() is not header_row
        and t._lay.itemAt(i).widget().findChildren(QLabel)
    ]
    short_row, long_row = rows
    # The wrapped row is taller than the single-line baseline; the short one isn't.
    assert long_row.height() > _ROW_H
    assert long_row.height() > short_row.height()


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
