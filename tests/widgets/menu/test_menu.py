"""Tests for MdMenu / MdMenuItem."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QFocusEvent, QMoveEvent
from PySide6.QtWidgets import QApplication, QLineEdit, QVBoxLayout, QWidget

from material_qt.widgets.menu import MdMenu, MdMenuItem, MdSubmenuItem
from material_qt.widgets.menu.menu import _SHADOW_MARGIN


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


def test_submenu_item_selection_emits_from_child_and_host(qtbot):
    host = MdMenu()
    qtbot.addWidget(host)
    sub = MdSubmenuItem("More")
    host.add_item(sub)
    leaf = MdMenuItem("Nested")
    sub.add_item(leaf)
    child_picked, host_picked = [], []
    sub.submenu.selected.connect(child_picked.append)
    host.selected.connect(host_picked.append)
    leaf.triggered.emit()
    assert child_picked == ["Nested"]
    assert host_picked == ["Nested"]
    sub.submenu.close()


def test_submenu_selection_closes_whole_chain(qtbot):
    host = MdMenu()
    qtbot.addWidget(host)
    sub = MdSubmenuItem("More")
    host.add_item(sub)
    leaf = MdMenuItem("Nested", value=7)
    sub.add_item(leaf)
    anchor = MdMenuItem("anchor")
    qtbot.addWidget(anchor)
    anchor.show()
    host.open_at(anchor)
    sub.open_submenu()
    assert not host.isHidden() and not sub.submenu.isHidden()
    picked, values = [], []
    host.selected.connect(picked.append)
    host.activated.connect(values.append)
    leaf.triggered.emit()
    assert picked == ["Nested"]
    assert values == [7]
    assert host.isHidden()
    assert sub.submenu.isHidden()


def test_highlight_navigation_skips_disabled(qtbot):
    m = MdMenu(grabs_focus=False)
    qtbot.addWidget(m)
    m.add_item(MdMenuItem("A"))
    m.add_item(MdMenuItem("B", enabled=False))
    m.add_item(MdMenuItem("C"))
    m.highlight_next()  # A
    assert m._highlight == 0
    m.highlight_next()  # skips disabled B -> C
    assert m._highlight == 2
    assert not m._items[1]._highlighted
    m.highlight_prev()  # skips disabled B -> A
    assert m._highlight == 0


def test_highlight_first_skips_disabled(qtbot):
    m = MdMenu(grabs_focus=False)
    qtbot.addWidget(m)
    m.add_item(MdMenuItem("A", enabled=False))
    m.add_item(MdMenuItem("B"))
    m.highlight_first()
    assert m._highlight == 1


def test_highlight_all_disabled_is_noop(qtbot):
    m = MdMenu(grabs_focus=False)
    qtbot.addWidget(m)
    m.add_item(MdMenuItem("A", enabled=False))
    m.add_item(MdMenuItem("B", enabled=False))
    m.highlight_next()
    assert m._highlight == -1


def test_activate_refuses_disabled_item(qtbot):
    m = MdMenu(grabs_focus=False)
    qtbot.addWidget(m)
    m.add_item(MdMenuItem("A", enabled=False))
    picked = []
    m.selected.connect(picked.append)
    m._set_highlight(0)  # force the highlight onto the disabled row
    assert m.activate_highlighted() is False
    assert picked == []


def test_keyboard_highlight_scrolls_into_view(qtbot, qapp):
    m = MdMenu(max_height=100, grabs_focus=False)
    qtbot.addWidget(m)
    for i in range(20):
        m.add_item(MdMenuItem(f"Item {i}"))
    anchor = MdMenuItem("anchor")
    qtbot.addWidget(anchor)
    anchor.show()
    m.open_at(anchor)
    qapp.processEvents()
    try:
        for _ in range(10):
            m.highlight_next()
        assert m._scroll.verticalScrollBar().value() > 0
    finally:
        m.close()


def test_open_at_caps_height_to_screen_near_bottom(qtbot, qapp):
    avail = qapp.primaryScreen().availableGeometry()
    m = MdMenu()  # uncapped
    qtbot.addWidget(m)
    for i in range(40):
        m.add_item(MdMenuItem(f"Item {i}"))
    anchor = MdMenuItem("anchor")
    qtbot.addWidget(anchor)
    anchor.move(100, avail.bottom() - 60)
    anchor.show()
    m.open_at(anchor)
    try:
        assert m.frameGeometry().bottom() <= avail.bottom()
        assert m.frameGeometry().top() >= avail.top()
    finally:
        m.close()


def test_open_at_flips_above_when_no_room_below(qtbot, qapp):
    avail = qapp.primaryScreen().availableGeometry()
    m = MdMenu()
    qtbot.addWidget(m)
    for i in range(3):
        m.add_item(MdMenuItem(f"Item {i}"))
    anchor = MdMenuItem("anchor")
    qtbot.addWidget(anchor)
    anchor.move(100, avail.bottom() - 60)
    anchor.show()
    m.open_at(anchor)
    try:
        anchor_top = anchor.mapToGlobal(anchor.rect().topLeft()).y()
        assert m.frameGeometry().bottom() <= avail.bottom()
        # Flipped above: the visible panel's bottom sits above the anchor.
        assert m.y() + m.height() - _SHADOW_MARGIN <= anchor_top
    finally:
        m.close()


def _non_grabbing_popup(qtbot):
    """A shown host window with two fields and a popup anchored to the first."""
    host = QWidget()
    qtbot.addWidget(host)
    lay = QVBoxLayout(host)
    field = QLineEdit()
    other = QLineEdit()
    lay.addWidget(field)
    lay.addWidget(other)
    host.show()
    m = MdMenu(field, grabs_focus=False)
    m.add_item(MdMenuItem("A"))
    m.open_at(field)
    assert not m.isHidden()
    return host, field, other, m


def test_non_grabbing_popup_closes_when_focus_leaves_anchor(qtbot):
    host, field, other, m = _non_grabbing_popup(qtbot)
    other.setFocus(Qt.FocusReason.TabFocusReason)
    QApplication.sendEvent(
        other, QFocusEvent(QEvent.Type.FocusIn, Qt.FocusReason.TabFocusReason)
    )
    assert m.isHidden()


def test_non_grabbing_popup_survives_focus_on_anchor(qtbot):
    host, field, other, m = _non_grabbing_popup(qtbot)
    QApplication.sendEvent(
        field, QFocusEvent(QEvent.Type.FocusIn, Qt.FocusReason.MouseFocusReason)
    )
    assert not m.isHidden()
    m.close()


def test_non_grabbing_popup_closes_on_host_window_move(qtbot):
    host, field, other, m = _non_grabbing_popup(qtbot)
    QApplication.sendEvent(host, QMoveEvent(QPoint(60, 60), QPoint(0, 0)))
    assert m.isHidden()


def test_non_grabbing_popup_closes_on_window_deactivate(qtbot):
    host, field, other, m = _non_grabbing_popup(qtbot)
    QApplication.sendEvent(host, QEvent(QEvent.Type.WindowDeactivate))
    assert m.isHidden()
