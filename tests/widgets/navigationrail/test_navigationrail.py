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
