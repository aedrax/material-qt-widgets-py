# Search — Flutter ↔ material_qt parity

Status legend: ✅ verified · ➕ added this pass · 🆕 built this pass · ⛔ N/A (rationale)

Flutter reference: `flutter/.../material/search_anchor.dart` (defines both
`SearchBar` — the docked field — and `SearchAnchor` — the full-screen / view
search surface). Qt: `qt/src/material_qt/widgets/searchbar/`
(`MdSearchBar`, `MdSearchView`).

Idiom mapping: Flutter callbacks → Qt Signals; `WidgetStateProperty<T>` →
single resting value (Qt widgets repaint per interaction state without a
declarative state map); theme-role colors via `ThemeManager`/`ColorRole`.

## SearchBar (search_anchor.dart) → MdSearchBar (widgets/searchbar) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `onChanged: ValueChanged<String>` | `textChanged(str)` Signal | ✅ |
| `onSubmitted: ValueChanged<String>` | `submitted(str)` Signal (Enter) | ✅ |
| `onTap: GestureTapCallback` | `clicked()` Signal (press on field via event filter, or on chrome) | ➕ |
| `hintText: String?` | `placeholder=` ctor kwarg + `set_placeholder()` | ✅ |
| `controller: TextEditingController?` | `text()` / `set_text()` + `textChanged` Signal (no separate controller object) | ✅ (mapped) |
| `leading: Widget?` | `leading_icon=` ctor kwarg (default `"search"`; `""` omits it) | ➕ |
| `trailing: Iterable<Widget>?` | `trailing_icon=` ctor kwarg (single icon — bar spec allows ≤2; one covered) | ✅ |
| `elevation: WidgetStateProperty<double?>` | `elevation=` ctor kwarg (`ElevationLevel`; collapses the state map to one resting level) | ➕ |
| `backgroundColor` | fixed `SURFACE_CONTAINER_HIGH` via theme role (M3 default) | ✅ (role) |
| `focusNode` | Qt focus is intrinsic to the `QLineEdit` | ⛔ (framework intrinsic) |
| `onTapOutside`, `constraints`, `shadowColor`, `surfaceTintColor`, `overlayColor`, `side`, `shape`, `padding`, `textStyle`, `hintStyle`, `textCapitalization`, `autoFocus`, `textInputAction`, `keyboardType`, `scrollPadding`, `contextMenuBuilder`, `readOnly`, `smartDashesType`, `smartQuotesType`, `enabled` | — | ⛔ (styling/IME/text-edit knobs out of the M3-role port's scope) |

## SearchAnchor view (search_anchor.dart) → MdSearchView (widgets/searchbar) — built 🆕

`MdSearchView` subclasses `core.ModalOverlay` (inherits scrim/fade,
Escape-to-dismiss, parent-resize tracking, drop-focus-before-hide, and
`rejected`/`closed`). `_center_panel` is overridden so the panel fills the
parent (full-screen) or anchors to the top (non-full-screen). Open it via
`open()` (inherited), typically wired to `MdSearchBar.clicked`.

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| opens from the bar | `view.open()` ← wire to `MdSearchBar.clicked` Signal | 🆕 |
| `viewLeading` (default back button) | built-in back affordance (`MdIconButton`, `leading_icon="arrow_back"`) → `dismiss()` | 🆕 |
| editable query | header `QLineEdit` (`body-large`) → `text()`/`set_text()` | 🆕 |
| `viewHintText: String?` | `view_hint_text=` ctor kwarg + `set_placeholder()` | 🆕 |
| `viewTrailing` (default clear) | built-in clear `MdIconButton("close")` empties the field | 🆕 |
| `suggestionsBuilder: SuggestionsBuilder` | `suggestions_provider: (query) -> Iterable[str]` ctor kwarg / `set_suggestions_provider()` — data, so a plain callable not a Signal; refreshes live on every query change | 🆕 |
| (manual suggestion set) | `set_suggestions(list)` + `suggestions()` getter | 🆕 |
| scrollable suggestion list | `QScrollArea` over a rebuilt `MdListItem` list (own layout; `MdList` isn't editable here / not scrollable) | 🆕 |
| selecting a suggestion | `suggestionSelected(value)` Signal, then close (does not set bar text — left to the wiring) | 🆕 |
| `viewOnChanged` | `textChanged(str)` Signal | 🆕 |
| `viewOnSubmitted` | `submitted(str)` Signal | 🆕 |
| `viewOnClose` / `viewOnOpen` | inherited `closed()` / call-site of `open()` | 🆕 |
| `isFullScreen: bool?` | `full_screen=` ctor kwarg (default `True`) | 🆕 |
| `viewBackgroundColor` / `viewElevation` | `SURFACE_CONTAINER_HIGH` + `ElevationLevel.LEVEL3` (M3 defaults) | 🆕 (role/token) |
| `viewBuilder`, `viewSurfaceTintColor`, `viewSide`, `viewShape`, `viewBarPadding`, `headerHeight`, `headerTextStyle`, `headerHintStyle`, `dividerColor`, `viewConstraints`, `viewPadding`, `shrinkWrap`, `textCapitalization`, `textInputAction`, `keyboardType`, `smartDashesType`, `smartQuotesType`, `enabled` | — | ⛔ (styling/IME knobs out of scope) |

### Notes / known simplifications
- Non-full-screen mode (`full_screen=False`) renders a top-anchored,
  full-width panel capped to ~2/3 parent height — a simplification of
  Flutter's precise anchor-to-bar geometry.
- `elevation` / `WidgetStateProperty` maps collapse to single resting values;
  Qt repaints per interaction state without a declarative state map.

- [x] all properties verified or added
- [ ] Coordinator follow-up: register/showcase the search view in the gallery
  (`gallery/gallery.py`) — e.g. an `MdSearchBar` whose `clicked` opens an
  `MdSearchView` with a demo suggestions provider; export `MdSearchView` /
  `SuggestionsProvider` from `widgets/__init__.py`. (`searchbar/__init__.py`
  already exports them.)
