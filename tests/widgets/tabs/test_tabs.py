"""Tests for MdTabs / MdTab."""

from __future__ import annotations

from material_qt.widgets.tabs import MdTabs


def test_first_tab_selected_by_default(qtbot):
    t = MdTabs()
    qtbot.addWidget(t)
    a = t.add_tab("A")
    t.add_tab("B")
    assert a.isChecked()


def test_exclusive_selection_and_signal(qtbot):
    t = MdTabs()
    qtbot.addWidget(t)
    a = t.add_tab("A")
    b = t.add_tab("B")
    seen = []
    t.changed.connect(seen.append)
    b.setChecked(True)
    assert b.isChecked() and not a.isChecked()
    assert seen[-1] == 1


def test_indicator_moves(qtbot):
    t = MdTabs()
    qtbot.addWidget(t)
    a = t.add_tab("Alpha")
    b = t.add_tab("Bravo")
    t.resize(300, 48)
    t.show()
    a.setChecked(True)
    x_a = t._ind
    b.setChecked(True)
    # After selecting b, the indicator target center is to the right of a's.
    cx_b, _ = t._indicator_target(b)
    cx_a, _ = t._indicator_target(a)
    assert cx_b > cx_a


def test_renders_primary_and_secondary(qtbot):
    for secondary in (False, True):
        t = MdTabs(secondary=secondary)
        qtbot.addWidget(t)
        t.add_tab("One", icon="" if secondary else "flight")
        t.add_tab("Two")
        t.resize(300, 48)
        t.grab()
