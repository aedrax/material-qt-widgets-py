"""Tests for MdMenu / MdMenuItem."""

from __future__ import annotations

from material_qt.widgets.menu import MdMenu, MdMenuItem, MdSubmenuItem


def test_add_items(qtbot):
    m = MdMenu()
    qtbot.addWidget(m)
    for t in ("Cut", "Copy", "Paste"):
        m.add_item(MdMenuItem(t))
    assert len(m._items) == 3


def test_trigger_emits_selected_and_closes(qtbot):
    m = MdMenu()
    qtbot.addWidget(m)
    item = MdMenuItem("Copy")
    m.add_item(item)
    picked = []
    m.selected.connect(picked.append)
    item.triggered.emit()
    assert picked == ["Copy"]


def test_item_width_includes_icon(qtbot):
    plain = MdMenuItem("Copy")
    withicon = MdMenuItem("Copy", leading_icon="content_copy")
    for it in (plain, withicon):
        qtbot.addWidget(it)
    assert withicon.sizeHint().width() > plain.sizeHint().width()


def test_panel_renders(qtbot):
    m = MdMenu()
    qtbot.addWidget(m)
    for t in ("Cut", "Copy", "Paste"):
        m.add_item(MdMenuItem(t, leading_icon="content_copy"))
    m._panel.resize(m._panel.sizeHint())
    m._panel.grab()


def test_item_value_defaults_to_text(qtbot):
    item = MdMenuItem("Copy")
    qtbot.addWidget(item)
    assert item.value == "Copy"


def test_item_custom_value_and_activated(qtbot):
    m = MdMenu()
    qtbot.addWidget(m)
    item = MdMenuItem("Copy", value=42)
    m.add_item(item)
    vals = []
    m.activated.connect(vals.append)
    item.triggered.emit()
    assert vals == [42]


def test_disabled_item_flag(qtbot):
    item = MdMenuItem("Copy", enabled=False)
    qtbot.addWidget(item)
    assert item.is_enabled() is False
    item.set_enabled(True)
    assert item.is_enabled() is True


def test_trailing_icon_widens_item(qtbot):
    plain = MdMenuItem("Copy")
    withicon = MdMenuItem("Copy", trailing_icon="check")
    for it in (plain, withicon):
        qtbot.addWidget(it)
    assert withicon.sizeHint().width() > plain.sizeHint().width()


def test_max_height_caps_popup(qtbot, qapp):
    m = MdMenu(max_height=100)
    qtbot.addWidget(m)
    for i in range(20):
        m.add_item(MdMenuItem(f"Item {i}"))
    anchor = MdMenuItem("anchor")  # any widget works as an anchor
    qtbot.addWidget(anchor)
    anchor.show()
    m.open_at(anchor)
    try:
        assert m.height() <= 100 + 2 * 14 + 1
    finally:
        m.close()


def test_submenu_opens_nested_menu(qtbot):
    host = MdMenu()
    qtbot.addWidget(host)
    sub = MdSubmenuItem("More")
    host.add_item(sub)
    sub.add_item(MdMenuItem("Nested"))
    assert len(sub.submenu._items) == 1
    # Triggering a submenu item opens its child, not selecting the host menu.
    picked = []
    host.selected.connect(picked.append)
    sub.triggered.emit()
    assert picked == []
    sub.submenu.close()


def test_highlight_navigation_wraps(qtbot):
    m = MdMenu(grabs_focus=False)
    qtbot.addWidget(m)
    for t in ("A", "B", "C"):
        m.add_item(MdMenuItem(t))
    m.highlight_next()  # 0
    assert m._highlight == 0 and m._items[0]._highlighted
    m.highlight_prev()  # wraps to 2
    assert m._highlight == 2 and m._items[2]._highlighted
    assert not m._items[0]._highlighted


def test_activate_highlighted_triggers_item(qtbot):
    m = MdMenu(grabs_focus=False)
    qtbot.addWidget(m)
    m.add_item(MdMenuItem("A"))
    m.add_item(MdMenuItem("B"))
    picked = []
    m.selected.connect(picked.append)
    assert m.activate_highlighted() is False  # nothing highlighted yet
    m.highlight_next()
    assert m.activate_highlighted() is True
    assert picked == ["A"]


def test_non_grabbing_menu_does_not_grab(qtbot):
    m = MdMenu(grabs_focus=False)
    qtbot.addWidget(m)
    assert m._grabs_focus is False


def test_max_height_uses_maximum_not_fixed(qtbot):
    # setMaximumHeight (not setFixedHeight) so a re-filter can shrink it.
    m = MdMenu(max_height=100)
    qtbot.addWidget(m)
    anchor = MdMenuItem("anchor")
    qtbot.addWidget(anchor)
    anchor.show()
    for i in range(20):
        m.add_item(MdMenuItem(f"Item {i}"))
    m.open_at(anchor)
    try:
        tall = m.height()
        m.clear()
        m.add_item(MdMenuItem("only one"))
        m.open_at(anchor)
        assert m.height() <= tall
    finally:
        m.close()


def test_submenu_item_selection_emits_from_child(qtbot):
    sub = MdSubmenuItem("More")
    qtbot.addWidget(sub)
    leaf = MdMenuItem("Nested")
    sub.add_item(leaf)
    picked = []
    sub.submenu.selected.connect(picked.append)
    leaf.triggered.emit()
    assert picked == ["Nested"]
    sub.submenu.close()
