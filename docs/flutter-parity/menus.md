# Menus, select & autocomplete — Flutter ↔ material_qt parity

Status legend: ✅ verified · ➕ added this pass · 🆕 built this pass · ⛔ N/A (rationale)

Scope: Flutter `dropdown_menu.dart` (DropdownMenu), `dropdown.dart`
(DropdownButton), `menu_anchor.dart` (MenuAnchor / MenuItemButton /
SubmenuButton), `popup_menu.dart` (PopupMenuButton), `autocomplete.dart`
(Autocomplete) → material_qt `widgets/select`, `widgets/menu`,
`widgets/autocomplete`. Callbacks are exposed as Qt Signals; values configured
via constructor kwargs and `set_*()` / `@property`.

## DropdownMenu (dropdown_menu.dart) → MdSelect (widgets/select) — covered ✅

`MdFilledSelect` / `MdOutlinedSelect` (base `_MdSelect`).

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `dropdownMenuEntries` | `items=` kwarg / `set_options(list)` / `add_option(text, value)` | ➕ (`items`/`set_options` added; `add_option` existed) |
| `initialSelection` | `value=` kwarg / `set_value(value)` | ➕ (`value` kwarg added; `set_value` existed) |
| `onSelected` | `changed(value)` Signal | ✅ |
| `label` / `labelWidget` | `label=` kwarg → MdField floating label | ✅ |
| `hintText` | `hint_text=` kwarg → display placeholder | ➕ |
| `helperText` | `supporting_text=` kwarg → MdField supporting text | ✅ |
| `enabled` | `enabled=` kwarg / `set_enabled()` / `is_enabled()` (gates open) | ➕ |
| `leadingIcon` | `leading_icon=` kwarg → MdIcon at field's left edge | ➕ |
| `trailingIcon` / `selectedTrailingIcon` / `showTrailingIcon` | built-in `arrow_drop_down` MdIcon | ✅ (fixed Material chevron) |
| `menuHeight` | `menu_height=` kwarg / `set_menu_height()` → MdMenu height cap + scroll | ➕ |
| `enableFilter` | `enable_filter=` kwarg → editable field + non-grabbing options popup (keyboard stays on the field; arrows/Enter/Esc forwarded), type-to-filter live menu | ➕ |
| `width` / `expandedInsets` | widget `setFixedWidth` / layout (Qt-native sizing) | ⛔ Qt layout handles sizing |
| `enableSearch` / `searchCallback` / `filterCallback` | `enable_filter` covers type-to-filter; custom predicate not exposed | ⛔ default substring filter |
| `controller` / `menuController` | not needed; widget owns its display + popup | ⛔ no external controller model |
| `requestFocusOnTap` / `focusNode` / `trailingIconFocusNode` | Qt focus model | ⛔ Qt focus handling |
| `errorText` | MdField error styling (`set_error` exists on field) | ⛔ error surfaced via field, not wired to a string |
| `style` / `textStyle` / `menuStyle` / `decorationBuilder` / `inputDecorationTheme` | theme-role colors + typescale via MaterialWidgetMixin / MdField | ⛔ theme tokens, not per-instance style objects |
| `textAlign` / `maxLines` / `keyboardType` / `textInputAction` / `cursorHeight` / `inputFormatters` / `scrollPadding` | QLineEdit native config (via field content) | ⛔ Qt input config |
| `alignmentOffset` / `closeBehavior` / `selectOnly` / `restorationId` | popup placement / framework plumbing | ⛔ not applicable |

### DropdownButton (dropdown.dart) — same MdSelect maps these

| Flutter property | Qt equivalent | Status |
|---|---|---|
| `items` | `items=` / `set_options()` | ➕ |
| `value` | `value=` / `set_value()` | ➕ |
| `onChanged` | `changed(value)` Signal | ✅ |
| `hint` / `disabledHint` | `hint_text=` (placeholder) | ➕ |
| `icon` / `iconSize` / `iconEnabledColor` / `iconDisabledColor` | built-in `arrow_drop_down` MdIcon (theme color) | ✅ |
| `menuMaxHeight` | `menu_height=` (MdMenu cap + scroll) | ➕ |
| `menuWidth` | `setFixedWidth(field.width())` on the popup | ✅ |
| `isExpanded` / `isDense` / `itemHeight` / `alignment` / `padding` | MdField + MdMenu fixed Material metrics | ⛔ Material spec metrics |
| `elevation` / `dropdownColor` / `focusColor` / `style` / `borderRadius` | theme tokens (MdMenu = surface-container, level-2, extra-small) | ⛔ theme tokens |
| `selectedItemBuilder` / `onTap` / `underline` / `autofocus` / `focusNode` / `enableFeedback` / `barrierDismissible` / `mouseCursor` / `dropdownMenuItemMouseCursor` | builders / Qt focus & cursor / popup behavior | ⛔ not applicable |

