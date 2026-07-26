# Data table

Rows and columns of sortable data.

**Classes:** `MdDataTable` · **Source:** `src/material_qt/widgets/datatable/`
**Spec:** data tables are an M2-era spec ([m2.material.io/components/data-tables](https://m2.material.io/components/data-tables)); there is no page for them in the current M3 catalogue. The module docstring names Flutter's [`DataTable`](https://api.flutter.dev/flutter/material/DataTable-class.html) as the upstream counterpart.

## Usage

```python
from material_qt import MdDataTable

table = MdDataTable(parent, selectable=True)
table.set_columns(["Dessert", "Calories", "Fat (g)"],
                  numeric=[False, True, True])
for row in [["Frozen yogurt", 159, 6], ["Ice cream sandwich", 237, 9],
            ["Eclair", 262, 16], ["Cupcake", 305, 4]]:
    table.add_row(row)

table.sortChanged.connect(lambda col, asc: print("sorted", col, asc))
table.selectionChanged.connect(lambda: print("selected:", table.selected_rows()))
```

## API

### MdDataTable

```python
MdDataTable(
    parent: QWidget | None = None,
    *,
    selectable: bool = False,
    column_spacing: int = 24,
)
```

- `set_columns(labels, *, numeric=None)` — define the column headers; `numeric` is a per-column `list[bool]` (defaults to all `False`) that right-aligns the column and switches it to numeric sorting.
- `add_row(values)` — append one row; every value is stringified with `str()`.
- `set_rows(rows)` — replace all rows in one shot (single re-render).
- `selected_rows()` — display indices of the checked rows (`selectable` tables only).
- `column_spacing` (property, settable) — horizontal spacing between columns, in pixels.
- `sort_column_index` (property) — the column currently sorted, or `None` (Flutter `sortColumnIndex`).
- `sort_ascending` (property) — whether the current sort is ascending (Flutter `sortAscending`).
- `sort_by(column, *, ascending=None)` — programmatically sort. With `ascending=None` it behaves like a header click: toggles direction if the column is already sorted, else sorts ascending. Emits `sortChanged` and re-renders.

**Signals:**

- `sortChanged = Signal(int, bool)` — `(column, ascending)` after a header click or `sort_by`.
- `selectionChanged = Signal()` — any row-checkbox or select-all change.
- `selectAllChanged = Signal(bool)` — the header select-all checkbox was toggled.

The module-level helper `sort_rows(rows, column, *, numeric, ascending)` implements the ordering and is shared with the paginated wrapper so both sort identically.

## Notes

- Sorting is numeric-vs-lexical per column, controlled by the `numeric` flag passed to `set_columns`: numeric columns sort by `float` value with unparseable (or NaN) cells last in *both* directions; text columns sort case-insensitively.
- **Selection is tracked by display index, not row identity, and resets whenever the rows are re-rendered** — i.e. on any sort, `add_row`, or `set_rows`. Read `selected_rows()` before mutating or sorting if you need it.
- The active sort is sticky: `add_row`/`set_rows` re-apply it so new data keeps matching the header's sort indicator.
- Layout: a 56 px heading row (`label-large`) over 52 px data rows (`body-medium`), separated by `outline-variant` dividers. Columns share the width equally; cells word-wrap and a row grows taller when its text wraps.
- With `selectable=True` a leading checkbox column appears plus a header select-all checkbox that mirrors row state as checked / unchecked / indeterminate (mixed).
- Header cells are clickable anywhere on the label and show an `▲`/`▼` arrow for the active sort direction.
- Deferred (scaffold): in-cell editing, sticky header, and column resizing.
- For page-by-page navigation over larger datasets, use [Paginated table](./paginated-table.md), which wraps this widget.
