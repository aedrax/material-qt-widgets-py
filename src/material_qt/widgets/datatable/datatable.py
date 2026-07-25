"""Material 3 data table for QtWidgets.

Ports the Material 3 data table (cf. Flutter's ``DataTable``): a 56px heading row
(``label-large`` ``on-surface``) over 52px data rows (``body-medium``
``on-surface``) separated by ``outline-variant`` dividers. Columns can be
right-aligned (numeric) and sorted by clicking the header (toggling asc/desc with
an arrow indicator). An optional leading checkbox column selects rows, with a
header select-all checkbox.

Signals: ``sortChanged(column, ascending)``, ``selectionChanged()`` and
``selectAllChanged(checked)``. Pagination lives in the sibling
:class:`MdPaginatedDataTable` wrapper (``paginated.py``).

Deferred (scaffold): in-cell editing, sticky header, and column
resizing. Row selection resets when the data is sorted or changed (the rows are
re-rendered), since selection is tracked by display index, not row identity.
"""

from __future__ import annotations

import math

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ...core.material_widget import MaterialWidgetMixin
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.shape import ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..checkbox import MdCheckbox
from ..divider import MdDivider

_HEADING_H = 56
_ROW_H = 52
_MARGIN = 24
_CHECKBOX_W = 56
_CELL_V_PAD = 8  # top/bottom padding so wrapped multi-line cells aren't cramped


def _cell_size_policy() -> QSizePolicy:
    """Equal, stretch-driven column width + wrap-aware height.

    Horizontal ``Ignored`` makes every column an equal share (identical in the
    header and every data row, so columns stay aligned at any width); vertical
    ``Minimum`` + ``heightForWidth`` lets a wrapped cell report the taller height
    its text needs at the column's width, so the row grows to fit.
    """
    sp = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
    sp.setHeightForWidth(True)
    return sp


def sort_rows(
    rows: list[list[str]], column: int, *, numeric: bool, ascending: bool
) -> None:
    """Sort ``rows`` in place by ``column``.

    Numeric columns sort by float value; unparseable (or NaN) cells sort last
    in *both* directions. Text columns sort case-insensitively. Shared by
    :class:`MdDataTable` and the paginated wrapper so both order identically.
    """

    def cell(row: list[str]) -> str:
        return row[column] if column < len(row) else ""

    if not numeric:
        rows.sort(key=lambda row: cell(row).lower(), reverse=not ascending)
        return

    def parse(row: list[str]) -> float | None:
        try:
            v = float(cell(row))
        except ValueError:
            return None
        return None if math.isnan(v) else v

    keyed = [(parse(row), row) for row in rows]
    parseable = [(k, row) for k, row in keyed if k is not None]
    junk = [row for k, row in keyed if k is None]
    parseable.sort(key=lambda kr: kr[0], reverse=not ascending)
    rows[:] = [row for _, row in parseable] + junk


class _HeaderCell(QLabel):
    """A clickable header label that toggles sorting for its column."""

    clicked = Signal(int)

    def __init__(self, text: str, column: int, *, numeric: bool) -> None:
        super().__init__(text)
        self._column = column
        self._base_text = text
        self.setFont(font_for_role(TypescaleRole.LABEL_LARGE))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        align = Qt.AlignmentFlag.AlignRight if numeric else Qt.AlignmentFlag.AlignLeft
        self.setAlignment(align | Qt.AlignmentFlag.AlignVCenter)
        self.setWordWrap(True)
        self.setSizePolicy(_cell_size_policy())

    def set_sort_indicator(self, state: str) -> None:
        """``state`` is 'asc', 'desc', or '' (none)."""
        arrow = {"asc": "  ▲", "desc": "  ▼"}.get(state, "")
        self.setText(self._base_text + arrow)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        self.clicked.emit(self._column)


