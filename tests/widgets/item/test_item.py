"""Tests for MdItem."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel

from material_qt.widgets.item import MdItem


def test_headline_and_supporting(qtbot):
    it = MdItem("Title", supporting_text="Subtitle")
    qtbot.addWidget(it)
    assert it._headline.text() == "Title"
    assert not it._supporting.isHidden()
    it.set_supporting_text("")
    assert it._supporting.isHidden()


def test_trailing_supporting_text(qtbot):
    it = MdItem("Title")
    qtbot.addWidget(it)
    assert it._trailing_supporting.isHidden()
    it.set_trailing_supporting_text("99+")
    assert not it._trailing_supporting.isHidden()
    assert it._trailing_supporting.text() == "99+"


def test_leading_trailing_slots(qtbot):
    lead, trail = QLabel("L"), QLabel("T")
    it = MdItem("Title", leading=lead, trailing=trail)
    qtbot.addWidget(it)
    assert it._leading is lead
    assert it._trailing is trail
    assert it._leading_holder.isVisibleTo(it)
    it.set_leading(None)
    assert it._leading is None


def test_renders(qtbot):
    it = MdItem("Title", supporting_text="Sub", trailing_supporting_text="1")
    qtbot.addWidget(it)
    it.resize(it.sizeHint())
    it.grab()
