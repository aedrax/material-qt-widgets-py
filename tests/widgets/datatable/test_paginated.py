"""Tests for MdPaginatedDataTable."""

from __future__ import annotations

from material_qt.widgets.datatable import MdPaginatedDataTable


def _table(qtbot, n=25, **kw) -> MdPaginatedDataTable:
    t = MdPaginatedDataTable(rows_per_page=10, **kw)
    qtbot.addWidget(t)
    t.set_columns(["Name", "N"], numeric=[False, True])
    t.set_rows([[f"row{i}", i] for i in range(n)])
    return t


def test_page_count(qtbot):
    t = _table(qtbot, n=25)
    assert t.page_count() == 3  # 10 + 10 + 5


def test_first_page_slice(qtbot):
    t = _table(qtbot, n=25)
    # Inner table holds only the first 10 rows.
    assert len(t.table._rows) == 10
    assert t.table._rows[0][0] == "row0"
    assert t.table._rows[-1][0] == "row9"


def test_next_and_last_page(qtbot):
    t = _table(qtbot, n=25)
    t.next_page()
    assert t.page == 1
    assert t.table._rows[0][0] == "row10"
    t.last_page()
    assert t.page == 2
    assert len(t.table._rows) == 5  # remainder
    assert t.table._rows[0][0] == "row20"


def test_prev_and_first_clamp(qtbot):
    t = _table(qtbot, n=25)
    t.last_page()
    t.previous_page()
    assert t.page == 1
    t.first_page()
    assert t.page == 0
    t.previous_page()  # already at first; clamps
    assert t.page == 0


def test_page_changed_signal(qtbot):
    t = _table(qtbot, n=25)
    seen = []
    t.pageChanged.connect(seen.append)
    t.next_page()
    t.next_page()
    assert seen == [1, 2]
    # No emit when clamped at the last page.
    t.next_page()
    assert seen == [1, 2]


def test_range_label(qtbot):
    t = _table(qtbot, n=25)
    assert t._range_label.text() == "1–10 of 25"
    t.next_page()
    assert t._range_label.text() == "11–20 of 25"
    t.last_page()
    assert t._range_label.text() == "21–25 of 25"


def test_empty_range_label(qtbot):
    t = MdPaginatedDataTable(rows_per_page=10)
    qtbot.addWidget(t)
    t.set_columns(["A"])
    t.set_rows([])
    assert t._range_label.text() == "0–0 of 0"
    assert t.page_count() == 1


def test_buttons_disabled_at_bounds(qtbot):
    t = _table(qtbot, n=25)
    assert not t._first_btn.isEnabled()
    assert not t._prev_btn.isEnabled()
    assert t._next_btn.isEnabled()
    t.last_page()
    assert t._first_btn.isEnabled()
    assert not t._next_btn.isEnabled()
    assert not t._last_btn.isEnabled()


def test_rows_per_page_resets_and_repages(qtbot):
    t = _table(qtbot, n=25)
    t.next_page()
    t.rows_per_page = 5
    assert t.page == 0
    assert t.page_count() == 5
    assert len(t.table._rows) == 5


def test_header_sort_sorts_full_dataset(qtbot):
    t = _table(qtbot, n=25)  # numeric column "N" holds 0..24, currently asc
    # Simulate a header click on the numeric column (descending toggle path).
    t.table.sort_by(1, ascending=False)
    # Page 0 must show the GLOBAL maxima, not just the first slice re-sorted.
    assert t.page == 0
    assert t.table._rows[0][1] == "24"
    assert t.table._rows[-1][1] == "15"
    # Navigating preserves the global descending order.
    t.next_page()
    assert t.table._rows[0][1] == "14"


def test_set_rows_reapplies_active_sort(qtbot):
    # Regression: set_rows replaced the data but the inner table kept its sort
    # indicator over now-unsorted rows.
    t = _table(qtbot, n=25)
    t.table.sort_by(1, ascending=False)
    t.set_rows([[f"new{i}", i] for i in range(15)])  # unsorted replacement
    assert t.page == 0
    assert t.table._rows[0][1] == "14"  # global max first, per the indicator
    assert t.table._rows[-1][1] == "5"


def test_add_row_reapplies_active_sort(qtbot):
    t = _table(qtbot, n=5)  # single page, 0..4 ascending
    t.table.sort_by(1, ascending=False)
    t.add_row(["mid", 3.5])  # must land between 4 and 3, not at the end
    assert [r[1] for r in t.table._rows] == ["4", "3.5", "3", "2", "1", "0"]


def test_sort_emits_page_changed_when_leaving_page(qtbot):
    # Regression: _on_sort jumped back to page 0 without emitting pageChanged.
    t = _table(qtbot, n=25)
    t.set_page(2)
    seen = []
    t.pageChanged.connect(seen.append)
    t.table.sort_by(1, ascending=False)
    assert t.page == 0
    assert seen == [0]
    # Already on page 0: sorting again must not emit a spurious pageChanged.
    t.table.sort_by(1, ascending=True)
    assert seen == [0]


def test_renders(qtbot):
    t = _table(qtbot, n=25, selectable=True)
    t.resize(t.sizeHint())
    t.grab()
