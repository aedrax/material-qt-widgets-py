# Text input — Flutter ↔ material_qt parity

Status legend: ✅ verified · ➕ added this pass · 🆕 built this pass · ⛔ N/A (rationale)

Scope: Flutter `TextField` (`text_field.dart`), `TextFormField` (`text_form_field.dart`),
and `InputDecoration` (`input_decorator.dart`) mapped onto material_qt's
`MdFilledTextField` / `MdOutlinedTextField` (`widgets/textfield`) and the shared
`MdField` chrome (`widgets/field`). Callbacks become Qt Signals; setters follow
`set_*()` / `@property` / constructor-kwarg conventions; colors come from theme
roles; input formatting uses `QValidator` instead of `inputFormatters`.

Both Filled and Outlined variants already existed and were verified, plus the
shared field chrome. No genuinely-missing whole component — this pass filled
properties only.

## TextField (text_field.dart) → MdFilledTextField / MdOutlinedTextField (widgets/textfield)

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| controller / onChanged | `text()` / `set_text()` + `textChanged(str)` Signal | ✅ |
| onSubmitted / onEditingComplete | `submitted(str)` Signal (QLineEdit.returnPressed) | ➕ |
| decoration.labelText | `label` kwarg → `MdField` floating label | ✅ |
| decoration.hintText | `placeholder` kwarg → `set_placeholder()` | ✅ |
| decoration.helperText | `supporting_text` kwarg → `set_supporting_text()` | ➕ (setter added; kwarg existed) |
| decoration.errorText / error | `error` kwarg + `set_error(bool)` (ERROR role) | ✅ |
| decoration.prefixIcon | `leading_icon` kwarg → `set_leading_icon(name)` (MdIcon slot) | ➕ |
| decoration.suffixIcon | `trailing_icon` kwarg → `set_trailing_icon(name)` (MdIcon slot) | ➕ |
| decoration.prefixText / suffixText | — | ⛔ N/A this pass — inline text inside the content area (a QLabel beside the input) is semantically distinct from the icon slots; the single chrome slot is reserved for icons. Deferred — see Coordinator follow-up. |
| decoration.counterText / buildCounter | `max_length` → live `MdField` counter (bottom-right) | ➕ |
| obscureText / obscuringCharacter | `password` kwarg → QLineEdit Password echo + visibility toggle | ➕ (toggle added; password existed) |
| maxLines | `max_lines` kwarg → multiline (QPlainTextEdit) when > 1 | ➕ |
| minLines | `min_lines` kwarg → multiline initial box height | ➕ |
| maxLength | `max_length` kwarg → QLineEdit.setMaxLength (single-line) / enforced truncation (multiline) + counter | ➕ |
| enabled | `enabled` kwarg + `set_enabled(bool)` | ➕ |
| readOnly | `read_only` kwarg + `set_read_only(bool)` / `is_read_only()` | ➕ |
| keyboardType / inputFormatters | `validator` kwarg + `set_validator(QValidator)` | ➕ |
| (escape hatch) | `line_edit` property (underlying QLineEdit/QPlainTextEdit), `field` property | ✅ |

### Filled / Outlined variants
| Flutter | Qt | Status |
|---|---|---|
| `TextField` + filled decoration | `MdFilledTextField` (FILLED chrome) | ✅ |
| `TextField` + `OutlineInputBorder` | `MdOutlinedTextField` (OUTLINED notched chrome) | ✅ |

## InputDecoration (input_decorator.dart) → MdField (widgets/field)

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| label / labelText | `label` (floating, animated) | ✅ |
| helper / helperText | `supporting_text` + `set_supporting_text()` | ➕ |
| hint / hintText | `placeholder` (on the content QLineEdit) | ✅ |
| error / errorText | `error` + `set_error()` (ERROR-role indicator/label/support) | ✅ |
| prefixIcon | `set_leading(widget)` slot | ➕ |
| suffixIcon | `set_trailing(widget)` slot | ➕ |
| counter / counterText | `set_counter(text)` (bottom-right of support row) | ➕ |
| filled / border | `FieldVariant.FILLED` / `FieldVariant.OUTLINED` | ✅ |
| enabled | inherited `setEnabled()` (label dims to ON_SURFACE) | ✅ |
| (multiline sizing) | `multiline_box_height` kwarg (taller box) | ➕ |

## TextFormField (text_form_field.dart) → QValidator

