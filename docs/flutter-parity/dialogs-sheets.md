# Dialogs & sheets — Flutter ↔ material_qt parity

Status legend: ✅ verified · ➕ added this pass · 🆕 built this pass · ⛔ N/A (rationale)

Scope: Flutter `dialog.dart` (Dialog/AlertDialog/SimpleDialog), `bottom_sheet.dart`
(BottomSheet + `showModalBottomSheet`), `snack_bar.dart` (SnackBar/SnackBarAction),
and the M3 side-sheet spec. Qt widgets live under
`qt/src/material_qt/widgets/{dialog,bottomsheet,sidesheet,snackbar}`.

The dialog and the date/time pickers share `core.ModalOverlay` (scrim/fade,
`open()`/`_close()`/`dismiss()`, `rejected`/`closed` Signals, drop-focus-before-hide).
The base is **not edited** here; `MdDialog` overrides the dismiss-triggering event
handlers locally to gate barrier dismissal. The sheets reimplement the scrim/slide
pattern in their own files.

Naming note: the class is `MdSnackbar` (lower-case *b*), matching the existing
module and `widgets/__init__.py` export; not renamed to `MdSnackBar` (would touch
the forbidden shared `__init__.py`/gallery).

---

## AlertDialog / Dialog (dialog.dart) → MdDialog (widgets/dialog) — covered ✅
| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `icon` | `MdDialog(icon=...)` → centered `MdIcon` (secondary role) | ✅ |
| `title` (widget) | `MdDialog(headline=...)` → `headline-small` label | ✅ |
| `content` (widget) | `MdDialog(supporting_text=...)` + `add_content(widget)` | ✅ |
| `actions` | `add_action(text, accept=True/False/None)` → `MdTextButton` | ✅ |
| (confirm) | `accepted` Signal (base contract) + auto `_close` | ✅ |
| (cancel/scrim/Escape) | `rejected` Signal (base) via `dismiss()` | ✅ |
| (close fired) | `closed` Signal (base) | ✅ |
| `barrierDismissible` (`showDialog`) | `barrier_dismissible` kwarg + `set_barrier_dismissible()`; gates scrim-click **and** Escape by overriding `mousePressEvent`/`keyPressEvent` locally | ➕ |
| `backgroundColor` | theme-role owned (`surface-container-high`) | ⛔ theme-role owned |
| `elevation` | theme-role owned (level-3, drop shadow) | ⛔ theme-role owned |
| `shadowColor` / `surfaceTintColor` | derived from elevation tokens | ⛔ theme-role owned |
| `shape` | corner-extra-large token | ⛔ token-owned |
| `iconColor` / `iconPadding` | role + fixed M3 padding | ⛔ token-owned |
| `titleTextStyle` / `titlePadding` | `headline-small` typescale + 24px pad | ⛔ token-owned |
| `contentTextStyle` / `contentPadding` | `body-medium` typescale + 24px pad | ⛔ token-owned |
| `actionsAlignment` / `actionsPadding` / `buttonPadding` | right-aligned row, fixed spacing | ⛔ not idiomatic in Qt |
| `actionsOverflow*` | Qt row does not overflow-stack | ⛔ not idiomatic in Qt |
| `insetPadding` / `alignment` | overlay centers the panel; `_panel_width()` clamps | ⛔ layout-owned |
| `clipBehavior` | panel paints its own clipped surface | ⛔ N/A |
| `constraints` | `_panel_width()` clamps 280–560 (M3 spec) | ⛔ token-owned |
| `semanticLabel` / `semanticsRole` | a11y, out of scope this pass | ⛔ out of scope |
| `insetAnimationDuration/Curve` | base drives fade+slide via motion tokens | ⛔ token-owned |
| `scrollable` | `add_content` accepts any widget (incl. a scroll area) | ⛔ caller-owned |

- [x] all properties verified or added

## SimpleDialog (dialog.dart) → MdDialog options — covered ✅
| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `title` | `headline=` (same as AlertDialog) | ✅ |
| `children` (`SimpleDialogOption`s) | `add_option(text)` → full-width, left-aligned, flat `QPushButton`; returns the button so caller wires `clicked` | ➕ |
| `SimpleDialogOption.onPressed` | the returned button's `clicked` Signal | ➕ |
| `SimpleDialogOption.child` | text label (icon/custom child not modelled) | ⛔ minimal port |
| `SimpleDialogOption.padding` | fixed 12px row padding | ⛔ token-owned |
| `titlePadding` / `contentPadding` / `*TextStyle` | token-owned (see AlertDialog) | ⛔ token-owned |

