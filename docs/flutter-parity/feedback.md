# Progress & feedback — Flutter ↔ material_qt parity

Status legend: ✅ verified · ➕ added this pass · 🆕 built this pass · ⛔ N/A (rationale)

Scope: only the task-named properties are ported. The long tail of Flutter
constructor params (semantics, deprecated `year2023` flags, `controller`,
rich/decoration overrides, etc.) is dispatched as ⛔ N/A — these are
web/Flutter-framework concerns, not part of the QObject port's surface.

## LinearProgressIndicator (progress_indicator.dart) → MdLinearProgress (widgets/progress) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `value` (null = indeterminate) | `value` / `set_value()` + `indeterminate` / `set_indeterminate()` | ✅ |
| `color` / `valueColor` | `color_role` / `set_color_role()` (default `PRIMARY`) | ➕ |
| `backgroundColor` (track) | `track_role` / `set_track_role()` (default `SURFACE_CONTAINER_HIGHEST`) | ➕ |
| `minHeight` | `min_height` / `set_min_height()` (drives sizeHint + paint thickness) | ➕ |
| `borderRadius` | `border_radius` / `set_border_radius()` (default = half thickness) | ➕ |
| `semanticsLabel` / `semanticsValue` | — | ⛔ Qt a11y handled via QAccessible, not a paint prop |
| `stopIndicatorColor` / `stopIndicatorRadius` / `trackGap` | — | ⛔ 2024 M3-expressive detail; out of scope |
| `year2023` | — | ⛔ deprecated Flutter migration flag |
| `controller` | — | ⛔ Flutter AnimationController; Qt uses internal QVariantAnimation |

## CircularProgressIndicator (progress_indicator.dart) → MdCircularProgress (widgets/progress) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `value` (null = indeterminate) | `value` / `indeterminate` (shared `_ProgressBase`) | ✅ |
| `color` / `valueColor` | `color_role` / `set_color_role()` (default `PRIMARY`) | ➕ |
| `backgroundColor` (track) | `track_role` / `set_track_role()` (default `SURFACE_CONTAINER_HIGHEST`) | ➕ |
| `strokeWidth` | `stroke_width` / `set_stroke_width()` (drives pen width + margin) | ➕ |
| (size) | `size` ctor kwarg | ✅ |
| `strokeAlign` / `strokeCap` | RoundCap fixed | ⛔ minor stroke detail; round cap matches M3 default |
| `constraints` / `padding` | Qt sizeHint / layout margins | ⛔ Flutter layout concern |
| `trackGap` / `year2023` | — | ⛔ 2024-expressive / deprecated flag |

## LoadingIndicator (M3 Expressive) → MdLoadingIndicator (widgets/loadingindicator) — covered ✅ (M3-expressive)

| Flutter / M3 concept | Qt equivalent | Status |
|---|---|---|
| morphing shape spinner | `MdLoadingIndicator` (`start`/`stop`, `is_running`, drivable `t`) | ✅ M3-expressive scaffold |
| active shape color | `PRIMARY` (live from theme) | ✅ |
| continuous loop | `QVariantAnimation` `setLoopCount(-1)` | ✅ |
| true 7-shape spring morph | approximated by lobe-count cookie morph | ⛔ deferred; noted M3-expressive |

(No Flutter `loading_indicator.dart` constructor; this tracks the M3 Expressive
component. Color-role override not added — left as a follow-up if needed.)

## Badge (badge.dart) → MdBadge (widgets/badge) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `label` (Widget) | `value` / `set_value()` (string; empty = dot) — kept canonical name | ✅ |
| `isLabelVisible` | `is_label_visible` / `set_label_visible()` (hides badge on host) | ➕ |
| `alignment` (default topEnd) | `alignment` / `set_alignment()` (default top-right) | ➕ |
| `offset` | `offset` / `set_offset()` (`QPoint`) | ➕ |
| `backgroundColor` | `background_role` / `set_background_role()` (default `ERROR`) | ➕ |
| `textColor` | `text_role` / `set_text_role()` (default `ON_ERROR`) | ➕ |
| `child` (anchor) | `attach(host)` overlay (reparent + track) | ✅ |
| `smallSize` / `largeSize` / `padding` / `textStyle` | token-driven (6px dot / 16px pill) | ⛔ M3 token sizing, not exposed |
| `Badge.count(count, maxCount)` | — | ⛔ convenience ctor; `set_value(str(n))` suffices |

