# Expansion, stepper & carousel — Flutter ↔ material_qt parity

Status legend: ✅ verified · ➕ added this pass · 🆕 built this pass · ⛔ N/A (rationale)

Scope: `widgets/expansionpanel`, `widgets/stepper` (new), `widgets/carousel`.
Flutter refs (read-only): `expansion_tile.dart`, `expansion_panel.dart`,
`stepper.dart`, `carousel.dart`.

## ExpansionTile (expansion_tile.dart) → MdExpansionPanel (widgets/expansionpanel) — covered ✅

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `title` | `title` ctor arg / `set_title()` | ✅ |
| `subtitle` | `subtitle=` kwarg / `set_subtitle()` | ➕ |
| `leading` | `leading=` kwarg (QWidget) | ➕ |
| `trailing` | `trailing=` kwarg (QWidget) | ➕ |
| `showTrailingIcon` | `show_trailing_icon=` kwarg (hides chevron) | ➕ |
| `children` | `add_content(QWidget)` | ✅ |
| `onExpansionChanged` | `toggled(bool)` Signal | ✅ |
| `initiallyExpanded` | `initially_expanded=` kwarg (`expanded=` alias kept) | ✅ |
| `backgroundColor` / `collapsedBackgroundColor` | `background_role=` (ColorRole) / `set_background_role()` | ➕ (single theme role; no separate collapsed role) |
| (expanded state read) | `expanded` property | ✅ |
| (programmatic toggle) | `toggle()` / `set_expanded(bool, animated=)` | ✅ |
| `controlAffinity` | ⛔ chevron is always trailing; leading/trailing are explicit slots |
| `expandedCrossAxisAlignment`, `expandedAlignment`, `childrenPadding`, `tilePadding` | ⛔ content uses a fixed 16px padded column |
| `textColor` / `collapsedTextColor` / `iconColor` / `collapsedIconColor` | ⛔ colors come from theme roles (on-surface / on-surface-variant) |
| `shape` / `collapsedShape` / `clipBehavior` | ⛔ square header surface (M3 list item); not parameterized |
| `controller`, `statesController` | ⛔ controlled via `set_expanded()` + `toggled` Signal |
| `maintainState`, `dense`, `visualDensity`, `minTileHeight`, `enableFeedback`, `enabled`, `expansionAnimationStyle`, `splashColor`, `internalAddSemanticForOnTap` | ⛔ not modeled |

## ExpansionPanelList (expansion_panel.dart) → MdExpansionPanel — covered ✅

Flutter's `ExpansionPanelList` is a *managed list* of `ExpansionPanel`s with optional
single-open (radio) grouping. The Qt port keeps panels **independent** (a host lays
several `MdExpansionPanel`s in a column); exclusive-accordion grouping is deferred (also
noted in the module docstring).