## MenuAnchor / MenuItemButton / PopupMenuButton (menu_anchor.dart, popup_menu.dart) → MdMenu / MdMenuItem (widgets/menu) — covered ✅

`MdMenu` is a `Qt.Popup` surface (surface-container, level-2 elevation,
corner-extra-small) of `MdMenuItem` rows, anchored to a trigger via `open_at`.

### MenuAnchor → MdMenu

| Flutter property | Qt equivalent | Status |
|---|---|---|
| `menuChildren` | `add_item(MdMenuItem)` / `clear()` | ✅ (`clear` ➕) |
| `builder` / `child` / `childFocusNode` | `open_at(anchor)` anchors to any trigger widget | ✅ |
| `onOpen` / `onClose` | Qt `show()`/`close()` of the popup window | ⛔ Qt window events |
| `alignmentOffset` | `open_at(anchor, side="bottom"|"right")` placement | ✅ (side placement) |
| (height overflow) | `max_height=` kwarg / `set_max_height()` → `setMaximumHeight` + QScrollArea (shrinks on re-filter) | ➕ |
| (keyboard, non-grabbing) | `grabs_focus=False` → Tool window + `highlight_next/prev` / `activate_highlighted` driven by the owning field | ➕ |
| `consumeOutsideTap` / `anchorTapClosesMenu` | `Qt.Popup` dismisses on outside click natively | ✅ |
| `style` / `clipBehavior` / `reservedPadding` / `layerLink` / `crossAxisUnconstrained` / `useRootOverlay` / `animated` / `onAnimationStatusChanged` | theme tokens / Qt popup window plumbing | ⛔ not applicable |

### MenuItemButton → MdMenuItem

| Flutter property | Qt equivalent | Status |
|---|---|---|
| `child` (label) | `text` ctor arg / `text` property | ✅ |
| `onPressed` | `triggered` Signal (+ menu `selected(text)` / `activated(value)`) | ✅ (`activated` ➕) |
| `leadingIcon` | `leading_icon=` (Material Symbols glyph) | ✅ |
| `trailingIcon` | `trailing_icon=` (Material Symbols glyph) | ➕ |
| `shortcut` | `trailing_text=` (shortcut text, right-aligned) | ✅ |
| (item value) | `value=` ctor arg / `value` property → menu `activated(value)` | ➕ |
| (enabled) | `enabled=` ctor arg / `set_enabled()` / `is_enabled()` (dims + ignores click) | ➕ |
| `onHover` / `requestFocusOnHover` / `onFocusChange` | `enterEvent`/`leaveEvent` repaint + Qt focus | ⛔ Qt event model |
| `closeOnActivate` | menu closes on select (default) | ✅ |
| `semanticsLabel` | `setAccessibleName` available via QWidget | ⛔ Qt a11y |
| `style` / `statesController` / `clipBehavior` / `overflowAxis` / `autofocus` / `focusNode` | theme tokens / Qt plumbing | ⛔ not applicable |

### SubmenuButton → MdSubmenuItem 🆕

A menu item that opens a nested `MdMenu` anchored to its right edge, on hover or
click.

| Flutter property | Qt equivalent | Status |
|---|---|---|
| `menuChildren` | `add_item()` / `submenu` property (the nested MdMenu) | 🆕 |
| `child` (label) | `text` ctor arg | 🆕 |
| `leadingIcon` | `leading_icon=` | 🆕 |
| `submenuIcon` | `submenu_icon=` (default `arrow_right`, drawn as trailing glyph) | 🆕 |
| open on hover / click | `enterEvent` + `triggered` → `open_submenu()` (anchors `side="right"`) | 🆕 |
| `onOpen` / `onClose` / `hoverOpenDelay` / `animated` / `controller` / `style` / `menuStyle` / `alignmentOffset` / `useRootOverlay` / `clipBehavior` / `statesController` / `focusNode` / `onAnimationStatusChanged` | Qt popup window + theme tokens | ⛔ not applicable |

