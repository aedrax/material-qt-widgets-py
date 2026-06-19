"""Material 3 data table for QtWidgets.

Ports the Material 3 data table (cf. Flutter's ``DataTable``): a 56px heading row
(``label-large`` ``on-surface``) over 52px data rows (``body-medium``
``on-surface``) separated by ``outline-variant`` dividers. Columns can be
right-aligned (numeric) and sorted by clicking the header (toggling asc/desc with
an arrow indicator). An optional leading checkbox column selects rows, with a
header select-all checkbox.

Signals: ``sortChanged(column, ascending)`` and ``selectionChanged()``.

Deferred (scaffold): pagination, in-cell editing, sticky header, and column
resizing. Row selection resets when the data is sorted or changed (the rows are
re-rendered), since selection is tracked by display index, not row identity.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
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

    def __init__(self, parent: QWidget | None = None, *, selectable: bool = False) -> None:
        super().__init__(parent)
        self._selectable = selectable
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
        self._render()

    def selected_rows(self) -> list[int]:
        return [i for i, cb in enumerate(self._row_checks) if cb.isChecked()]

    # -- sorting -----------------------------------------------------------

    def _sort_by(self, column: int) -> None:
        if self._sort_col == column:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = column
            self._sort_asc = True

        def key(row: list[str]):
            v = row[column]
            if self._numeric[column]:
                try:
                    return (0, float(v))
                except ValueError:
                    return (1, 0.0)
            return (0, v.lower())

        self._rows.sort(key=key, reverse=not self._sort_asc)
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
        return lbl

    def _make_row(self, height: int) -> tuple[QWidget, QHBoxLayout]:
        row = QWidget()
        row.setFixedHeight(height)
        hl = QHBoxLayout(row)
        hl.setContentsMargins(_MARGIN, 0, _MARGIN, 0)
        hl.setSpacing(_MARGIN)
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
            cell.clicked.connect(self._sort_by)
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
                cb.toggled.connect(lambda *_: self.selectionChanged.emit())
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

    def _on_select_all(self, checked: bool) -> None:
        for cb in self._row_checks:
            cb.blockSignals(True)
            cb.setChecked(checked)
            cb.blockSignals(False)
        self.selectionChanged.emit()


__all__ = ["MdDataTable"]