| Flutter property (ExpansionPanel / …List) | Qt equivalent | Status |
|---|---|---|
| `ExpansionPanel.headerBuilder` | `title` + `leading`/`trailing` slots | ✅ |
| `ExpansionPanel.body` | `add_content()` | ✅ |
| `ExpansionPanel.isExpanded` | `expanded` / `set_expanded()` | ✅ |
| `ExpansionPanel.backgroundColor` | `background_role=` | ➕ |
| `ExpansionPanel.canTapOnHeader` | ⛔ whole header is always tappable |
| `ExpansionPanel.splashColor` / `highlightColor` | ⛔ theme ripple |
| `…List.expansionCallback` | per-panel `toggled(bool)` Signal | ✅ |
| `…List.children` | host composes N `MdExpansionPanel`s | ✅ (composition) |
| `ExpansionPanelRadio` / `_allowOnlyOnePanelOpen` / `initialOpenPanelValue` | ⛔ exclusive-accordion grouping deferred (panels independent) |
| `…List.animationDuration` | ⛔ fixed MEDIUM2 token |
| `…List.elevation` | ⛔ flat list surface (M3 default is flat) |
| `…List.dividerColor` | ⛔ no inter-panel divider drawn (host's concern) |
| `…List.expandedHeaderPadding`, `materialGapSize`, `expandIconColor` | ⛔ not modeled |

## CarouselView (carousel.dart) → MdCarousel / MdWeightedCarousel (widgets/carousel) — covered ✅

| Flutter property | Qt equivalent | Status |
|---|---|---|
| `children` | `add_item(QWidget)` / `add_tile(label)` | ✅ |
| `itemExtent` | `item_extent=` kwarg (tile width + snap stride) | ➕ |
| `onIndexChanged` | `indexChanged(int)` Signal | ✅ |
| `itemSnapping` | `item_snapping=` kwarg / `set_item_snapping()` (default `True`; Flutter default `False`) | ➕ |
| `scrollDirection` | `scroll_direction=` kwarg — horizontal only | ➕ (⛔ vertical: QScrollArea strip + `weighted_geometry` are horizontal-only; a vertical mode would be a rewrite) |
| `padding` | `padding=` kwarg (margin around the strip) | ➕ |
| `onTap` | `MdWeightedCarousel.itemTapped(int)`; `MdCarousel` tiles ripple on click | ✅ |
| `flexWeights` (`CarouselView.weighted`) | `MdWeightedCarousel(weights=[…])` | ✅ |
| `consumeMaxWeight` | `MdWeightedCarousel(consume_max_weight=)` | ✅ |
| `shrinkExtent` | ⛔ weighted tiles collapse via `weighted_geometry`; not a separate knob |
| `reverse` | ⛔ not modeled |
| `infinite` | ⛔ not modeled |
| `controller` | ⛔ controlled via drag/wheel + `indexChanged`; `current_index` property |
| `backgroundColor` / `elevation` / `shape` / `overlayColor` / `itemClipBehavior` | ⛔ tiles use theme container roles + EXTRA_LARGE shape |
| `enableSplash` | ⛔ default tiles ripple; flex tiles do not (transparent to mouse) |
| `itemBuilder` / `itemCount` (`.weighted` lazy ctor) | ⛔ eager `add_item`/`add_tile`; no lazy builder |

## Stepper (stepper.dart) → MdStepper (widgets/stepper) — built 🆕

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `steps` (`List<Step>`) | `steps` ctor arg (`list[MdStep]`) / `steps` property | 🆕 |
| `Step.title` | `MdStep(title=…)` | 🆕 |
| `Step.subtitle` | `MdStep(subtitle=…)` | 🆕 |
| `Step.content` | `MdStep(content=QWidget)` | 🆕 |
| `Step.state` (`StepState`) | `MdStep(state=StepState.…)` / `set_step_state()` | 🆕 |
| `Step.isActive` | `MdStep(active=…)` (synced to `currentStep`) | 🆕 |
| `StepState.{indexed,editing,complete,disabled,error}` | `StepState.{INDEXED,EDITING,COMPLETE,DISABLED,ERROR}` | 🆕 |
| `StepperType.{vertical,horizontal}` | `StepperType.{VERTICAL,HORIZONTAL}`, `type=` kwarg | 🆕 |
| `currentStep` | `currentStep` property / `set_current_step(int)` | 🆕 |
| `onStepTapped` | `stepTapped(int)` Signal (disabled steps don't emit) | 🆕 |
| `onStepContinue` | `continued` Signal (Continue button) | 🆕 |
| `onStepCancel` | `canceled` Signal (Cancel button) | 🆕 |
| `controlsBuilder` | default Continue/Cancel bar; `show_controls=` to disable | 🆕 (no custom builder) |
| `elevation`, `margin` | ⛔ flat; outer margins are the host's concern |
| `connectorColor` / `connectorThickness` | ⛔ connector uses `outline-variant` role, 1px |
| `stepIconBuilder` / `stepIconHeight` / `stepIconWidth` / `stepIconMargin` | ⛔ fixed 24px themed circle |
| `physics`, `controller`, `clipBehavior` | ⛔ not a scroll view; host scrolls if needed |
| `headerPadding`, `contentPadding` | ⛔ fixed paddings |

### Step circle states (M3)
- INDEXED / DISABLED → step number; PRIMARY fill when active, else `on-surface @ 38%`.
- EDITING → pencil icon; COMPLETE → check icon (PRIMARY fill when active).
- ERROR → ERROR fill + "!" glyph.

- [x] all properties verified or added

## Coordinator follow-up (shared files — NOT edited here)
- Export `MdStepper`, `MdStep`, `StepState`, `StepperType` from `widgets/__init__.py`
  (and `core` re-exports if applicable). `widgets/stepper/__init__.py` already exports them.
- Register `MdStepper` in the gallery `_COMPONENTS` / `COMPONENT_META`
  (`material_qt/gallery/gallery.py`) with a demo page (vertical + horizontal steppers,
  Continue/Cancel wired, a COMPLETE and an ERROR step).
- Optionally surface the new `MdExpansionPanel` (subtitle/leading/trailing/background_role)
  and `MdCarousel` (item_extent/item_snapping/padding) knobs in their gallery demos.