- [x] all properties verified or added

## BottomSheet / showModalBottomSheet (bottom_sheet.dart) → MdBottomSheet (modal) — covered ✅
| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| (slide-up panel) | `open()` slides up from bottom edge | ✅ |
| (content) | `add_content(widget)` | ✅ |
| `onClosing` | `closed` Signal | ✅ |
| `isDismissible` | `is_dismissible` kwarg + `set_dismissible()`; gates scrim-click and Escape | ➕ |
| `showDragHandle` | `show_drag_handle` kwarg; toggles the handle paint **and** shrinks the panel top margin (28→16) when off | ➕ |
| `enableDrag` / `onDragStart` / `onDragEnd` | the Qt port has no pointer drag-to-dismiss gesture (dismissal is scrim/Escape); no flag is exposed rather than ship a no-op | ⛔ no drag gesture in the Qt port |
| `dragHandleColor` / `dragHandleSize` | `on-surface-variant`@40%, 32×4 (M3) | ⛔ token-owned |
| `backgroundColor` / `elevation` / `shadowColor` | `surface-container-low`, level-1 | ⛔ theme-role owned |
| `shape` | corner-extra-large top corners | ⛔ token-owned |
| `constraints` / `scrollControlDisabledMaxHeightRatio` | `max_height_ratio` kwarg (default 0.6) caps panel height as a fraction of the host | ➕ |
| `clipBehavior` | panel paints its own clipped surface | ⛔ N/A |
| `animationController` / `transitionAnimationController` | internal `QVariantAnimation` + motion tokens | ⛔ token-owned |
| `isScrollControlled` / `useSafeArea` | Flutter-route-specific layout | ⛔ not idiomatic in Qt |
| `barrierColor` | scrim role @ 32% | ⛔ token-owned |

- [x] all properties verified or added

## MdStandardBottomSheet (persistent, non-modal) — covered ✅
| Capability | Qt (QObject) equivalent | Status |
|---|---|---|
| dock inline, peek↔full | `MdStandardBottomSheet`, `_PEEK` height | ✅ |
| expand/collapse | `expand()` / `collapse()` / `set_expanded(animated=)`; `expanded` @property | ✅ |
| state change | `toggled(bool)` Signal | ✅ |
| content | `add_content(widget)` | ✅ |

- [x] all properties verified or added

## SideSheet (M3 spec) → MdSideSheet (modal) — covered ✅
| M3 capability | Qt (QObject) equivalent | Status |
|---|---|---|
| anchor right / left | `MdSideSheet(side="right"|"left")`, leading corners rounded | ✅ |
| header (title + close) | `title=` label + `close` `MdIconButton` → `dismiss()` | ✅ |
| content | `add_content(widget)` | ✅ |
| trailing actions | `add_action(text)` → `MdTextButton` (reveals a divider) | ✅ |
| slide in/out + scrim | `open()` / `dismiss()`, horizontal slide | ✅ |
| close fired | `closed` Signal | ✅ |
| dismiss on scrim/Escape/close | `mousePressEvent`/`keyPressEvent`/close button | ✅ |
| background/elevation/shape | `surface-container-low`, level-1, extra-large leading corners | ⛔ token-owned |
| fixed width | `_WIDTH` = 320 (M3) | ⛔ token-owned |

- [x] all properties verified or added

## MdStandardSideSheet (persistent, non-modal) — covered ✅
| Capability | Qt (QObject) equivalent | Status |
|---|---|---|
| dock inline, width toggle | `MdStandardSideSheet`, animates 0↔320 | ✅ |
| header / content / actions | `title=`, `add_content`, `add_action` | ✅ |
| expand/collapse | `expand()` / `collapse()` / `set_expanded()`; `expanded` @property | ✅ |
| state change | `toggled(bool)` Signal | ✅ |

- [x] all properties verified or added