class MdDataTable(MaterialWidgetMixin, QWidget):
    """A Material 3 data table."""

    sortChanged = Signal(int, bool)
    selectionChanged = Signal()
    selectAllChanged = Signal(bool)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        selectable: bool = False,
        column_spacing: int = _MARGIN,
    ) -> None:
        super().__init__(parent)
        self._selectable = selectable
        self._column_spacing = max(0, int(column_spacing))
        self._columns: list[str] = []
        self._numeric: list[bool] = []
        self._rows: list[list[str]] = []
        self._sort_col: int | None = None
        self._sort_asc = True
        self._row_checks: list[MdCheckbox] = []
        self._header_cells: list[_HeaderCell] = []

        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(0)
        self._init_material(
            shape=ShapeScale.NONE,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE,
        )
        ThemeManager.instance().themeChanged.connect(self._render)

    # -- model -------------------------------------------------------------

    def set_columns(self, labels: list[str], *, numeric: list[bool] | None = None) -> None:
        self._columns = list(labels)
        self._numeric = list(numeric) if numeric else [False] * len(labels)
        self._render()

    def add_row(self, values: list) -> None:
        self._rows.append([str(v) for v in values])
        self._apply_sort()
        self._render()

    def set_rows(self, rows: list[list]) -> None:
        """Replace all rows in one shot (single re-render)."""
        self._rows = [[str(v) for v in row] for row in rows]
        self._apply_sort()
        self._render()

    def _apply_sort(self) -> None:
        """Re-apply the active sort so changed data matches the indicator."""
        if self._sort_col is not None and self._sort_col < len(self._numeric):
            sort_rows(
                self._rows,
                self._sort_col,
                numeric=self._numeric[self._sort_col],
                ascending=self._sort_asc,
            )

    def selected_rows(self) -> list[int]:
        return [i for i, cb in enumerate(self._row_checks) if cb.isChecked()]

    @property
    def column_spacing(self) -> int:
        """Horizontal spacing/margin between columns, in pixels."""
        return self._column_spacing

    @column_spacing.setter
    def column_spacing(self, value: int) -> None:
        value = max(0, int(value))
        if value != self._column_spacing:
            self._column_spacing = value
            self._render()

    # -- sorting -----------------------------------------------------------

    @property
    def sort_column_index(self) -> int | None:
        """The column index currently sorted, or ``None`` (Flutter ``sortColumnIndex``)."""
        return self._sort_col

    @property
    def sort_ascending(self) -> bool:
        """Whether the current sort is ascending (Flutter ``sortAscending``)."""
        return self._sort_asc

    def sort_by(self, column: int, *, ascending: bool | None = None) -> None:
        """Programmatically sort by ``column``.

        With ``ascending=None`` this toggles direction when the column is
        already sorted (matching a header click); otherwise it sets the given
        direction. Emits ``sortChanged`` and re-renders.
        """
        if not (0 <= column < len(self._columns)):
            return
        if ascending is None:
            if self._sort_col == column:
                self._sort_asc = not self._sort_asc
            else:
                self._sort_col = column
                self._sort_asc = True
        else:
            self._sort_col = column
            self._sort_asc = bool(ascending)
        sort_rows(
            self._rows,
            column,
            numeric=self._numeric[column],
            ascending=self._sort_asc,
        )
        self.sortChanged.emit(column, self._sort_asc)
        self._render()

    # -- view --------------------------------------------------------------

    def _clear_layout(self) -> None:
        while self._lay.count():
            item = self._lay.takeAt(0)
            if item is None:
                break
            w = item.widget()
            if w is not None:
                # setParent(None) removes it from the tree *now*; deleteLater
                # alone is async, leaving stale rows painted over the new ones.
                w.setParent(None)
                w.deleteLater()

    def _cell_label(self, text: str, *, numeric: bool, heading: bool) -> QLabel:
        lbl = QLabel(text)
        role = TypescaleRole.LABEL_LARGE if heading else TypescaleRole.BODY_MEDIUM
        lbl.setFont(font_for_role(role))
        align = Qt.AlignmentFlag.AlignRight if numeric else Qt.AlignmentFlag.AlignLeft
        lbl.setAlignment(align | Qt.AlignmentFlag.AlignVCenter)
        color = ThemeManager.instance().color(ColorRole.ON_SURFACE).name()
        lbl.setStyleSheet(f"color: {color};")
        lbl.setWordWrap(True)
        lbl.setSizePolicy(_cell_size_policy())
        return lbl

    def _make_row(self, height: int) -> tuple[QWidget, QHBoxLayout]:
        row = QWidget()
        # Minimum (not fixed) height so a row grows when a cell's text wraps to
        # multiple lines; it stays at ``height`` while every cell fits on one.
        row.setMinimumHeight(height)
        sp = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sp.setHeightForWidth(True)
        row.setSizePolicy(sp)
        hl = QHBoxLayout(row)
        hl.setContentsMargins(_MARGIN, _CELL_V_PAD, _MARGIN, _CELL_V_PAD)
        hl.setSpacing(self._column_spacing)
        return row, hl

    def _render(self) -> None:
        self._clear_layout()
        self._row_checks = []
        self._header_cells = []
        if not self._columns:
            return

        # Heading row.
        header, hl = self._make_row(_HEADING_H)
        if self._selectable:
            self._select_all = MdCheckbox()
            self._select_all.toggled.connect(self._on_select_all)
            self._select_all.setFixedWidth(_CHECKBOX_W - _MARGIN)
            hl.addWidget(self._select_all)
        for col, label in enumerate(self._columns):
            cell = _HeaderCell(label, col, numeric=self._numeric[col])
            cell.clicked.connect(self.sort_by)
            state = "" if self._sort_col != col else ("asc" if self._sort_asc else "desc")
            cell.set_sort_indicator(state)
            color = ThemeManager.instance().color(ColorRole.ON_SURFACE).name()
            cell.setStyleSheet(f"color: {color};")
            hl.addWidget(cell, 1)
            self._header_cells.append(cell)
        self._lay.addWidget(header)
        self._lay.addWidget(MdDivider())

        # Data rows.
        for r, values in enumerate(self._rows):
            row, rl = self._make_row(_ROW_H)
            if self._selectable:
                cb = MdCheckbox()
                cb.toggled.connect(self._on_row_toggled)
                cb.setFixedWidth(_CHECKBOX_W - _MARGIN)
                rl.addWidget(cb)
                self._row_checks.append(cb)
            for col in range(len(self._columns)):
                text = values[col] if col < len(values) else ""
                rl.addWidget(
                    self._cell_label(text, numeric=self._numeric[col], heading=False), 1
                )
            self._lay.addWidget(row)
            if r < len(self._rows) - 1:
                self._lay.addWidget(MdDivider())
        # Absorb any extra vertical space so rows keep their natural (content)
        # height instead of stretching to fill a taller container.
        self._lay.addStretch(1)

    def _on_select_all(self, checked: bool) -> None:
        for cb in self._row_checks:
            cb.blockSignals(True)
            cb.setChecked(checked)
            cb.blockSignals(False)
            cb._sync_marker()  # blocked signals skip the visual sync
        self.selectAllChanged.emit(checked)
        self.selectionChanged.emit()

    def _on_row_toggled(self, *_: object) -> None:
        self._sync_select_all()
        self.selectionChanged.emit()

    def _sync_select_all(self) -> None:
        """Mirror row state onto the header checkbox: all -> checked, none ->
        unchecked, mixed -> indeterminate (tristate partial)."""
        checked = [cb.isChecked() for cb in self._row_checks]
        all_checked = bool(checked) and all(checked)
        sa = self._select_all
        sa.blockSignals(True)  # don't ricochet through _on_select_all
        sa.setChecked(all_checked)
        sa.blockSignals(False)
        sa.set_indeterminate(any(checked) and not all_checked)
        sa._sync_marker()  # blocked signals skip the visual sync


__all__ = ["MdDataTable"]
