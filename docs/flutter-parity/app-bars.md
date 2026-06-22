# App bars & toolbars — Flutter ↔ material_qt parity

Status legend: ✅ verified · ➕ added this pass · 🆕 built this pass · ⛔ N/A (rationale)

Scope: Flutter `app_bar.dart` (`AppBar` + `SliverAppBar`) and `bottom_app_bar.dart`
(`BottomAppBar`) mapped onto `material_qt` `widgets/topappbar`, `widgets/toolbar`,
and the new `widgets/bottomappbar`. Conventions: callbacks → Qt Signals,
`set_*()` / `@property` / constructor kwargs, theme-role colors (no raw `QColor`
overrides).

## AppBar (app_bar.dart) → MdTopAppBar (widgets/topappbar) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `leading` | `leading=` ctor kwarg (a `QWidget`, typically `MdIconButton`) | ✅ |
| `title` | `title=` ctor kwarg / `set_title(str)` | ✅ |
| `actions` | `add_action(icon, *, toggle=False) -> MdIconButton` (button exposes `clicked`) | ✅ |
| `centerTitle` | `variant=TopAppBarVariant.CENTER` (centered title is a distinct M3 variant, not a bool) | ✅ |
| `backgroundColor` | `surface` role fill, tinting `surface → surface-container` on scroll-under (theme-role, not raw color) | ✅ |
| `elevation` | base `LEVEL0` (M3 flat at rest) | ✅ |
| `scrolledUnderElevation` | `scrolled_under_elevation=` ctor kwarg (default `LEVEL3`); applied when `collapse_fraction > 0` | ➕ |
| `toolbarHeight` | `toolbar_height=` ctor kwarg (overrides the 64px per-row height; shifts every variant's expanded height by the delta) | ➕ |
| `bottom` | `bottom=` ctor kwarg / `set_bottom(widget)` — persistent sub-row (e.g. a tab bar) below the toolbar rows; not collapsed | ➕ |
| (SliverAppBar) `pinned` | `attach_scroll_area()` / `set_collapse_fraction()` — collapse-and-stay is the default scroll-under behavior | ✅ (mapped) |
| (SliverAppBar) `floating` / `snap` | mapped onto the existing collapse fraction; directional reveal-on-scroll-up physics intentionally not built (drive `set_collapse_fraction` from your own scroll logic for reveal) | ⛔ (see note) |
| (SliverAppBar) `expandedHeight` | implied by `variant` (CENTER/SMALL 64, MEDIUM 112, LARGE 152) + `toolbar_height` | ✅ |
| (SliverAppBar) `collapsedHeight` | the per-row `toolbar_height` (64 default); collapse target | ✅ |
| `shape` | `set_radii()` via MaterialWidgetMixin (M3 top app bars are square — `ShapeScale.NONE`) | ✅ |

### Mapped / documented (no new behavior)

- `centerTitle` → CENTER variant (above).
- `pinned` → collapse-and-stay (`attach_scroll_area`).
- `floating`/`snap`/`stretch`/`stretchTriggerOffset` → reveal-on-scroll-up
  physics belong to a scroll coordinator; the collapse API (`set_collapse_fraction`
  0..1) is the seam to drive them. Not replicated as automatic physics here.

### N/A (framework plumbing — deliberately omitted)

- ⛔ `automaticallyImplyLeading` / `automaticallyImplyActions` — Scaffold/route
  inference; Qt has no implicit route stack, leading is explicit.
- ⛔ `flexibleSpace` — Sliver flexible-space delegate; the bottom slot + collapse
  cover the M3 use cases.
- ⛔ `notificationPredicate` — `ScrollNotification` filtering; Qt drives collapse
  from a `QScrollBar` directly.
- ⛔ `shadowColor` / `surfaceTintColor` — theme-role colors only; surface tint is
  the `surface → surface-container` lerp, shadow is the elevation drop-shadow.
- ⛔ `foregroundColor` / `iconTheme` / `actionsIconTheme` / `toolbarTextStyle` /
  `titleTextStyle` — fg is `on-surface` from the theme; icon/text styling is the
  child widgets' own (theme-role) concern.
- ⛔ `primary` / `systemOverlayStyle` — status-bar / safe-area system chrome; not
  applicable to desktop QtWidgets.
- ⛔ `excludeHeaderSemantics` / `useDefaultSemanticsOrder` — Flutter semantics
  tree; Qt uses its own accessibility layer.
- ⛔ `toolbarOpacity` / `bottomOpacity` — Sliver scroll-fade internals; the
  cross-fade is handled inside `set_collapse_fraction`.
- ⛔ `forceMaterialTransparency` / `animateColor` / `clipBehavior` / `titleSpacing`
  / `leadingWidth` / `actionsPadding` — fine-grained layout/paint knobs not part
  of the M3 surface contract; layout uses the M3 16px padding.

- [x] all properties verified, added, or marked N/A with rationale

## Toolbar (M3-Expressive) → MdToolbar (widgets/toolbar) — covered ✅

`MdToolbar` is the **M3-Expressive** toolbar (a floating or docked action-row
pill), not a Flutter `AppBar`. Flutter has no direct equivalent. It covers:

| Capability | Qt equivalent | Status |
|---|---|---|
| Floating pill (rounded, level-3, `surface-container`) | `variant=ToolbarVariant.FLOATING` | ✅ |
| Docked bar (less rounded, flat) | `variant=ToolbarVariant.DOCKED` | ✅ |
| Action icon buttons | `add_action(icon, *, toggle) -> MdIconButton` | ✅ |
| Count | `count()` | ✅ |

It does **not** host a cradled FAB or a bottom-pinned action bar → that is
`BottomAppBar`, built below.

## BottomAppBar (bottom_app_bar.dart) → MdBottomAppBar (widgets/bottomappbar) — built 🆕

Not covered by `MdToolbar` (which is the floating/docked Expressive pill with no
FAB notch). Built `MdBottomAppBar`: a bottom-pinned bar hosting leading action
icon buttons + an optional trailing `MdFab`, with an optional notch cradling the
FAB. Defaults follow the M3 token block in `bottom_app_bar.dart`.

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `child` (action row) | `add_action(icon, *, toggle) -> MdIconButton`; leading actions ordered before the trailing FAB | 🆕 |
| (FAB pairing) `FloatingActionButtonLocation.endContained` | `set_fab(MdFab \| None)` / `fab` property — trailing, end-cradled. Departure: Flutter's `Scaffold` owns the FAB as a sibling and feeds its geometry to the bar; this widget hosts and positions the FAB itself (trailing, top-aligned, within bounds) so the notch cradles it without overhang/clipping | 🆕 |
| `shape` (`NotchedShape`) | `notch=` ctor kwarg / `set_notch(bool)` / `notch` property — rounded cut at the FAB center | 🆕 |
| `notchMargin` | constant `4.0` (M3 default; matches Flutter's `notchMargin` default) | 🆕 |
| `height` | `height=` ctor kwarg (default 80, M3 default) | 🆕 |
| `color` | `surface-container` role (theme-role; matches M3 `ColorScheme.surfaceContainer`) | 🆕 |
| `elevation` | `elevation=` ctor kwarg (default `LEVEL3`, M3 default) | 🆕 |
| `padding` | M3 default `EdgeInsets.symmetric(vertical: 12, horizontal: 16)` baked into the layout | 🆕 |
| `surfaceTintColor` / `shadowColor` | ⛔ theme-role only (tint via theme, shadow via elevation drop-shadow) | ⛔ |
| `clipBehavior` | ⛔ Flutter `PhysicalShape` clip knob; not part of the M3 surface contract | ⛔ |

- [x] all properties verified, added, or marked N/A with rationale

## Coordinator follow-up

- **Export `MdBottomAppBar`**: add to `qt/src/material_qt/widgets/__init__.py`
  (and `widgets/bottomappbar` is already a package with its own `__init__.py`).
  Not edited here per the shared-file rule.
- **Register in gallery**: add an `MdBottomAppBar` demo (leading actions + FAB,
  notch on/off) to `gallery/gallery.py`. Not edited here per the shared-file rule.
- The `MdTopAppBar` `bottom` slot pairs naturally with `MdTabs` for the gallery
  demo (tab bar under a top app bar).
