# Navigation — Flutter ↔ material_qt parity

Status legend: ✅ verified · ➕ added this pass · 🆕 built this pass · ⛔ N/A (rationale)

Scope note: this maps the navigation widgets called out in the unit task. Flutter
framework idioms with no QtWidgets analogue (overlay/splash factories, gesture
physics, text scalers, `WidgetStateProperty`, `ShapeBorder`, surface-tint, semantic
labels, clip behavior) are marked ⛔ with a rationale rather than ported. Colors
come from the active `ThemeManager` palette (theme-role) unless an explicit
override is set.

## NavigationBar (navigation_bar.dart) → MdNavigationBar (widgets/navigationbar) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `destinations` | `add_destination(label, *, icon, active_icon, badge)` | ✅ |
| `selectedIndex` | `selected_index` @property + `set_selected_index(i)` | ➕ |
| `onDestinationSelected` | `changed(int)` Signal | ✅ |
| `labelBehavior` | `label_behavior` ctor kwarg + `set_label_behavior("always"/"selected"/"hide")` | ✅ |
| (per-destination badge — Qt extension) | `add_destination(..., badge=""/text)` → dot or count pill | ✅ |
| `backgroundColor` | `surface-container` theme role (`MaterialWidgetMixin`) | ✅ |
| `animationDuration` | motion tokens via `MdNavigationTab` toggle | ⛔ derived from motion tokens, not a public knob |
| `elevation` / `shadowColor` / `surfaceTintColor` | — | ⛔ not in unit scope; M3 bar is flat surface-container |
| `indicatorColor` / `indicatorShape` | `secondary-container` pill (theme) | ⛔ not in unit scope for the bar (scoped to TabBar) |
| `height` | fixed 80px (M3 token) | ⛔ spec-fixed |
| `overlayColor` / `labelTextStyle` / `labelPadding` / `maintainBottomViewPadding` | — | ⛔ `WidgetStateProperty`/layout-padding framework idioms |

- [x] all properties verified or added

### NavigationDestination → MdNavigationTab (widgets/navigationtab) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `icon` | `icon` ctor kwarg | ✅ |
| `selectedIcon` | `active_icon` ctor kwarg | ✅ |
| `label` | `label` positional / `setText` | ✅ |
| `enabled` | `setEnabled()` (QAbstractButton) — ripple disables with it | ✅ |
| `tooltip` | `setToolTip()` (QWidget) | ✅ |
| (badge — Qt extension) | `set_badge(""/text/None)` | ✅ |

- [x] all properties verified or added

## NavigationRail (navigation_rail.dart) → MdNavigationRail (widgets/navigationrail) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `destinations` | `add_destination(label, *, icon, active_icon)` | ✅ |
| `selectedIndex` | `selected_index` @property + `set_selected_index(i)` | ➕ |
| `onDestinationSelected` | `changed(int)` Signal | ✅ |
| `extended` | `extended` ctor kwarg + @property + `set_extended(bool, *, animated)` (animated width) | ✅ |
| `labelType` | `label_type` ctor kwarg + `set_label_type("all"/"selected"/"none")` | ✅ |
| `groupAlignment` | `group_alignment` ctor kwarg + `set_group_alignment("top"/"center"/"bottom")` | ✅ |
| `leading` | `set_leading(widget, *, at_top=None)` | ✅ |
| `trailing` | `set_trailing(widget, *, at_bottom=None)` | ✅ |
| `leadingAtTop` | `leading_at_top` ctor kwarg + `set_leading_at_top(bool)` | ➕ |
| `trailingAtBottom` | `trailing_at_bottom` ctor kwarg + `set_trailing_at_bottom(bool)` | ➕ |
| `backgroundColor` | `surface` theme role | ✅ |
| `useIndicator` / `indicatorColor` / `indicatorShape` | `secondary-container` pill (theme) | ⛔ not in unit scope; spec-styled |
| `minWidth` / `minExtendedWidth` | 80px / 256px (M3 tokens) | ⛔ spec-fixed |
| `elevation` | — | ⛔ not in unit scope; flat surface |
| `scrollable` / `mainAxisAlignment` | `group_alignment` covers the alignment cases | ⛔ rail height fits its destinations; scroll not needed |
| `unselected/selectedLabelTextStyle`, `unselected/selectedIconTheme` | typescale tokens + theme roles | ⛔ `TextStyle`/`IconThemeData` framework idioms |

- [x] all properties verified or added

### NavigationRailDestination → _RailDestination (widgets/navigationrail) — covered ✅

| Flutter property | Qt equivalent | Status |
|---|---|---|
| `icon` / `selectedIcon` | `icon` / `active_icon` | ✅ |
| `label` | `label` positional | ✅ |
| `disabled` | `setEnabled(False)` | ✅ |
| `indicatorColor` / `indicatorShape` / `padding` | theme pill + token spacing | ⛔ per-destination style override out of scope |

- [x] all properties verified or added

