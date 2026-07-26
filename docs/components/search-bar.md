# Search

Field for searching app content.

**Classes:** `MdSearchBar`, `MdSearchView`, `SuggestionsProvider` · **Source:** `src/material_qt/widgets/searchbar/`
**Spec:** https://m3.material.io/components/search. The module docstrings name Flutter's `SearchBar` and the view half of `SearchAnchor` (`search_anchor.dart`) as the upstream counterparts.

`MdSearchBar` is the docked resting state: a fully-rounded `surface-container-high` bar with a leading search icon, a borderless input, and an optional trailing action icon. `MdSearchView` is the overlay that opens when the bar is tapped: a header (back affordance, editable query field, clear button) above a divider and a live-updating suggestion list.

## Usage

```python
from material_qt import MdSearchBar, MdSearchView

fruits = ["Apple", "Apricot", "Avocado", "Banana", "Blueberry", "Cherry"]

bar = MdSearchBar(placeholder="Search fruit", trailing_icon="mic")
bar.submitted.connect(lambda q: print("Searched:", q))
bar.trailingClicked.connect(lambda: print("Voice search..."))

view = MdSearchView(
    window,  # the widget the overlay fills
    view_hint_text="Search fruit",
    suggestions_provider=lambda q: [f for f in fruits if q.lower() in f.lower()],
)
bar.clicked.connect(view.open)
view.suggestionSelected.connect(bar.set_text)
```

## API

### MdSearchBar

```python
MdSearchBar(
    parent: QWidget | None = None,
    *,
    placeholder: str = "Search",
    leading_icon: str = "search",
    trailing_icon: str = "",
    elevation: ElevationLevel | int = ElevationLevel.LEVEL0,
)
```

- `text()` / `set_text(text)` / `set_placeholder(text)` — read/write the query and hint.
- `line_edit` — escape hatch: the underlying `QLineEdit` (e.g. to drive a suggestions dropdown).
- **Signals:** `textChanged = Signal(str)`, `submitted = Signal(str)` (Enter), `clicked = Signal()` (the bar was tapped — the cue to open the search view), `trailingClicked = Signal()` (the trailing action icon was tapped).

### MdSearchView

```python
MdSearchView(
    parent: QWidget,
    *,
    view_hint_text: str = "Search",
    leading_icon: str = "arrow_back",
    suggestions_provider: SuggestionsProvider | None = None,
    full_screen: bool = True,
)
```

- `open()` — show the overlay and focus the query field (typically wired to `MdSearchBar.clicked`).
- `text()` / `set_text(text)` / `set_placeholder(text)` — read/write the query and hint.
- `set_suggestions_provider(provider)` — set the `query -> suggestions` callable and refresh the list.
- `set_suggestions(suggestions)` / `suggestions()` — the manual path: replace / read the current suggestion list.
- Inherited from `ModalOverlay`: the scrim/fade, Escape-to-dismiss, `dismiss()`, and the `rejected` / `closed` signals on dismissal.
- **Signals:** `textChanged = Signal(str)`, `submitted = Signal(str)`, `suggestionSelected = Signal(str)` (the user picked a suggestion; the view then closes).

### SuggestionsProvider

```python
SuggestionsProvider = Callable[[str], Iterable[str]]
```

A plain callable mapping the current query to suggestion strings (Flutter's `suggestionsBuilder`; it returns data, so it is a callable rather than a Signal).

## Notes

- The bar's trailing icon is an interactive `MdIconButton`, not part of the bar's tap target: tapping it fires `trailingClicked`, not `clicked`. A press anywhere else on the bar (input, chrome, icons, padding) fires `clicked`.
- Icons are Material Symbols ligature names (`leading_icon="search"`, `trailing_icon="mic"`), never `QIcon`.
- `elevation` collapses Flutter's `WidgetStateProperty<double?>` to a single resting `ElevationLevel`. Flutter's `controller` maps to `text()` / `set_text()` plus `textChanged`.
- `MdSearchView` requires a parent widget — it is an overlay that fills (full-screen) or top-anchors on that parent. Non-full-screen mode is a simplification: a top-anchored surface spanning the width, capped at about 2/3 height (the source notes Flutter's anchored-to-bar geometry as a follow-up).
- Flutter `SearchAnchor` `view*` mapping (from the docstring): `viewHintText` → `view_hint_text` / `set_placeholder`; `viewLeading` → the built-in back affordance (`leading_icon`); `viewTrailing` → the built-in clear button; `viewOnChanged` / `viewOnSubmitted` → `textChanged` / `submitted`; `isFullScreen` → `full_screen`.
- The gallery's search-bar page shows the alternative desktop pattern — a suggestion dropdown anchored under the bar via the shared `DropdownController` — instead of the full-screen view.
- There is no package demo module; the component pages live in the gallery. See [../usage.md](../usage.md) to run it, and [text field](./text-field.md) for general-purpose input.
