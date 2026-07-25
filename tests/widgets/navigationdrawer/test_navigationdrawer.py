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


def test_selected_index_round_trip(qtbot):
    d = MdNavigationDrawer()
    qtbot.addWidget(d)
    d.add_destination("Inbox", icon="inbox")
    d.add_destination("Sent", icon="send")
    d.add_destination("Spam", icon="report")
    assert d.selected_index == 0
    d.selected_index = 2
    assert d.selected_index == 2
    d.set_selected_index(1)
    assert d.selected_index == 1
    d.set_selected_index(99)
    assert d.selected_index == 1


def test_footer_is_last_and_destinations_stay_grouped(qtbot):
    from PySide6.QtWidgets import QLabel
    d = MdNavigationDrawer()
    qtbot.addWidget(d)
    d.add_destination("Inbox", icon="inbox")
    footer = QLabel("v1.0")
    d.set_footer(footer)
    # footer is pinned to the very bottom (after the trailing stretch).
    assert d._lay.itemAt(d._lay.count() - 1).widget() is footer
    # a destination added AFTER the footer still lands above the stretch.
    later = d.add_destination("Sent", icon="send")
    footer_idx = d._lay.indexOf(footer)
    later_idx = d._lay.indexOf(later)
    assert later_idx < footer_idx


def test_set_width(qtbot):
    d = MdNavigationDrawer()
    qtbot.addWidget(d)
    d.set_width(280)
    assert d.width() == 280


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


def test_theme_toggle_after_delete_does_not_raise(qtbot):
    """Regression: section restyles were plain closures on the singleton
    ThemeManager, so a theme change after the drawer died raised RuntimeError."""
    from material_qt.theme.theme_manager import ThemeManager

    d = MdNavigationDrawer(headline="Mail")
    qtbot.addWidget(d)
    d.add_destination("Inbox", icon="inbox")
    d.add_section("Labels")
    d.deleteLater()
    qtbot.wait(20)  # process the deferred delete
    ThemeManager.instance().toggle_light_dark()  # must not raise
    ThemeManager.instance().toggle_light_dark()


def test_section_restyles_on_theme_change(qtbot):
    from material_qt.theme.theme_manager import ThemeManager

    d = MdNavigationDrawer()
    qtbot.addWidget(d)
    label = d.add_section("Labels")
    before = label.styleSheet()
    ThemeManager.instance().toggle_light_dark()
    assert label.styleSheet() != before


def test_set_footer_deletes_replaced_widget(qtbot):
    from PySide6.QtWidgets import QLabel
    from shiboken6 import isValid

    d = MdNavigationDrawer()
    qtbot.addWidget(d)
    old = QLabel("v1")
    d.set_footer(old)
    new = QLabel("v2")
    d.set_footer(new)
    qtbot.wait(20)  # process the deferred delete
    assert not isValid(old)
    assert d._footer is new
