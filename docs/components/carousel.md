# Carousel

Scrollable row of contained items.

**Classes:** `MdCarousel`, `MdWeightedCarousel` · **Source:** `src/material_qt/widgets/carousel/`
**Spec:** [m3.material.io/components/carousel](https://m3.material.io/components/carousel). The module docstring names Flutter's `CarouselView` as the upstream counterpart: `MdCarousel` is the uncontained layout, `MdWeightedCarousel` the weighted multi-browse / hero layouts.

## Usage

```python
from material_qt import MdCarousel, MdWeightedCarousel

names = ["Beach", "Mountain", "Forest", "City", "Desert", "Lake"]

carousel = MdCarousel(parent)
for name in names:
    carousel.add_tile(name)
carousel.indexChanged.connect(lambda i: print("showing", names[i]))

multi = MdWeightedCarousel(parent, weights=[3, 2, 1])   # multi-browse
for name in names:
    multi.add_tile(name)
multi.itemTapped.connect(lambda i: print("tapped", names[i]))
```

## API

### MdCarousel

```python
MdCarousel(
    parent: QWidget | None = None,
    *,
    item_extent: int = 150,
    item_height: int = 180,
    item_snapping: bool = True,
    padding: int = 0,
    scroll_direction: Qt.Orientation = Qt.Orientation.Horizontal,
)
```

- `add_item(widget)` — append an arbitrary widget to the strip.
- `add_tile(label)` — append (and return) a default tile: a `primary-container` rounded panel with a label, sized `item_extent` × `item_height`.
- `count()` — number of items.
- `item_extent` (property) — width of default tiles and the snap stride (Flutter `itemExtent`).
- `item_snapping` (property) / `set_item_snapping(enabled)` — whether releasing a drag settles on an item's leading edge (Flutter `itemSnapping`).
- `current_index` (property) — index of the leading visible item.

**Signals:**

- `indexChanged = Signal(int)` — the leading visible item changed (Flutter's `onIndexChanged`). Note the Qt-style name; this widget does not use the `changed(int)` convention of the navigation widgets.

### MdWeightedCarousel

```python
MdWeightedCarousel(
    parent: QWidget | None = None,
    *,
    weights: list[int] = [3, 2, 1],
    consume_max_weight: bool = True,
)
```

- `add_item(widget)` / `add_tile(label)` / `count()` / `current_index` — as above; `add_tile` returns a variable-width flex tile cycling through the container palettes.
- `p` (Qt `Property(float)`, via `get_p()` / `set_p(value)`) — the continuous scroll position driving the layout; animatable, clamped to the valid range.

**Signals:**

- `indexChanged = Signal(int)` — the leading item changed.
- `itemTapped = Signal(int)` — an item was clicked rather than dragged.

The pure helper `weighted_geometry(p, n, weights, width)` (importable from `material_qt.widgets.carousel.carousel`) computes the `(index, left, width)` tiling for a given scroll position.

## Notes

- `MdCarousel` is built on a `QScrollArea` with both scrollbars hidden: kinetic drag/swipe (via `QScroller`) and the wheel are the scrolling affordances, and it hosts its own horizontal scroll area so it drops into a vertically scrolling page without the two directions fighting. A wheel notch advances exactly one item; a plain click still activates an item (e.g. a tile's ripple).
- `item_snapping` defaults to `True` here even though Flutter defaults `itemSnapping` to `False` — snapping is treated as the carousel's defining affordance in this port. Disabling it makes drags scroll freely; positions are still tracked for `indexChanged`.
- Horizontal only: passing any other `scroll_direction` raises `ValueError`. The widget fixes its own height to `item_height + 16 + 2 * padding`.
- `MdWeightedCarousel` positions children manually (no `QLayout` and no scroll area): items resize as they scroll, per `weights` — e.g. `[3, 2, 1]` multi-browse, `[1, 7, 1]` centre-hero. Slot widths are relative shares of the content width, and the tiling always sums exactly to it (no gaps or overlaps).
- `consume_max_weight=True` (the default, matching Flutter's `consumeMaxWeight`) lets the first and last items expand into the max-weight slot at the ends of the scroll, emptying the small edge slots. Set it `False` to keep the viewport full instead: edge items stay at their slot size and the scroll range shrinks accordingly.
- In the weighted carousel a press only becomes a drag after 4 px of horizontal movement; anything less counts as a tap and emits `itemTapped`. Its flex tiles are transparent to mouse events (so the carousel gets the drag), which also means weighted tiles have no ripple.
- Releasing a weighted drag (or a wheel notch) animates `p` to the nearest whole index with emphasized easing.
- Deferred: the weighted layouts are not part of `MdCarousel` itself (use `MdWeightedCarousel`), and vertical scrolling is not implemented.
