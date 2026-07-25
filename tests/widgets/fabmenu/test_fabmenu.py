"""Tests for MdFabMenu."""

from __future__ import annotations

from material_qt.widgets.fabmenu import MdFabMenu


def test_starts_closed_items_hidden(qtbot):
    m = MdFabMenu()
    qtbot.addWidget(m)
    row = m.add_item("Share", icon="share")
    assert not m.is_open
    assert not row.isVisibleTo(m)


def test_toggle_opens_and_emits(qtbot):
    m = MdFabMenu()
    qtbot.addWidget(m)
    row = m.add_item("Share", icon="share")
    seen = []
    m.toggled.connect(seen.append)
    m.toggle()
    assert m.is_open and seen == [True]
    assert row.isVisibleTo(m)


def test_item_click_emits_index_and_closes(qtbot):
    m = MdFabMenu()
    qtbot.addWidget(m)
    m.add_item("Share", icon="share")
    second = m.add_item("Edit", icon="edit")
    m.set_open(True)
    got = []
    m.itemClicked.connect(got.append)
    second.click()  # add_item returns the item's small FAB
    assert got == [1] and not m.is_open


def test_renders_open(qtbot):
    m = MdFabMenu()
    qtbot.addWidget(m)
    m.add_item("Share", icon="share")
    m.add_item("Edit", icon="edit")
    m.set_open(True)
    m.resize(m.sizeHint())
    m.grab()


def test_theme_toggle_after_delete_does_not_raise(qtbot):
    """Regression: item-label restyles were lambdas on the singleton
    ThemeManager, so a theme change after the menu died raised RuntimeError."""
    from material_qt.theme.theme_manager import ThemeManager

    m = MdFabMenu()
    qtbot.addWidget(m)
    m.add_item("Share", icon="share")
    m.deleteLater()
    qtbot.wait(20)  # process the deferred delete
    ThemeManager.instance().toggle_light_dark()  # must not raise
    ThemeManager.instance().toggle_light_dark()


def test_item_label_restyles_on_theme_change(qtbot):
    from material_qt.theme.theme_manager import ThemeManager

    m = MdFabMenu()
    qtbot.addWidget(m)
    m.add_item("Share", icon="share")
    lbl = m._items[0][0]
    before = lbl.styleSheet()
    ThemeManager.instance().toggle_light_dark()
    assert lbl.styleSheet() != before