## NavigationDrawer (navigation_drawer.dart) + Drawer (drawer.dart) → MdNavigationDrawer (widgets/navigationdrawer) — covered ✅

The task notes Drawer ≈ NavigationDrawer container, so Drawer's container props map
onto MdNavigationDrawer (no separate MdDrawer widget).

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `children` (destinations / sections / dividers) | `add_destination()`, `add_section()`, `add_divider()`, `add_widget()` | ✅ |
| `header` | `headline` ctor kwarg (title-small header) | ✅ |
| `footer` | `set_footer(widget)` — pinned to the bottom, below destinations | ➕ |
| `selectedIndex` | `selected_index` @property + `set_selected_index(i)` (destinations only) | ➕ |
| `onDestinationSelected` | `changed(int)` Signal (index among destinations only) | ✅ |
| `backgroundColor` | `surface-container-low` theme role | ✅ |
| Drawer `width` | `set_width(px)` (default 360 M3 container width) | ➕ |
| `tilePadding` | 16px row padding (M3 token) | ⛔ spec-fixed |
| Drawer/NavigationDrawer `elevation` / `shadowColor` / `surfaceTintColor` / `shape` | — | ⛔ not in unit scope; flat container |
| `indicatorColor` / `indicatorShape` | `secondary-container` full-pill (theme) | ⛔ not in unit scope; spec-styled |
| Drawer `child` / `semanticLabel` / `clipBehavior` | arbitrary content via `add_widget()` | ⛔ container is the navigation drawer; clip/semantics framework idioms |

- [x] all properties verified or added

### NavigationDrawerDestination → _DrawerItem (widgets/navigationdrawer) — covered ✅

| Flutter property | Qt equivalent | Status |
|---|---|---|
| `icon` / `selectedIcon` | `icon` / `active_icon` | ✅ |
| `label` | `label` positional | ✅ |
| `enabled` | `setEnabled()` | ✅ |
| `backgroundColor` | `secondary-container` active fill (theme) | ⛔ per-row override out of scope |

- [x] all properties verified or added

## TabBar (tabs.dart) → MdTabs (widgets/tabs) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `tabs` | `add_tab(label, *, icon)` | ✅ |
| `controller` (selected index) | `selected_index` @property + `set_selected_index(i)` | ➕ |
| `onTap` | `changed(int)` Signal | ✅ |
| `isScrollable` | `scrollable` ctor kwarg + `is_scrollable` @property + `set_scrollable(bool)` (QScrollArea, natural-width tabs, auto-scroll-to-selected) | 🆕 |
| `indicatorColor` | `set_indicator_color(QColor|None)` (None → `primary` role) | ➕ |
| `indicatorWeight` | `set_indicator_weight(px)` (0 → 3px primary / 2px secondary) | ➕ |
| `indicatorSize` | `set_indicator_size("tab"/"label")` | ➕ |
| `labelColor` | `set_label_color(QColor|None)` | ➕ |
| `unselectedLabelColor` | `set_unselected_label_color(QColor|None)` | ➕ |
| `dividerColor` | `set_divider_color(QColor|None)` (None → `surface-container-highest`) | ➕ |
| (primary vs secondary — Qt option) | `secondary` ctor kwarg | ✅ |
| `dividerHeight` | 1px line | ⛔ spec-fixed |
| `padding` / `labelPadding` / `indicatorPadding` | token spacing | ⛔ layout-padding framework idiom |
| `automaticIndicatorColorAdjustment` | — | ⛔ tied to Flutter's `indicatorColor` auto-contrast logic |
| `labelStyle` / `unselectedLabelStyle` | title-small typescale token | ⛔ `TextStyle` framework idiom |
| `scrollController` / `physics` / `dragStartBehavior` | QScrollArea handles wheel/clip | ⛔ Flutter scroll-physics idioms |
| `overlayColor` / `splashFactory` / `splashBorderRadius` / `mouseCursor` | ripple + pointing cursor (built-in) | ⛔ `WidgetStateProperty`/ink framework idioms |
| `enableFeedback` / `onHover` / `onFocusChange` | hover/focus via QWidget events | ⛔ haptic/per-tab hover callbacks framework idioms |
| `indicator` / `tabAlignment` / `textScaler` / `indicatorAnimation` | spec indicator + emphasized motion | ⛔ framework idioms / spec-fixed |

- [x] all properties verified or added

### Tab (tabs.dart) → MdTab (widgets/tabs) — covered ✅

| Flutter property | Qt equivalent | Status |
|---|---|---|
| `text` | `label` positional / `setText` | ✅ |
| `icon` | `icon` ctor kwarg (stacked above label on primary tabs) | ✅ |
| `child` | — | ⛔ MdTab is a painted QAbstractButton (icon+label); it does not host an arbitrary child widget. Use `text`/`icon` |
| `iconMargin` / `height` | token spacing + fixed 48px | ⛔ spec-fixed |

- [x] all properties verified or added
