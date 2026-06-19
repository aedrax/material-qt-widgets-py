"""Tests for MdSearchBar."""

from __future__ import annotations

from material_qt.widgets.searchbar import MdSearchBar


def test_text_changed_signal(qtbot):
    s = MdSearchBar()
    qtbot.addWidget(s)
    seen = []
    s.textChanged.connect(seen.append)
    s.set_text("hello")
    assert s.text() == "hello"
    assert seen[-1] == "hello"


def test_submitted_on_return(qtbot):
    s = MdSearchBar()
    qtbot.addWidget(s)
    got = []
    s.submitted.connect(got.append)
    s.set_text("query")
    s._edit.returnPressed.emit()
    assert got == ["query"]


def test_renders(qtbot):
    s = MdSearchBar(placeholder="Search recipes", trailing_icon="mic")
    qtbot.addWidget(s)
    s.resize(360, 56)
    s.grab()
