"""Tests for MdNavigationBar."""

from __future__ import annotations

from material_qt.widgets.navigationbar import MdNavigationBar


def test_first_destination_selected(qtbot):
    bar = MdNavigationBar()
    qtbot.addWidget(bar)
    a = bar.add_destination("Home", icon="home")
    bar.add_destination("Search", icon="search")
    assert a.isChecked()


def test_exclusive_and_signal(qtbot):
    bar = MdNavigationBar()
    qtbot.addWidget(bar)
    a = bar.add_destination("Home", icon="home")
    b = bar.add_destination("Search", icon="search")
    seen = []
    bar.changed.connect(seen.append)
    b.setChecked(True)
    assert b.isChecked() and not a.isChecked()
    assert seen[-1] == 1


def test_renders(qtbot):
    bar = MdNavigationBar()
    qtbot.addWidget(bar)
    for label, icon in [("Home", "home"), ("Search", "search"), ("Saved", "bookmark")]:
        bar.add_destination(label, icon=icon)
    bar.resize(bar.sizeHint())
    bar.grab()
