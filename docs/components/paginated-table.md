# Paginated table

Data table with page-by-page navigation.

**Classes:** `MdPaginatedDataTable` · **Source:** `src/material_qt/widgets/datatable/` (`paginated.py`)
**Spec:** Flutter API — [`PaginatedDataTable`](https://api.flutter.dev/flutter/material/PaginatedDataTable-class.html), which the module docstring names as the upstream counterpart. Wraps an [`MdDataTable`](./data-table.md) and adds a footer pagination control.

## Usage

```python
from material_qt import MdPaginatedDataTable

table = MdPaginatedDataTable(parent, rows_per_page=5)
table.set_columns(["Item", "Qty", "Price"], numeric=[False, True, True])
table.set_rows([[f"Item {i}", str(i * 2), f"${i * 3}.00"]
                for i in range(1, 24)])

table.pageChanged.connect(lambda page: print("now on page", page))
```

## API

### MdPaginatedDataTable

```python
MdPaginatedDataTable(
    parent: QWidget | None = None,
    *,
    selectable: bool = False,
    rows_per_page: int = 10,
    column_spacing: int = 24,
)
```

- `table` (property) — the wrapped `MdDataTable` (for columns, sort state, and selection access).
- `set_columns(labels, *, numeric=None)` — forwarded to the inner table; `numeric` also drives the wrapper's full-dataset sorting.
- `set_rows(rows)` — replace the *full* dataset; re-applies any active sort and resets to the first page.
- `add_row(values)` — append one row to the full dataset (re-applies the active sort).
- `rows_per_page` (property, settable) / `set_rows_per_page(value)` — page size (minimum 1); changing it resets to the first page.
- `page` (property) — zero-based index of the visible page.
- `page_count()` — number of pages (at least 1, even when empty).
- `set_page(page)` — jump to a page (clamped); emits `pageChanged` if the page actually changes.
- `first_page()` / `previous_page()` / `next_page()` / `last_page()` — navigation, same as the footer buttons.

**Signals:**

- `pageChanged = Signal(int)` — the zero-based page index, emitted whenever the visible page changes (navigation, or a header sort that moves you off a later page).

Sort and selection signals live on the inner table: connect to `table.sortChanged`, `table.selectionChanged`, and `table.selectAllChanged` via the `table` property.

## Notes

- The wrapper owns the **full** dataset and feeds only the current page's slice into the inner `MdDataTable`, re-rendering on navigation. Do not call `set_rows` on the inner table directly — it would be overwritten on the next refresh.
- Clicking a column header sorts the *full* dataset, not just the visible slice: the wrapper intercepts the inner table's `sortChanged`, re-sorts everything with the same numeric/lexical key (shared `sort_rows` helper), then re-pages from the top so page 0 shows the global extreme. If you were not on page 0, this also emits `pageChanged(0)`.
- **Selection is per-page only.** Row checkboxes live in the inner table and are rebuilt on every page change, so navigating away clears them — mirroring `MdDataTable`'s documented "selection resets on re-render" behavior. Cross-page, identity-tracked selection is out of scope.
- The footer is a fixed 56 px strip with an `X–Y of N` range label (1-based, `0–0 of 0` when empty) and first/prev/next/last icon buttons; the buttons disable themselves at the ends of the range.
- If the dataset shrinks (e.g. a smaller `set_rows`), the current page is clamped into the new range on refresh.
- Column alignment/sorting semantics, cell stringification, and the deferred features are all inherited from [Data table](./data-table.md).
