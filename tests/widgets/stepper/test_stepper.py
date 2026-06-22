"""Tests for MdStepper."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel

from material_qt.widgets.stepper import MdStep, MdStepper, StepState, StepperType


def _steps() -> list[MdStep]:
    return [
        MdStep("Account", QLabel("a"), subtitle="Set up", state=StepState.COMPLETE),
        MdStep("Profile", QLabel("b")),
        MdStep("Confirm", QLabel("c")),
    ]


def test_empty_stepper_constructs(qtbot):
    s = MdStepper()
    qtbot.addWidget(s)
    assert s.currentStep == 0
    assert s.steps == []


def test_current_step_defaults_and_clamps(qtbot):
    s = MdStepper(_steps(), current_step=99)
    qtbot.addWidget(s)
    assert s.currentStep == 2  # clamped to last step


def test_set_current_step_changes_visible_content(qtbot):
    s = MdStepper(_steps(), current_step=0)
    qtbot.addWidget(s)
    s.show()
    assert s._content_holders[0].isVisibleTo(s)
    assert not s._content_holders[1].isVisibleTo(s)
    s.set_current_step(1)
    assert s.currentStep == 1
    assert s._content_holders[1].isVisibleTo(s)
    assert not s._content_holders[0].isVisibleTo(s)


def test_set_current_step_marks_active(qtbot):
    s = MdStepper(_steps(), current_step=0)
    qtbot.addWidget(s)
    assert s.steps[0].active and not s.steps[1].active
    s.set_current_step(1)
    assert s.steps[1].active and not s.steps[0].active


def test_step_tapped_signal(qtbot):
    s = MdStepper(_steps())
    qtbot.addWidget(s)
    seen = []
    s.stepTapped.connect(seen.append)
    s._headers[2].clicked.emit()
    assert seen == [2]


def test_disabled_step_does_not_emit_tap(qtbot):
    steps = _steps()
    steps[1].state = StepState.DISABLED
    s = MdStepper(steps)
    qtbot.addWidget(s)
    seen = []
    s.stepTapped.connect(seen.append)
    # Disabled header swallows the press (no clicked signal).
    s._headers[1].mousePressEvent(None)
    assert seen == []


def test_continue_and_cancel_signals(qtbot):
    s = MdStepper(_steps())
    qtbot.addWidget(s)
    cont, canc = [], []
    s.continued.connect(lambda: cont.append(1))
    s.canceled.connect(lambda: canc.append(1))
    # Find the buttons inside the current content holder.
    from material_qt.widgets.button.button import MdTextButton

    buttons = s._content_holders[0].findChildren(MdTextButton)
    labels = {b.text(): b for b in buttons}
    labels["Continue"].click()
    labels["Cancel"].click()
    assert cont == [1] and canc == [1]


def test_set_step_state_updates(qtbot):
    s = MdStepper(_steps())
    qtbot.addWidget(s)
    s.set_step_state(1, StepState.ERROR)
    assert s.steps[1].state is StepState.ERROR


def test_renders_vertical(qtbot):
    s = MdStepper(_steps(), type=StepperType.VERTICAL)
    qtbot.addWidget(s)
    s.resize(420, 360)
    s.grab()


def test_renders_horizontal(qtbot):
    s = MdStepper(_steps(), type=StepperType.HORIZONTAL)
    qtbot.addWidget(s)
    s.resize(520, 220)
    s.grab()