| Flutter property | Qt (QObject) equivalent | Status |
|---|---|---|
| validator (FormFieldValidator) | `set_validator(QValidator)` / `validator` kwarg | ➕ |
| autovalidateMode / onSaved / initialValue | — | ⛔ N/A — Flutter's Form/FormField machinery has no QtWidgets analog; Qt uses QValidator + per-field error state. Validation UX (set_error + supporting_text) is the idiomatic equivalent. |

## Intentionally not ported (⛔ N/A — cosmetic / platform-specific long tail)

These TextField/InputDecoration properties have no idiomatic place in the Qt
port or are handled by Qt itself; left as escape-hatch territory via `line_edit`.

| Flutter property | Rationale |
|---|---|
| focusNode / autofocus / canRequestFocus | Use `line_edit.setFocus()` / Qt focus policy directly. |
| textCapitalization / autocorrect / enableSuggestions / smartDashesType / smartQuotesType / enableIMEPersonalizedLearning / enableInlinePrediction | Mobile soft-keyboard hints; no desktop QtWidgets analog. |
| textInputAction / keyboardAppearance / keyboardType (soft kbd) | Mobile keyboard config; N/A on desktop. |
| cursorWidth / cursorHeight / cursorRadius / cursorColor / cursorErrorColor / cursorOpacityAnimates / showCursor | Qt manages the caret; tweak via stylesheet on `line_edit` if needed. |
| selectionControls / selectionHeightStyle / selectionWidthStyle / enableInteractiveSelection / selectAllOnFocus | Qt handles selection natively. |
| magnifierConfiguration / stylusHandwritingEnabled / scribbleEnabled | Touch/stylus features; no QtWidgets analog. |
| contextMenuBuilder / toolbarOptions / onAppPrivateCommand / contentInsertionConfiguration | Qt provides a native context menu; customize on `line_edit`. |
| scrollController / scrollPhysics / scrollPadding | Qt scroll behavior is built into QPlainTextEdit. |
| autofillHints / restorationId / groupId / undoController / statesController | Framework plumbing without a QtWidgets equivalent. |
| style / strutStyle / textAlign / textAlignVertical / textDirection | Typography is theme-driven (BODY_LARGE); set on `line_edit` for overrides. |
| expands / isDense / isCollapsed / contentPadding / constraints / visualDensity | Density variants not in this pass; fixed M3 metrics used. |
| onTap / onTapOutside / onTapUpOutside / onTapAlwaysCalled / ignorePointers / mouseCursor / dragStartBehavior / clipBehavior | Low-level pointer plumbing; use Qt events on `line_edit`. |
| floatingLabelBehavior / floatingLabelAlignment / alignLabelWithHint | Label floats on focus/populate by default (M3 standard behavior). |
| *Style / *MaxLines (labelStyle, hintStyle, helperMaxLines, errorMaxLines, …) | Per-element style overrides; theme roles cover the defaults. |
| *Border (enabledBorder/focusedBorder/errorBorder/disabledBorder/focusedErrorBorder) | Borders derive from variant + state (focus/error) automatically. |
| fillColor / focusColor / hoverColor / iconColor / prefix/suffixIconColor | Theme-role driven (surface-container-highest, primary, on-surface-variant). |
| semanticCounterText / hintLocales / hintTextDirection / hintFadeDuration / maintainHintSize / maintainLabelSize | a11y / i18n / animation niceties without a QtWidgets analog in this pass. |
| maxLengthEnforcement | QLineEdit hard-enforces maxLength (equivalent to `enforced`). |

## Checklist
- [x] All TextField / InputDecoration / TextFormField properties verified, added, or marked N/A
- [x] Filled + Outlined variants verified
- [x] Field chrome (label / indicator / outline / supporting / error / icon slots / counter) verified
- [x] Added this pass: submitted signal, multiline (max_lines/min_lines), prefix/suffix icons,
      character counter (max_length, enforced), password visibility toggle (real click),
      QValidator, enabled, read_only, set_supporting_text
- [x] Tests: tests/widgets/textfield + tests/widgets/field (30 pass); full suite 336 pass
- [ ] Coordinator follow-up #1: gallery.py is off-limits to this unit. If the text-field
      gallery demo should showcase the new props (multiline, icons, counter, password
      toggle, validator), wire them into `gallery/gallery.py` and the textfield/field
      `demo.py` exemplars in a coordinator pass.
- [ ] Coordinator follow-up #2: prefixText / suffixText (inline text labels inside the
      content area). Implementing well needs a second content slot beside the input
      (QLabel left/right of the QLineEdit), separate from the icon slots. Deferred to a
      focused pass rather than overloading the single icon slot.
