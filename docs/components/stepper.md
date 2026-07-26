# Stepper

Guide a user through ordered steps.

**Classes:** `MdStepper`, `MdStep`, `StepState`, `StepperType` · **Source:** `src/material_qt/widgets/stepper/`
**Spec:** <https://api.flutter.dev/flutter/material/Stepper-class.html> (Flutter-parity widget; not in the M3 component catalogue). Ports Flutter's `Stepper`: an ordered list of steps, each with a numbered (or icon) circle reflecting its state, a title, an optional subtitle, and a content widget revealed for the current step. Flutter's callbacks become Qt signals.

## Usage

```python
from material_qt import MdStepper, MdStep

steps = [
    MdStep("Account", account_form),
    MdStep("Address", address_form, subtitle="Shipping only"),
    MdStep("Confirm", summary_widget),
]
stepper = MdStepper(steps, parent=page)

stepper.stepTapped.connect(stepper.set_current_step)
stepper.continued.connect(lambda: stepper.set_current_step(stepper.currentStep + 1))
stepper.canceled.connect(lambda: stepper.set_current_step(stepper.currentStep - 1))
```

## API

### MdStepper

Extends `QWidget`.

```python
MdStepper(
    steps: list[MdStep] | None = None,
    parent: QWidget | None = None,
    *,
    type: StepperType = StepperType.VERTICAL,
    current_step: int = 0,
    show_controls: bool = True,
)
```

- `steps` — property; the list of `MdStep` objects.
- `type` — property; the `StepperType` (named `type` to match Flutter).
- `currentStep` — property; the current step index (camelCase to match the Flutter property name).
- `set_current_step(index)` — change the current step; the index is clamped into range, the active flags are re-synced, and the matching content is shown.
- `set_step_state(index, state)` — change one step's `StepState` and refresh its header.

**Signals:**

- `stepTapped = Signal(int)` — a step header was clicked (Flutter `onStepTapped`); payload is the step index. Disabled steps do not emit.
- `continued = Signal()` — the Continue button was clicked (Flutter `onStepContinue`).
- `canceled = Signal()` — the Cancel button was clicked (Flutter `onStepCancel`).

The stepper does not advance itself on `continued`/`canceled`/`stepTapped` — connect them to `set_current_step` as in the usage snippet.

### MdStep

A single step; mirrors Flutter's `Step`. A plain class holding mutable attributes (`title`, `subtitle`, `content`, `state`, `active`):

```python
MdStep(
    title: str,
    content: QWidget | None = None,
    *,
    subtitle: str = "",
    state: StepState = StepState.INDEXED,
    active: bool = False,
)
```

When `content` is `None` an empty `QWidget` is substituted. `active` mirrors Flutter's `isActive` and is managed by the stepper (the current step is marked active).

### StepState

The state of a step's circle (cf. Flutter `StepState`):

- `INDEXED` — show the step number.
- `EDITING` — show a pencil icon.
- `COMPLETE` — show a tick icon.
- `DISABLED` — show the step number, not tappable.
- `ERROR` — show an error glyph.

### StepperType

The stepper's main axis (cf. Flutter `StepperType`): `VERTICAL`, `HORIZONTAL`.

## Notes

- Layout: a `VERTICAL` stepper stacks step headers with the active step's content in-between; a `HORIZONTAL` stepper lays the circles in a row separated by thin connector lines, with the active content below the row.
- Circle fill: a step's circle fills with `PRIMARY` when it is active *or* complete (M3 fills completed steps with primary too); `ERROR` fills with the error color and draws `!`; inactive/disabled circles use `on-surface` at 38% opacity. The `EDITING`/`COMPLETE` glyphs are `MdIcon`s (`edit`/`check` ligature names).
- `show_controls=False` omits the Continue / Cancel button bar under each step's content; the `continued`/`canceled` signals then never fire.
- The requested `current_step` is clamped into range at construction; `set_current_step` clamps too and is a no-op on an empty stepper.
- Step headers ripple on press and show a pointing-hand cursor unless the step is `DISABLED`.
- Steps are laid out once at construction — build the full `steps` list up front; `set_step_state` is the supported post-construction mutation.
- Icon glyphs require the Material Symbols font; see [icon](./icon.md) for font resolution and [theming](../theming.md) for color roles.
