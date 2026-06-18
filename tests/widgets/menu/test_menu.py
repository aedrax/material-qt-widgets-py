"""Tests for MdMenu / MdMenuItem."""

from __future__ import annotations

from material_qt.widgets.menu import MdMenu, MdMenuItem


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
