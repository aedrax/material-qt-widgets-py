"""Tests for MdNavigationRail."""

from __future__ import annotations

from material_qt.widgets.navigationrail import MdNavigationRail


def test_first_destination_selected(qtbot):
    rail = MdNavigationRail()
    qtbot.addWidget(rail)
    a = rail.add_destination("Home", icon="home")
    rail.add_destination("Search", icon="search")
    assert a.isChecked()


def test_exclusive_and_signal(qtbot):
    rail = MdNavigationRail()
    qtbot.addWidget(rail)
    a = rail.add_destination("Home", icon="home")
    b = rail.add_destination("Search", icon="search")
    seen = []
    rail.changed.connect(seen.append)
    b.setChecked(True)
    assert b.isChecked() and not a.isChecked()
    assert seen[-1] == 1


def test_renders(qtbot):
    rail = MdNavigationRail()
    qtbot.addWidget(rail)
    for label, icon in [("Home", "home"), ("Search", "search"), ("Saved", "bookmark")]:
        rail.add_destination(label, icon=icon)
    rail.resize(rail.sizeHint())
    rail.grab()


def test_extended_width_toggle(qtbot):
    rail = MdNavigationRail()
    qtbot.addWidget(rail)
    rail.add_destination("Home", icon="home")
    assert rail.width() == 80
    rail.set_extended(True, animated=False)
    assert rail.extended and rail.width() == 256
    rail.set_extended(False, animated=False)
    assert not rail.extended and rail.width() == 80


def test_extended_constructor(qtbot):
    rail = MdNavigationRail(extended=True)
    qtbot.addWidget(rail)
    rail.add_destination("Home", icon="home")
    assert rail.width() == 256


def test_label_type_none_shortens_destinations(qtbot):
    rail = MdNavigationRail(label_type="none")
    qtbot.addWidget(rail)
    d = rail.add_destination("Home", icon="home")
    assert d.sizeHint().height() == 48  # no label reserved
    rail.set_label_type("all")
    assert d.sizeHint().height() == 56


def test_label_type_selected_only_active_shows_label(qtbot):
    rail = MdNavigationRail(label_type="selected")
    qtbot.addWidget(rail)
    a = rail.add_destination("Home", icon="home")
    b = rail.add_destination("Search", icon="search")
    assert a._shows_label() and not b._shows_label()  # a is selected by default
    b.setChecked(True)
    assert b._shows_label() and not a._shows_label()


def test_trailing_and_group_alignment(qtbot):
    from PySide6.QtWidgets import QLabel
    rail = MdNavigationRail(group_alignment="center")
    qtbot.addWidget(rail)
    rail.add_destination("Home", icon="home")
    trailing = QLabel("⚙")
    rail.set_trailing(trailing)
    # trailing is the last item in the rail's layout
    last = rail._lay.itemAt(rail._lay.count() - 1)
    assert last.widget() is trailing
