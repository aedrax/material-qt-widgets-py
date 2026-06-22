# Flutter ↔ material_qt widget parity

These checklists audit every user-facing Flutter Material widget (reference:
the `flutter/` submodule, `packages/flutter/lib/src/material/`) against the
`material_qt` PySide6/QtWidgets port, category by category. Each Flutter
property is mapped to its idiomatic **QObject** equivalent — Qt Signals for
callbacks, `set_*()`/`@property`/constructor kwargs for named params, theme-role
colors instead of per-instance color args — and marked:

- ✅ verified · ➕ property added this pass · 🆕 component built this pass · ⛔ N/A (with rationale)

## Checklists by category

| Category | File |
|---|---|
| Buttons, FAB, icon buttons | [buttons.md](buttons.md) |
| Selection controls (checkbox/radio/switch) | [selection-controls.md](selection-controls.md) |
| Sliders | [sliders.md](sliders.md) |
| Segmented & button groups | [segmented.md](segmented.md) |
| Text input | [text-input.md](text-input.md) |
| Menus, select & autocomplete | [menus.md](menus.md) |
| Search | [search.md](search.md) |
| App bars & toolbars | [app-bars.md](app-bars.md) |
| Navigation | [navigation.md](navigation.md) |
| Dialogs & sheets | [dialogs-sheets.md](dialogs-sheets.md) |
| Pickers | [pickers.md](pickers.md) |
| Chips | [chips.md](chips.md) |
| Containment & data display | [containment-data.md](containment-data.md) |
| Progress & feedback | [feedback.md](feedback.md) |
| Expansion, stepper & carousel | [expansion-stepper.md](expansion-stepper.md) |

## Components built during this audit (🆕)

Gaps that were genuinely missing whole components, now built (each with tests
and a gallery page unless noted):

| Component | Flutter source | Qt module |
|---|---|---|
| `MdAutocomplete` | `autocomplete.dart` | `widgets/autocomplete` |
| `MdSubmenuItem` | `menu_anchor.dart` (SubmenuButton) | `widgets/menu` |
| `MdSearchView` (full-screen search) | `search_anchor.dart` | `widgets/searchbar` |
| `MdBottomAppBar` | `bottom_app_bar.dart` | `widgets/bottomappbar` |
| `MdCalendarDatePicker` (inline) | `calendar_date_picker.dart` | `widgets/datepicker` |
| `MdChoiceChip` | `choice_chip.dart` | `widgets/chips` |
| `MdCircleAvatar` | `circle_avatar.dart` | `widgets/avatar` |
| `MdPaginatedDataTable` | `paginated_data_table.dart` | `widgets/datatable` |
| `MdRefreshIndicator` | `refresh_indicator.dart` | `widgets/refreshindicator` |
| `MdStepper` (+`MdStep`) | `stepper.dart` | `widgets/stepper` |

## Notes

- Flutter framework idioms with no Qt analog (`ButtonStyle`/`WidgetStateProperty`,
  `clipBehavior`, `visualDensity`, `materialTapTargetSize`, `*ThemeData`,
  semantics/restoration, hero/route animation) are marked ⛔ with rationale in
  each checklist — they are Flutter-specific, not port gaps.
- Per-instance color args (`activeColor`, `backgroundColor`, …) map to M3 theme
  **roles**, set globally via `ThemeManager`, not per widget.
