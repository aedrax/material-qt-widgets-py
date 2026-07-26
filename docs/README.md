# material-qt documentation

Material Design 3 as plain QtWidgets for PySide6. If you're new here, start
with the guides; the component reference covers every widget in the
catalogue.

## Guides

| Doc | Covers |
| --- | --- |
| [Getting started](./usage.md) | Install, minimal app, imports, icons, scrollbars, the gallery, running tests |
| [Theming](./theming.md) | `ThemeManager`, light/dark/system, color roles, brand overrides, presets, native-widget palette |
| [Architecture](./architecture.md) | The tokens → theme → core → widgets stack, `MaterialWidgetMixin`, motion, typography, library conventions |

## Components

One page per gallery page (`python -m material_qt.gallery` shows them all
live). The category grouping below is a documentation aid — the package
tree itself is flat.

### Buttons & actions

| Component | Classes | |
| --- | --- | --- |
| [Button](./components/button.md) | `MdElevatedButton` `MdFilledButton` `MdFilledTonalButton` `MdOutlinedButton` `MdTextButton` | Five common button variants for actions. |
| [Icon button](./components/icon-button.md) | `MdIconButton` `MdFilledIconButton` `MdFilledTonalIconButton` `MdOutlinedIconButton` | Icon-only buttons, optionally toggleable. |
| [FAB](./components/fab.md) | `MdFab` `MdBrandedFab` | Floating action button for the primary action. |
| [FAB menu](./components/fab-menu.md) | `MdFabMenu` | A FAB that expands into labeled actions. |
| [Button group](./components/button-group.md) | `MdButtonGroup` | Connected pills, single- or multi-select. |
| [Segmented](./components/segmented.md) | `MdSegmentedButtonSet` `MdSegmentedButton` | Connected toggle buttons for choices. |
| [Split button](./components/split-button.md) | `MdSplitButton` | Primary action plus a dropdown. |

### Selection controls

| Component | Classes | |
| --- | --- | --- |
| [Checkbox](./components/checkbox.md) | `MdCheckbox` | Select one or more items from a set. |
| [Radio](./components/radio.md) | `MdRadio` | Select one option from a set. |
| [Switch](./components/switch.md) | `MdSwitch` | Toggle the state of a single item. |
| [Slider](./components/slider.md) | `MdSlider` | Select a value from a range. |
| [Range slider](./components/range-slider.md) | `MdRangeSlider` | Select a range between two values. |

### Text input & fields

| Component | Classes | |
| --- | --- | --- |
| [Field](./components/field.md) | `MdField` | Chrome shared by text fields and selects. |
| [Text field](./components/text-field.md) | `MdFilledTextField` `MdOutlinedTextField` | Let users enter and edit text. |
| [Select](./components/select.md) | `MdFilledSelect` `MdOutlinedSelect` | Dropdown to pick from options. |
| [Autocomplete](./components/autocomplete.md) | `MdAutocomplete` `MdFilledAutocomplete` `MdOutlinedAutocomplete` | Text field that filters options as you type. |
| [Search bar](./components/search-bar.md) | `MdSearchBar` `MdSearchView` | Field for searching app content. |
| [Chips](./components/chips.md) | `MdAssistChip` `MdFilterChip` `MdInputChip` `MdSuggestionChip` `MdChoiceChip` `MdChipSet` | Compact elements for input, filters, and actions. |

### Navigation

| Component | Classes | |
| --- | --- | --- |
| [Navigation bar](./components/navigation-bar.md) | `MdNavigationBar` | Bottom bar switching destinations. |
| [Navigation rail](./components/navigation-rail.md) | `MdNavigationRail` | Vertical side rail switching destinations. |
| [Navigation drawer](./components/navigation-drawer.md) | `MdNavigationDrawer` | Side panel of navigation destinations. |
| [Navigation tab](./components/navigation-tab.md) | `MdNavigationTab` | A single navigation destination. |
| [Tabs](./components/tabs.md) | `MdTabs` `MdTab` | Organize content across primary/secondary tabs. |
| [Top app bar](./components/top-app-bar.md) | `MdTopAppBar` | Title and actions at the top of a screen. |
| [Bottom app bar](./components/bottom-app-bar.md) | `MdBottomAppBar` | Bottom action bar with an optional FAB. |