## Tooltip (tooltip.dart) → MdTooltip (widgets/tooltip) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `message` | `text` ctor + `set_text()` | ✅ |
| `waitDuration` | `wait_ms` (default 500) | ✅ |
| `showDuration` | `show_ms` (default 1500) | ✅ |
| `preferBelow` | `prefer_below` / `set_prefer_below()` (flips side, clip-aware) | ➕ |
| `margin` | `margin` / `set_margin()` (window-edge inset in positioning) | ➕ |
| `verticalOffset` | fixed `_GAP` (8px) | ⛔ constant gap matches M3 |
| `richMessage` / `decoration` / `textStyle` / `textAlign` | token-styled label | ⛔ token-driven styling |
| `triggerMode` / `enableTapToDismiss` / `onTriggered` / `mouseCursor` | hover trigger + press-to-dismiss | ⛔ Flutter gesture config |
| `exitDuration` / `enableFeedback` / `ignorePointer` / `positionDelegate` / `constraints` / `height` | — | ⛔ Flutter-framework / deprecated |

## MaterialBanner (banner.dart) → MdBanner (widgets/banner) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `content` | `text` ctor + wrapped `body-medium` label | ✅ |
| `leading` | `icon` ctor (leading `MdIcon`, `PRIMARY`) | ✅ |
| `actions` | `add_action(text) -> MdTextButton` (connect `clicked`) | ✅ |
| `elevation` | `elevation` ctor + `elevation` prop + `set_elevation()` (via mixin) | ➕ |
| `backgroundColor` | `background_role` / `set_background_role()` (default `SURFACE`) | ➕ |
| `dividerColor` | `divider_role` / `set_divider_role()` (default `OUTLINE_VARIANT`) | ➕ |
| `contentTextStyle` | token `body-medium` / `on-surface` | ⛔ token-driven |
| `surfaceTintColor` / `shadowColor` | mixin elevation shadow | ⛔ Flutter tint/shadow split not modeled |
| `padding` / `margin` / `leadingPadding` | fixed 16px (`_PAD`) | ⛔ M3 token padding |
| `forceActionsBelow` / `overflowAlignment` / `minActionBarHeight` | single trailing action row | ⛔ Flutter OverflowBar layout |
| `animation` / `onVisible` | — | ⛔ Flutter Scaffold-controller concern |

## RefreshIndicator (refresh_indicator.dart) → MdRefreshIndicator (widgets/refreshindicator) — built 🆕

| Flutter property / API | Qt (QObject) equivalent | Status |
|---|---|---|
| `child` (scrollable) | `child` ctor + `set_child()` / `child` prop | 🆕 |
| `onRefresh` (Future callback) | `refresh` **Signal** (emitted on trigger) | 🆕 |
| `displacement` (default 40) | `displacement` / `set_displacement()` | 🆕 |
| `color` | `color_role` / `set_color_role()` (default `PRIMARY`, themes spinner) | 🆕 |
| (spinner) | indeterminate `MdCircularProgress` (size 36) — reused, inherits `setLoopCount(-1)` | 🆕 |
| pull-to-refresh gesture | drag on child past threshold → `trigger()`; programmatic `begin()` / `trigger()` / `end()` / `finish()` | 🆕 |
| `show({atTop})` | `begin()` (reveal, no signal) / `trigger()` (reveal + emit) | 🆕 |
| dismiss | `end()` / `finish()` (alias) + `is_refreshing` state | 🆕 |
| `RefreshIndicator.adaptive` (Cupertino) | — | ⛔ iOS/macOS platform variant; N/A on Qt desktop |
| `edgeOffset` | — | ⛔ scroll-edge inset; gesture is best-effort headlessly |
| `strokeWidth` | spinner default | ⛔ minor; spinner stroke fixed |
| `triggerMode` (onEdge/anywhere) | drag-from-top heuristic | ⛔ scroll-position semantics not modeled |
| `elevation` | spinner has no card shadow | ⛔ M3 2024 spinner has no elevation surface |
| `notificationPredicate` / `onStatusChange` / `semanticsLabel` / `semanticsValue` | — | ⛔ Flutter ScrollNotification / a11y framework |

- [x] all properties verified or added
- [ ] Coordinator follow-up: register `MdRefreshIndicator` in `gallery/gallery.py`
- [ ] Coordinator follow-up: export `MdRefreshIndicator` from `widgets/core` (or `widgets/__init__.py`) alongside the other progress/feedback widgets
- [ ] Coordinator follow-up: `MdBanner` sets `MdDivider._color_role` directly (private) because `MdDivider` has no public setter; add `set_color_role()` to `MdDivider` (widgets/divider) and switch the banner to it
- [ ] Coordinator follow-up (optional): expose a `color_role` override on `MdLoadingIndicator` if theming flexibility is wanted
