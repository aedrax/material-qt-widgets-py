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
