"""Tests for MdNavigationDrawer."""

from __future__ import annotations

from material_qt.widgets.navigationdrawer import MdNavigationDrawer


def test_first_destination_selected(qtbot):
    d = MdNavigationDrawer(headline="Mail")
    qtbot.addWidget(d)
    a = d.add_destination("Inbox", icon="inbox")
    d.add_destination("Sent", icon="send")
    assert a.isChecked()


def test_exclusive_and_signal(qtbot):
    d = MdNavigationDrawer()
    qtbot.addWidget(d)
    a = d.add_destination("Inbox", icon="inbox")
    b = d.add_destination("Sent", icon="send")
    seen = []
    d.changed.connect(seen.append)
    b.setChecked(True)
    assert b.isChecked() and not a.isChecked()
    assert seen[-1] == 1


def test_renders(qtbot):
    d = MdNavigationDrawer(headline="Mail")
    qtbot.addWidget(d)
    for label, icon in [("Inbox", "inbox"), ("Starred", "star"), ("Sent", "send")]:
        d.add_destination(label, icon=icon)
    d.resize(d.sizeHint())
    d.grab()


def test_index_ignores_non_destination_children(qtbot):
    d = MdNavigationDrawer()
    qtbot.addWidget(d)
    a = d.add_destination("Inbox", icon="inbox")
    d.add_section("Labels")        # not a destination
    d.add_divider()                # not a destination
    b = d.add_destination("Work", icon="work")
    seen = []
    d.changed.connect(seen.append)
    b.setChecked(True)
    # b is the 2nd *destination* -> index 1, despite the section/divider between.
    assert seen[-1] == 1
    assert not a.isChecked()


def test_active_icon(qtbot):
    d = MdNavigationDrawer()
    qtbot.addWidget(d)
    item = d.add_destination("Inbox", icon="inbox", active_icon="mark_email_unread")
    assert item._active_icon == "mark_email_unread"
    assert item._icon == "inbox"


def test_renders_with_sections_and_dividers(qtbot):
    d = MdNavigationDrawer(headline="Mail")
    qtbot.addWidget(d)
    d.add_destination("Inbox", icon="inbox")
    d.add_destination("Starred", icon="star")
    d.add_divider()
    d.add_section("Labels")
    d.add_destination("Work", icon="work")
    d.add_destination("Personal", icon="person")
    d.resize(d.sizeHint())
    d.grab()
