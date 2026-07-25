"""Tests for MdCheckbox."""

from __future__ import annotations

from material_qt.tokens.color import ColorRole
from material_qt.widgets.checkbox import MdCheckbox


def test_toggle_and_signal(qtbot):
    cb = MdCheckbox()
    qtbot.addWidget(cb)
    states = []
    cb.toggled.connect(states.append)
    cb.toggle()
    assert cb.isChecked() is True
    assert states == [True]


def test_checked_clears_indeterminate(qtbot):
    cb = MdCheckbox()
    qtbot.addWidget(cb)
    cb.set_indeterminate(True)
    assert cb.indeterminate is True
    cb.setChecked(True)
    assert cb.indeterminate is False


def test_size_is_state_layer(qtbot):
    cb = MdCheckbox()
    qtbot.addWidget(cb)
    assert cb.sizeHint().width() == 40
    assert cb.sizeHint().height() == 40


def test_error_and_disabled_render(qtbot):
    for kw in ({}, {"checked": True}, {"checked": True, "error": True}):
        cb = MdCheckbox(**kw)
        qtbot.addWidget(cb)
        cb.resize(cb.sizeHint())
        cb.grab()
    cb = MdCheckbox(checked=True)
    qtbot.addWidget(cb)
    cb.setEnabled(False)
    cb.resize(cb.sizeHint())
    cb.grab()


def test_ripple_and_focus(qtbot):
    cb = MdCheckbox()
    qtbot.addWidget(cb)
    assert cb.ripple is not None
    assert cb.focus_ring is not None


def test_indeterminate_constructor(qtbot):
    cb = MdCheckbox(indeterminate=True)
    qtbot.addWidget(cb)
    assert cb.indeterminate is True
    assert cb.isChecked() is False
    cb.resize(cb.sizeHint())
    cb.grab()


def test_label_sets_accessible_name(qtbot):
    cb = MdCheckbox(label="Accept terms")
    qtbot.addWidget(cb)
    assert cb.label == "Accept terms"
    cb.set_label("Other")
    assert cb.accessibleName() == "Other"


def test_error_ripple_role_at_construction(qtbot):
    """Regression: the ctor computed the ripple role ignoring ``error``."""
    cb = MdCheckbox(error=True)
    qtbot.addWidget(cb)
    assert cb.ripple.overlay.color_role == ColorRole.ERROR


def test_set_error_resyncs_ripple_role(qtbot):
    """Regression: set_error never resynced the ripple color role."""
    cb = MdCheckbox()
    qtbot.addWidget(cb)
    assert cb.ripple.overlay.color_role == ColorRole.ON_SURFACE
    cb.set_error(True)
    assert cb.ripple.overlay.color_role == ColorRole.ERROR
    cb.set_error(False)
    assert cb.ripple.overlay.color_role == ColorRole.ON_SURFACE


def test_uncheck_clears_indeterminate(qtbot):
    """Regression: unchecking a checked+indeterminate checkbox left the dash
    (indeterminate was only cleared when transitioning TO checked)."""
    cb = MdCheckbox(checked=True)
    qtbot.addWidget(cb)
    cb.set_indeterminate(True)
    assert cb.isChecked() and cb.indeterminate
    cb.click()
    assert cb.isChecked() is False
    assert cb.indeterminate is False


def test_repeated_toggle_with_animation_settle(qtbot):
    """Regression: a finished animation must not leave a stale C++ object that
    crashes the next toggle (persistent-animation fix)."""
    from PySide6.QtTest import QTest

    cb = MdCheckbox()
    qtbot.addWidget(cb)
    cb.show()
    for _ in range(4):
        cb.toggle()
        QTest.qWait(200)  # let the 150ms animation fully finish between toggles
    assert cb.isChecked() is False