## SnackBar / SnackBarAction (snack_bar.dart) → MdSnackbar (widgets/snackbar) — covered ✅
| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `content` | `MdSnackbar(text=...)` → `body-medium` label | ✅ |
| `action` (`SnackBarAction`) | `action_label=` → clickable label | ✅ |
| `SnackBarAction.label` | `action_label` text | ✅ |
| `SnackBarAction.onPressed` | `action` Signal (fires then auto-dismisses) | ✅ |
| `duration` | `duration=` kwarg (default 4000ms, per `_snackBarDisplayDuration`) | ✅ |
| (auto/early dismiss) | `dismissed` Signal | ✅ |
| `behavior` (`SnackBarBehavior.fixed`/`floating`) | `behavior="floating"|"fixed"` kwarg + `behavior` @property; fixed = flush full-width at the edge, floating = inset + margin | ➕ |
| `showCloseIcon` | `show_close_icon=` kwarg → trailing `close` `MdIcon`; dismisses without emitting `action` | ➕ |
| `closeIconColor` | `inverse-on-surface` role | ⛔ theme-role owned |
| `backgroundColor` / `elevation` | `inverse-surface`, level-3 | ⛔ theme-role owned |
| `shape` | corner-extra-small (4px) token | ⛔ token-owned |
| `margin` / `padding` / `width` | M3 margins/widths in `_reposition` (344–600, 16px) | ⛔ token/layout-owned |
| `actionOverflowThreshold` | single action only (M3 limit) | ⛔ not idiomatic in Qt |
| `animation` | internal `QVariantAnimation` slide (short4 token) | ⛔ token-owned |
| `onVisible` | could map to a Signal; not requested this pass | ⛔ out of scope |
| `dismissDirection` / `hitTestBehavior` / `clipBehavior` | gesture/clip knobs not modelled | ⛔ N/A |

- [x] all properties verified or added

## DraggableScrollableSheet (draggable_scrollable_sheet.dart, widgets/) → MdDraggableScrollableSheet (widgets/draggablesheet) — built 🆕
Non-modal bottom-anchored sheet, sized as a fraction of the parent height,
draggable between min/max with snap, hosting a scroll area (Material scrollbars).
Owns its state: `size_fraction` + `sizeChanged(float)` emitted on every change.
Resize math is pure (`clamp_size`, `nearest_snap`); the wheel-vs-scroll decision
is pure (`couple_wheel`, full truth table tested).
| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `initialChildSize` / `minChildSize` / `maxChildSize` | `initial_size=` / `min_size=` / `max_size=` (clamped) | 🆕 |
| `snap` / `snapSizes` | `snap=` / `snap_sizes=` (min/max always included) | 🆕 |
| `builder` (gives a ScrollController) | `add_content(widget)` into an internal `QScrollArea` | 🆕 |
| `DraggableScrollableController.size` | `size_fraction` @property (renamed to avoid `QWidget.size`) | 🆕 |
| `controller.animateTo` / `.jumpTo` / `.reset` | `animate_to()` / `set_size(animated=)` / `reset()` | 🆕 |
| (notifications) | `sizeChanged(float)` Signal | 🆕 |
| drag/scroll coupling | handle-drag resizes (snaps on release); **wheel** couples to the inner scroll (`couple_wheel`) | 🆕 |
| mouse/touch finger-drag coupling over content | ⛔ deferred — only the handle drags and the wheel couples (event-capture over arbitrary content is fragile) |
| snap after a wheel resize | ⛔ deferred — only handle-release snaps; wheel resize lands free |
| `expand` / `shouldCloseOnMinExtent` / `snapAnimationDuration` | ⛔ token durations; non-modal sheet does not auto-close |

- Note: the down-wheel=grow mapping is faithful to Flutter's finger-up=grow; deliberate, documented in the module.
- [x] all properties verified or added; built with tests + gallery page

---

## Coordinator follow-up
- None required. No shared file (`core/modal_overlay.py`, `core/__init__.py`,
  `gallery/gallery.py`, `widgets/__init__.py`) was edited. The new dialog/sheet/
  snackbar kwargs are exercised in unit tests; `gallery.py` (forbidden here) is
  unchanged — if the gallery should demo the new `barrier_dismissible`,
  `show_drag_handle`/`is_dismissible`, `behavior`/`show_close_icon`, or
  `add_option` options, that wiring is a gallery-side follow-up.