### PopupMenuButton → MdMenu (anchored popup)

| Flutter property | Qt equivalent | Status |
|---|---|---|
| `itemBuilder` | `add_item(MdMenuItem)` | ✅ |
| `onSelected` | `selected(text)` / `activated(value)` Signals | ✅ |
| `initialValue` | preselect via `MdMenuItem` focus (no persisted selection model) | ⛔ menu is stateless |
| `onOpened` / `onCanceled` | Qt popup show/close | ⛔ Qt window events |
| `offset` / `position` / `constraints` | `open_at(anchor, side=...)` + `setFixedWidth`/`set_max_height` | ✅ (partial: side + size cap) |
| `enabled` | per-item `enabled`; trigger widget controls open | ✅ (item-level) |
| `icon` / `child` / `iconSize` / `iconColor` / `tooltip` / `splashRadius` | the trigger widget is the caller's (e.g. MdIconButton) | ⛔ caller-provided trigger |
| `elevation` / `shadowColor` / `surfaceTintColor` / `color` / `shape` / `borderRadius` / `menuPadding` / `padding` | theme tokens (surface-container, level-2, extra-small) | ⛔ theme tokens |
| `enableFeedback` / `useRootNavigator` / `routeSettings` / `popUpAnimationStyle` / `clipBehavior` / `requestFocus` / `style` | Qt popup plumbing | ⛔ not applicable |

## Autocomplete (autocomplete.dart) → MdAutocomplete (widgets/autocomplete) — built 🆕

`MdAutocomplete` (alias of `MdFilledAutocomplete`; `MdOutlinedAutocomplete`
variant). MdField chrome + QLineEdit, reusing the MdMenu surface for the
filtered options popup.

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| `optionsBuilder` | `options=` kwarg / `set_options()` + `matching_options(query)` (substring filter); shown in a single reused **non-grabbing** MdMenu so the keyboard stays on the field (QCompleter pattern; arrows/Enter/Esc forwarded) | 🆕 |
| `onSelected` | `selected(value)` Signal (emits the option object) | 🆕 |
| `displayStringForOption` | `display_string_for_option=` callable / `set_display_string_for_option()` | 🆕 |
| `optionsMaxHeight` | `options_max_height=` kwarg → MdMenu height cap + scroll | 🆕 |
| `initialValue` | `initial_value=` kwarg → field text | 🆕 |
| (text changes) | `text_changed(str)` Signal; `text()` / `set_text()` | 🆕 |
| `label` / `placeholder` / `supporting_text` | ctor kwargs → MdField chrome | 🆕 |
| `textEditingController` | widget owns its QLineEdit (`line_edit` property exposes it) | ⛔ no external controller |
| `fieldViewBuilder` / `optionsViewBuilder` | fixed MdField + MdMenu rendering | ⛔ no builder injection |
| `optionsViewOpenDirection` | opens below the field (`open_at` default) | ⛔ down only |
| `focusNode` | Qt focus model | ⛔ Qt focus handling |

### Verified empirically (real X display)

- Editable filter / autocomplete: the options popup does **not** grab the
  keyboard; typing continues to filter, arrows/Enter/Esc navigate, and a real
  mouse click on a row selects it. The top match is auto-highlighted so Enter
  commits it. Focus-out close is deferred one event-loop turn so a click on the
  popup lands before it closes.
- Submenu opens a nested popup while the host menu stays visible; selection from
  the nested menu emits correctly. Note: nested-popup selection was exercised
  via `triggered` + open/visibility checks; real-mouse click on a nested-Popup
  leaf is a known-untested edge (same class as the autocomplete path, which is
  verified).

- [x] all properties verified or added
- [ ] Coordinator follow-up: register `MdAutocomplete` (and optionally
      `MdFilledSelect`/`MdOutlinedSelect`, `MdMenu`) in the gallery
      `_COMPONENTS` / `COMPONENT_META`; export `MdAutocomplete` /
      `MdSubmenuItem` from `widgets/__init__.py` / `widgets/core` as appropriate.
      (Not done here per the shared-file rule — only the new autocomplete dir,
      the select/menu widget dirs, and this checklist were edited.)
