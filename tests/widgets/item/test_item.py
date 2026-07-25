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


def test_swap_deletes_replaced_widget(qtbot):
    # Regression: replaced slot widgets were setParent(None) but never
    # deleted, leaking them as invisible top-levels.
    from shiboken6 import isValid

    it = MdItem("Title")
    qtbot.addWidget(it)
    old_lead, old_trail = QLabel("L1"), QLabel("T1")
    it.set_leading(old_lead)
    it.set_trailing(old_trail)
    it.set_leading(QLabel("L2"))
    it.set_trailing(None)
    qtbot.wait(20)  # process the deferred deletes
    assert not isValid(old_lead)
    assert not isValid(old_trail)


def test_swap_same_widget_is_not_deleted(qtbot):
    from shiboken6 import isValid

    it = MdItem("Title")
    qtbot.addWidget(it)
    lead = QLabel("L")
    it.set_leading(lead)
    it.set_leading(lead)  # re-setting the same widget must not delete it
    qtbot.wait(20)
    assert isValid(lead)
    assert it._leading is lead


def test_renders(qtbot):
    it = MdItem("Title", supporting_text="Sub", trailing_supporting_text="1")
    qtbot.addWidget(it)
    it.resize(it.sizeHint())
    it.grab()
