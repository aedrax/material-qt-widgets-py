"""Tests for MdRadio."""

from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from material_qt.widgets.radio import MdRadio


def test_checkable_toggle(qtbot):
    r = MdRadio()
    qtbot.addWidget(r)
    r.setChecked(True)
    assert r.isChecked() is True


def test_group_exclusivity(qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    lay = QVBoxLayout(parent)
    a, b, c = MdRadio(checked=True), MdRadio(), MdRadio()
    for r in (a, b, c):
        lay.addWidget(r)
    assert a.isChecked() and not b.isChecked()
    b.setChecked(True)
    # autoExclusive: selecting b deselects a.
    assert b.isChecked() and not a.isChecked()


def test_toggleable_deselects_on_click(qtbot):
    r = MdRadio(checked=True, toggleable=True)
    qtbot.addWidget(r)
    assert r.toggleable is True
    assert r.isChecked() is True
    # Clicking an already-selected toggleable radio deselects it.
    r.click()
    assert r.isChecked() is False
    # Clicking again selects it back.
    r.click()
    assert r.isChecked() is True


def test_toggleable_in_button_group(qtbot):
    from PySide6.QtWidgets import QButtonGroup, QVBoxLayout, QWidget

    parent = QWidget()
    qtbot.addWidget(parent)
    lay = QVBoxLayout(parent)
    group = QButtonGroup(parent)
    a, b = MdRadio(toggleable=True), MdRadio(toggleable=True)
    for r in (a, b):
        lay.addWidget(r)
        group.addButton(r)
    a.click()
    assert a.isChecked() and not b.isChecked()
    # Re-clicking selected A deselects it; the group ends with nothing checked.
    a.click()
    assert not a.isChecked() and not b.isChecked()
    # Selecting B still works after the group's exclusivity was toggled off/on.
    b.click()
    assert b.isChecked() and not a.isChecked()


def test_toggleable_space_deselects(qtbot):
    """Regression: keyboard Space goes through the C++ click path, bypassing
    the Python click() shadow — a toggleable checked radio never deselected."""
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QApplication

    r = MdRadio(checked=True, toggleable=True)
    qtbot.addWidget(r)

    def space(etype):
        QApplication.sendEvent(
            r, QKeyEvent(etype, Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier)
        )

    space(QEvent.Type.KeyPress)
    space(QEvent.Type.KeyRelease)
    assert r.isChecked() is False
    # Space again re-selects.
    space(QEvent.Type.KeyPress)
    space(QEvent.Type.KeyRelease)
    assert r.isChecked() is True
    # Mouse parity retained: click() still deselects.
    r.click()
    assert r.isChecked() is False


def test_non_toggleable_space_stays_selected(qtbot):
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QApplication

    r = MdRadio(checked=True)
    qtbot.addWidget(r)
    for etype in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease):
        QApplication.sendEvent(
            r, QKeyEvent(etype, Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier)
        )
    assert r.isChecked() is True


def test_non_toggleable_stays_selected_on_click(qtbot):
    r = MdRadio(checked=True)
    qtbot.addWidget(r)
    r.click()
    # Default (non-toggleable, autoExclusive): re-clicking does not deselect.
    assert r.isChecked() is True


def test_label_sets_accessible_name(qtbot):
    r = MdRadio(label="Option A")
    qtbot.addWidget(r)
    assert r.label == "Option A"
    r.set_label("Option B")
    assert r.accessibleName() == "Option B"


def test_size_is_state_layer(qtbot):
    r = MdRadio()
    qtbot.addWidget(r)
    assert r.sizeHint().width() == 40 and r.sizeHint().height() == 40


def test_renders(qtbot):
    for kw in ({}, {"checked": True}):
        r = MdRadio(**kw)
        qtbot.addWidget(r)
        r.resize(r.sizeHint())
        r.grab()
    r = MdRadio(checked=True)
    qtbot.addWidget(r)
    r.setEnabled(False)
    r.resize(r.sizeHint())
    r.grab()


def test_ripple_and_focus(qtbot):
    r = MdRadio()
    qtbot.addWidget(r)
    assert r.ripple is not None and r.focus_ring is not None


def test_repeated_toggle_with_animation_settle(qtbot):
    """Regression: a finished animation must not leave a stale C++ object that
    crashes the next toggle (persistent-animation fix)."""
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QVBoxLayout, QWidget

    parent = QWidget()
    qtbot.addWidget(parent)
    lay = QVBoxLayout(parent)
    a, b = MdRadio(checked=True), MdRadio()
    lay.addWidget(a)
    lay.addWidget(b)
    parent.show()
    # Alternate selection; each switch animates the dot in/out on both radios.
    for sel in (b, a, b, a):
        sel.setChecked(True)
        QTest.qWait(200)  # let the 150ms animation fully finish
    assert a.isChecked() and not b.isChecked()


def test_button_group_exclusive_across_parents(qtbot):
    """Radios in different parent widgets (e.g. wrapped in row layouts) are made
    mutually exclusive by a QButtonGroup, even though autoExclusive alone can't
    link them."""
    from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QWidget

    container = QWidget()
    qtbot.addWidget(container)
    group = QButtonGroup(container)
    radios = []
    for i in range(3):
        # Each radio in its OWN wrapper -> different parents.
        row = QWidget(container)
        QHBoxLayout(row)
        r = MdRadio(checked=(i == 0))
        row.layout().addWidget(r)
        group.addButton(r)
        radios.append(r)
    assert [r.isChecked() for r in radios] == [True, False, False]
    radios[2].setChecked(True)
    assert sum(r.isChecked() for r in radios) == 1
    assert radios[2].isChecked()
