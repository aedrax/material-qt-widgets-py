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


def test_label_behavior_propagates(qtbot):
    bar = MdNavigationBar(label_behavior="selected")
    qtbot.addWidget(bar)
    a = bar.add_destination("Home", icon="home")
    b = bar.add_destination("Search", icon="search")
    assert a._shows_label() and not b._shows_label()  # a selected by default
    bar.set_label_behavior("hide")
    assert not a._shows_label() and not b._shows_label()
    bar.set_label_behavior("always")
    assert a._shows_label() and b._shows_label()


def test_badge(qtbot):
    bar = MdNavigationBar()
    qtbot.addWidget(bar)
    dot = bar.add_destination("Home", icon="home", badge="")
    count = bar.add_destination("Mail", icon="mail", badge="8")
    plain = bar.add_destination("Search", icon="search")
    assert dot._badge == "" and count._badge == "8" and plain._badge is None


def test_selected_index_round_trip(qtbot):
    bar = MdNavigationBar()
    qtbot.addWidget(bar)
    bar.add_destination("Home", icon="home")
    bar.add_destination("Search", icon="search")
    bar.add_destination("Saved", icon="bookmark")
    assert bar.selected_index == 0  # first selected by default
    bar.selected_index = 2
    assert bar.selected_index == 2
    bar.set_selected_index(1)
    assert bar.selected_index == 1
    bar.set_selected_index(99)  # out of range -> no-op
    assert bar.selected_index == 1


def test_renders_no_labels_and_badges(qtbot):
    bar = MdNavigationBar(label_behavior="hide")
    qtbot.addWidget(bar)
    bar.add_destination("Home", icon="home", badge="")
    bar.add_destination("Mail", icon="mail", badge="99+")
    bar.add_destination("Search", icon="search")
    bar.resize(bar.sizeHint())
    bar.grab()
