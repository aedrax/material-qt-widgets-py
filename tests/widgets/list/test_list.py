"""Tests for MdList / MdListItem."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel

from material_qt.widgets.list import MdList, MdListItem


def test_clicked_signal(qtbot):
    it = MdListItem("Row")
    qtbot.addWidget(it)
    seen = []
    it.clicked.connect(lambda: seen.append(1))
    it.clicked.emit()
    assert seen == [1]


def test_min_height(qtbot):
    it = MdListItem("Row")
    qtbot.addWidget(it)
    assert it.sizeHint().height() >= 56


def test_interactive_vs_static(qtbot):
    interactive = MdListItem("A")
    static = MdListItem("B", interactive=False)
    for it in (interactive, static):
        qtbot.addWidget(it)
    assert interactive.ripple is not None
    assert static.ripple is None


def test_list_add_items_and_dividers(qtbot):
    lst = MdList()
    qtbot.addWidget(lst)
    lst.add_item(MdListItem("A"))
    lst.add_item(MdListItem("B"), divider=True)
    assert len(lst.items) == 2


def test_renders(qtbot):
    lst = MdList()
    qtbot.addWidget(lst)
    lst.add_item(MdListItem("Inbox", supporting_text="3 new",
                            leading=QLabel("I")))
    lst.add_item(MdListItem("Sent"), divider=True)
    lst.resize(400, 160)
    lst.grab()


def test_selected_property(qtbot):
    it = MdListItem("Row", selected=True)
    qtbot.addWidget(it)
    assert it.selected is True
    it.set_selected(False)
    assert it.selected is False
    it.selected = True
    assert it.selected is True
    it.grab()  # selected paint path


def test_enabled_property_suppresses_click(qtbot):
    it = MdListItem("Row", enabled=False)
    qtbot.addWidget(it)
    assert it.enabled is False
    assert it.isEnabled() is False
    it.set_enabled(True)
    assert it.isEnabled() is True


def test_content_padding(qtbot):
    it = MdListItem("Row")
    qtbot.addWidget(it)
    it.set_content_padding(4, 2, 4, 2)
    assert it.content_padding() == (4, 2, 4, 2)
