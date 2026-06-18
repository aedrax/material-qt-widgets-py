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
