"""Material paginated data table for QtWidgets.

Ports Flutter's ``PaginatedDataTable``: wraps an :class:`MdDataTable` and adds a
footer pagination control — a "rows per page" count, an "X–Y of N" range label,
and first/prev/next/last navigation buttons. The wrapper owns the *full* dataset
and feeds only the current page's slice into the inner table, re-rendering on
navigation. Emits ``pageChanged(int)`` with the zero-based page index whenever
the visible page changes.

Clicking a column header sorts the *full* dataset (the wrapper intercepts the
inner table's ``sortChanged`` and re-sorts ``_all_rows``), then re-pages from
the top so page 0 shows the global extreme.

Selection limitation: row checkboxes live in the inner table and are rebuilt on
every page change, so selection is per-page only — navigating away clears it.
Cross-page (identity-tracked) selection is out of scope, mirroring
:class:`MdDataTable`'s documented "selection resets on re-render" behavior.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.shape import ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..divider import MdDivider
from ..iconbutton.iconbutton import MdIconButton
from .datatable import MdDataTable, sort_rows

_FOOTER_H = 56
_MARGIN = 24


class MdPaginatedDataTable(MaterialWidgetMixin, QWidget):
    """An :class:`MdDataTable` with a footer pagination control."""

    pageChanged = Signal(int)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        selectable: bool = False,
        rows_per_page: int = 10,
        column_spacing: int = _MARGIN,
    ) -> None:
        super().__init__(parent)
        self._rows_per_page = max(1, int(rows_per_page))
        self._page = 0
        self._all_rows: list[list[str]] = []
        self._numeric: list[bool] = []

        self._table = MdDataTable(
            selectable=selectable, column_spacing=column_spacing
        )
        # A header click sorts the *full* dataset (not just the visible slice),
        # then re-pages from the top so page 0 shows the global extreme.
        self._table.sortChanged.connect(self._on_sort)

        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(0)
        self._lay.addWidget(self._table)
        self._lay.addWidget(MdDivider())
        self._lay.addWidget(self._build_footer())

        self._init_material(
            shape=ShapeScale.NONE,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE,
        )
        ThemeManager.instance().themeChanged.connect(self._restyle_label)

    # -- inner table delegation -------------------------------------------

    @property
    def table(self) -> MdDataTable:
        """The wrapped data table (for columns, sort and selection access)."""
        return self._table

    def set_columns(self, labels: list[str], *, numeric: list[bool] | None = None) -> None:
        self._numeric = list(numeric) if numeric else [False] * len(labels)
        self._table.set_columns(labels, numeric=numeric)

    def set_rows(self, rows: list[list]) -> None:
        """Replace the full dataset; resets to the first page."""
        self._all_rows = [[str(v) for v in row] for row in rows]
        self._page = 0
        self._refresh()

    def add_row(self, values: list) -> None:
        self._all_rows.append([str(v) for v in values])
        self._refresh()

    # -- footer ------------------------------------------------------------

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        footer.setFixedHeight(_FOOTER_H)
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(_MARGIN, 0, _MARGIN, 0)
        fl.setSpacing(8)
        fl.addStretch(1)

        self._range_label = QLabel()
        self._range_label.setFont(font_for_role(TypescaleRole.LABEL_LARGE))
        self._range_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        fl.addWidget(self._range_label)

        self._first_btn = MdIconButton("first_page")
        self._prev_btn = MdIconButton("chevron_left")
        self._next_btn = MdIconButton("chevron_right")
        self._last_btn = MdIconButton("last_page")
        self._first_btn.clicked.connect(self.first_page)
        self._prev_btn.clicked.connect(self.previous_page)
        self._next_btn.clicked.connect(self.next_page)
        self._last_btn.clicked.connect(self.last_page)
        for b in (self._first_btn, self._prev_btn, self._next_btn, self._last_btn):
            fl.addWidget(b)
        return footer

    def _restyle_label(self) -> None:
        color = ThemeManager.instance().color(ColorRole.ON_SURFACE_VARIANT).name()
        self._range_label.setStyleSheet(f"color: {color};")

    # -- paging model ------------------------------------------------------

    @property
    def rows_per_page(self) -> int:
        return self._rows_per_page

    @rows_per_page.setter
    def rows_per_page(self, value: int) -> None:
        value = max(1, int(value))
        if value != self._rows_per_page:
            self._rows_per_page = value
            self._page = 0
            self._refresh()

    def set_rows_per_page(self, value: int) -> None:
        self.rows_per_page = value

    @property
    def page(self) -> int:
        """Zero-based index of the visible page."""
        return self._page

    def page_count(self) -> int:
        if not self._all_rows:
            return 1
        return (len(self._all_rows) + self._rows_per_page - 1) // self._rows_per_page

    def set_page(self, page: int) -> None:
        page = max(0, min(int(page), self.page_count() - 1))
        if page != self._page:
            self._page = page
            self._refresh()
            self.pageChanged.emit(self._page)

    def first_page(self) -> None:
        self.set_page(0)

    def previous_page(self) -> None:
        self.set_page(self._page - 1)

    def next_page(self) -> None:
        self.set_page(self._page + 1)

    def last_page(self) -> None:
        self.set_page(self.page_count() - 1)

    # -- rendering ---------------------------------------------------------

    def _on_sort(self, column: int, ascending: bool) -> None:
        """Re-sort the full dataset when the inner table's header is clicked.

        The inner table has already sorted (and re-rendered) its current page
        slice and set its sort indicator; we re-sort ``_all_rows`` with the same
        key and re-page from the top so the global ordering is correct.
        """
        if 0 <= column < len(self._numeric):
            sort_rows(
                self._all_rows,
                column,
                numeric=self._numeric[column],
                ascending=ascending,
            )
        self._page = 0
        self._refresh()

    def _refresh(self) -> None:
        # Clamp page in case the dataset shrank.
        self._page = max(0, min(self._page, self.page_count() - 1))
        start = self._page * self._rows_per_page
        end = start + self._rows_per_page
        # Feed the current page slice to the inner table via its public
        # set_rows (single re-render; MdDataTable._clear_layout does
        # setParent(None) before deleteLater() so stale rows do not linger).
        self._table.set_rows(self._all_rows[start:end])

        self._update_range_label()
        self._update_buttons()

    def _update_range_label(self) -> None:
        total = len(self._all_rows)
        if total == 0:
            self._range_label.setText("0–0 of 0")
        else:
            start = self._page * self._rows_per_page + 1
            end = min(start + self._rows_per_page - 1, total)
            self._range_label.setText(f"{start}–{end} of {total}")
        self._restyle_label()

    def _update_buttons(self) -> None:
        at_first = self._page <= 0
        at_last = self._page >= self.page_count() - 1
        self._first_btn.setEnabled(not at_first)
        self._prev_btn.setEnabled(not at_first)
        self._next_btn.setEnabled(not at_last)
        self._last_btn.setEnabled(not at_last)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


__all__ = ["MdPaginatedDataTable"]
