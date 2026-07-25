"""Tests for MdButtonGroup."""

from __future__ import annotations

from material_qt.widgets.buttongroup import MdButtonGroup


def test_multi_select_independent(qtbot):
    g = MdButtonGroup(multi=True)
    qtbot.addWidget(g)
    a = g.add_button("Bold", icon="format_bold")
    b = g.add_button("Italic", icon="format_italic")
    a.setChecked(True)
    b.setChecked(True)
    assert g.selected_indices() == [0, 1]


def test_single_select_exclusive(qtbot):
    g = MdButtonGroup(multi=False)
    qtbot.addWidget(g)
    a = g.add_button("Day")
    b = g.add_button("Week")
    a.setChecked(True)
    b.setChecked(True)
    assert g.selected_indices() == [1] and not a.isChecked()


def test_changed_signal(qtbot):
    g = MdButtonGroup(multi=True)
    qtbot.addWidget(g)
    a = g.add_button("One")
    seen = []
    g.changed.connect(seen.append)
    a.setChecked(True)
    assert seen[-1] == [0]


def test_single_select_switch_emits_changed_once(qtbot):
    """Regression: an exclusive switch fires two toggled signals (old off, new
    on); ``changed`` must still be emitted exactly once."""
    g = MdButtonGroup(multi=False)
    qtbot.addWidget(g)
    a = g.add_button("Day")
    b = g.add_button("Week")
    a.setChecked(True)
    seen = []
    g.changed.connect(seen.append)
    b.click()
    assert seen == [[1]]


def test_renders(qtbot):
    g = MdButtonGroup()
    qtbot.addWidget(g)
    for label, icon in [("Bold", "format_bold"), ("Italic", "format_italic")]:
        g.add_button(label, icon=icon)
    g.resize(g.sizeHint())
    g.grab()
