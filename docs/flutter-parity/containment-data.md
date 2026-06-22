# Containment & data display — Flutter ↔ material_qt parity

Status legend: ✅ verified · ➕ added this pass · 🆕 built this pass · ⛔ N/A (rationale)

Idioms: Flutter callbacks → Qt Signals; `final foo` props → `@property`/`set_*()`/
constructor kwargs; `Color?` → theme `ColorRole` resolved live in `paintEvent`
(repaints on `themeChanged`).

## Card (card.dart) → MdCard (widgets/card) — covered ✅
| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `child` | `add_widget()` / `content_layout()` | ✅ |
| `color` | per-variant `surface_role` (theme) | ✅ |
| `elevation` | `set_elevation()` (mixin) + per-variant default | ✅ |
| `shape` | `set_radii()` (mixin); corner-medium default | ✅ |
| Elevated/Filled/Outlined | `CardVariant` enum | ✅ |
| `margin` | ⛔ outer margin is the parent layout's job in Qt (`QLayout.setContentsMargins` on the container), not a property of the widget itself; inner content padding is exposed via the content layout. |
| `shadowColor` / `surfaceTintColor` | ⛔ Qt elevation uses a `QGraphicsDropShadowEffect`; no per-card tint role in M3 Qt port. |
| `borderOnForeground` / `clipBehavior` / `semanticContainer` | ⛔ rendering/semantics details with no Qt analogue. |

## ListTile (list_tile.dart) → MdListItem/MdItem (widgets/list, widgets/item) — covered ✅
| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `leading` | `set_leading()` / `leading=` (MdItem) | ✅ |
| `title` | `headline=` / `set_headline()` | ✅ |
| `subtitle` | `supporting_text=` / `set_supporting_text()` | ✅ |
| `trailing` | `set_trailing()` / `trailing=` | ✅ |
| `onTap` | `clicked` Signal | ✅ |
| `selected` | `selected` @property / `set_selected()` (tonal `secondary-container` paint) | ➕ |
| `enabled` | `enabled` @property / `set_enabled()` (suppresses `clicked`) | ➕ |
| `contentPadding` | `set_content_padding(l,t,r,b)` / `content_padding()` | ➕ |
| `onLongPress` / `onFocusChange` / hover/focus/splash colors | ⛔ press/focus handled by the Material mixin (ripple + focus ring); no per-tile color overrides. |
| `dense` / `visualDensity` / `isThreeLine` / `*TextStyle` | ⛔ typography & density fixed by M3 typescale roles. |

## Divider (divider.dart) → MdDivider (widgets/divider) — covered ✅
| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| horizontal/vertical | `orientation=` / `set_orientation()` | ✅ |
| `thickness` | `thickness` @property / ctor kwarg (re-applies fixed extent) | ➕ |
| `indent` | `indent` @property / ctor kwarg (numeric px) | ➕ |
| `endIndent` | `end_indent` @property / ctor kwarg | ➕ |
| `color` | `color_role` @property / `set_color_role()` / ctor kwarg (theme) | ➕ |
| web `inset`/`inset-start`/`inset-end` | boolean `inset` / `inset_start` / `inset_end` (16px) — stacks with numeric indent | ✅ |
| `height` / `radius` | ⛔ `height` is the divider's *layout box* (Qt: parent layout spacing); `radius` (rounded ends) not in M3 Qt port. |

## DataTable (data_table.dart) → MdDataTable (widgets/datatable) — covered ✅
| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `columns` | `set_columns(labels, numeric=)` | ✅ |
| `rows` | `add_row()` | ✅ |
| `DataColumn.numeric` | `numeric=` list (right-aligns + numeric sort) | ✅ |
| `DataColumn.onSort` / sort | `_HeaderCell` click + `sort_by()` + `sortChanged` Signal | ✅ |
| `sortColumnIndex` | `sort_column_index` @property | ➕ |
| `sortAscending` | `sort_ascending` @property | ➕ |
| (programmatic sort) | `sort_by(column, ascending=None)` | ➕ |
| `onSelectAll` | `selectAllChanged(bool)` Signal (header select-all) | ➕ |
| row selection | `selectable=`, `selected_rows()`, `selectionChanged` Signal | ✅ |
| `columnSpacing` | `column_spacing` @property / ctor kwarg | ➕ |
| `horizontalMargin` | fixed 24px row margin (`_MARGIN`) | ✅ |
| `decoration` / `*RowColor` / `*TextStyle` / `border` | ⛔ colors & typography fixed by M3 surface/typescale roles. |
| in-cell editing / sticky header / column resize | ⛔ deferred scaffold (noted in module docstring). |

## CircleAvatar (circle_avatar.dart) → MdCircleAvatar (widgets/avatar) — built 🆕
| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `child` (initials/text) | `text=` / `text` @property / `set_text()` | 🆕 |
| `backgroundImage` | `image=` (`QPixmap | str` path) / `set_image()` | 🆕 |
| `backgroundColor` | `background_role` (theme, default `primary-container`) | 🆕 |
| `foregroundColor` | `foreground_role` (theme, default `on-primary-container`) | 🆕 |
| `radius` | `radius` @property / `set_radius()` (default 20 ⇒ 40px circle) | 🆕 |
| `minRadius` / `maxRadius` | ⛔ single `radius` covers sizing; animated constraint pair not ported. |
| `foregroundImage` | ⛔ collapsed into `image` (no separate fg/bg image layering). |
| `onBackgroundImageError` / `onForegroundImageError` | ⛔ Qt surfaces load failure synchronously via `QPixmap.isNull()` (falls back to text). |

## PaginatedDataTable (paginated_data_table.dart) → MdPaginatedDataTable (widgets/datatable) — built 🆕
Wrapper that owns the full dataset and feeds the current page slice into an inner
`MdDataTable` (keeps the GOTCHA-safe `_clear_layout` re-render).
| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `columns` / `source` rows | `set_columns()`, `set_rows()`, `add_row()` | 🆕 |
| `rowsPerPage` | `rows_per_page` @property / `set_rows_per_page()` / ctor kwarg | 🆕 |
| `initialFirstRowIndex` / current page | `page` @property, `set_page()` | 🆕 |
| first/prev/next/last controls | `first_page()` / `previous_page()` / `next_page()` / `last_page()` + footer `MdIconButton`s (disabled at bounds) | 🆕 |
| `onPageChanged` | `pageChanged(int)` Signal (zero-based) | 🆕 |
| "X–Y of N" label | footer range label (`label-large`, `on-surface-variant`) | 🆕 |
| `columnSpacing` | `column_spacing=` (forwarded to inner table) | 🆕 |
| header sort | ✅ intercepts inner `sortChanged`, re-sorts the *full* dataset, re-pages from top (global ordering, not per-slice). |
| row selection | ⛔ per-page only — checkboxes are rebuilt each page so navigation clears selection; cross-page identity-tracked selection out of scope (mirrors `MdDataTable`'s "selection resets on re-render"). |
| `header` / `actions` / `availableRowsPerPage` dropdown | ⛔ not ported — core paging control only (rows-per-page is set programmatically). |
| `onRowsPerPageChanged` / `controller` / `arrowHeadColor` | ⛔ no rows-per-page selector UI; styling via theme roles. |

- [x] all properties verified or added
- [ ] Coordinator follow-up: register `MdCircleAvatar` and `MdPaginatedDataTable` in the gallery (`catalog`/`gallery.py`); export `MdCircleAvatar` from `widgets/__init__.py` (and `MdPaginatedDataTable` is already exported from `widgets/datatable`). Not done here per the shared-file rule.