### Containment & sheets

| Component | Classes | |
| --- | --- | --- |
| [Card](./components/card.md) | `MdCard` | Container for related content and actions. |
| [Dialog](./components/dialog.md) | `MdDialog` | Modal surface for focused tasks and decisions. |
| [Bottom sheet](./components/bottom-sheet.md) | `MdBottomSheet` `MdStandardBottomSheet` | Sheet anchored to the bottom edge. |
| [Side sheet](./components/side-sheet.md) | `MdSideSheet` `MdStandardSideSheet` | Side panel for supporting content. |
| [Draggable sheet](./components/draggable-sheet.md) | `MdDraggableScrollableSheet` | Resizable bottom sheet with scrollable content. |
| [Expansion panel](./components/expansion-panel.md) | `MdExpansionPanel` | Header that expands to reveal content. |
| [Divider](./components/divider.md) | `MdDivider` | Thin line that groups content. |

### Lists, tables & collections

| Component | Classes | |
| --- | --- | --- |
| [List](./components/list.md) | `MdList` `MdListItem` | Vertical index of text and images. |
| [Item](./components/item.md) | `MdItem` | Content layout primitive with slots. |
| [Reorderable list](./components/reorderable-list.md) | `MdReorderableList` | Drag rows by a handle to reorder them. |
| [Data table](./components/data-table.md) | `MdDataTable` | Rows and columns of sortable data. |
| [Paginated table](./components/paginated-table.md) | `MdPaginatedDataTable` | Data table with page-by-page navigation. |
| [Carousel](./components/carousel.md) | `MdCarousel` `MdWeightedCarousel` | Scrollable row of contained items. |
| [Dismissible](./components/dismissible.md) | `MdDismissible` | Swipe a row aside to dismiss it. |

### Menus & overlays

| Component | Classes | |
| --- | --- | --- |
| [Menu](./components/menu.md) | `MdMenu` `MdMenuItem` `MdSubmenuItem` `DropdownController` | Popup list of choices anchored to a control. |
| [Tooltip](./components/tooltip.md) | `MdTooltip` | Brief label shown on hover or focus. |
| [Toolbar](./components/toolbar.md) | `MdToolbar` | Floating or docked row of actions. |

### Pickers

| Component | Classes | |
| --- | --- | --- |
| [Date picker](./components/date-picker.md) | `MdDatePicker` | Select a date from a calendar. |
| [Calendar](./components/calendar.md) | `MdCalendarDatePicker` | Inline calendar for selecting a date. |
| [Time picker](./components/time-picker.md) | `MdTimePicker` | Select a time on a clock dial. |

### Feedback & progress

| Component | Classes | |
| --- | --- | --- |
| [Progress](./components/progress.md) | `MdLinearProgress` `MdCircularProgress` | Linear and circular progress. |
| [Loading indicator](./components/loading-indicator.md) | `MdLoadingIndicator` | Morphing shape for short waits. |
| [Refresh indicator](./components/refresh-indicator.md) | `MdRefreshIndicator` | Pull-to-refresh spinner over content. |
| [Snackbar](./components/snackbar.md) | `MdSnackbar` | Brief message with an optional action. |
| [Banner](./components/banner.md) | `MdBanner` | Prominent inline message with actions. |
| [Badge](./components/badge.md) | `MdBadge` | Small status indicator overlaid on an anchor. |

### Media & misc

| Component | Classes | |
| --- | --- | --- |
| [Icon](./components/icon.md) | `MdIcon` | Material Symbols icon rendering. |
| [Avatar](./components/avatar.md) | `MdCircleAvatar` | Circular image or initials for a person. |
| [Scrollbar](./components/scrollbar.md) | `MdScrollBar` | Rounded thumb that thickens on hover. |
| [Stepper](./components/stepper.md) | `MdStepper` | Guide a user through ordered steps. |

The gallery's Typography page has no widget of its own — the type scale is
covered in [Architecture § Typography](./architecture.md#typography--the-type-scale).
