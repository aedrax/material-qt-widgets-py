"""Tests for MdSearchView (the full-screen search surface) and MdSearchBar onTap."""

from __future__ import annotations

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication, QWidget

from material_qt.widgets.searchbar import MdSearchBar, MdSearchView


def _host(qtbot) -> QWidget:
    host = QWidget()
    host.resize(600, 800)
    qtbot.addWidget(host)
    return host


def _press(widget: QWidget) -> None:
    pos = widget.rect().center()
    ev = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        pos,
        widget.mapToGlobal(pos),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    QApplication.sendEvent(widget, ev)


# -- MdSearchBar onTap (clicked) --------------------------------------------


def test_bar_click_on_field_emits_clicked(qtbot):
    bar = MdSearchBar()
    qtbot.addWidget(bar)
    taps = []
    bar.clicked.connect(lambda: taps.append(1))
    _press(bar._edit)  # press lands on the child QLineEdit
    assert taps == [1]


def test_bar_click_on_chrome_emits_clicked(qtbot):
    bar = MdSearchBar()
    qtbot.addWidget(bar)
    taps = []
    bar.clicked.connect(lambda: taps.append(1))
    _press(bar)  # press on the bar padding/icons
    assert taps == [1]


def test_bar_leading_icon_optional(qtbot):
    bar = MdSearchBar(leading_icon="")
    qtbot.addWidget(bar)
    assert bar._leading is None


# -- MdSearchView ------------------------------------------------------------


def test_open_fills_parent_full_screen(qtbot):
    host = _host(qtbot)
    host.show()
    view = MdSearchView(host)
    view.open()
    assert not view.isHidden()
    assert view.size() == host.size()
    assert view._panel.size() == host.size()


def test_provider_populates_suggestions_live(qtbot):
    host = _host(qtbot)
    fruits = ["apple", "apricot", "banana", "cherry"]
    view = MdSearchView(
        host,
        suggestions_provider=lambda q: [f for f in fruits if q.lower() in f],
    )
    view.set_text("ap")
    assert view.suggestions() == ["apple", "apricot"]
    view.set_text("err")
    assert view.suggestions() == ["cherry"]


def test_set_suggestions_manual(qtbot):
    host = _host(qtbot)
    view = MdSearchView(host)
    view.set_suggestions(["one", "two", "three"])
    assert view.suggestions() == ["one", "two", "three"]
    view.set_suggestions(["x"])
    assert view.suggestions() == ["x"]  # replaced, not appended


def test_selecting_suggestion_emits_and_closes(qtbot):
    host = _host(qtbot)
    host.show()
    view = MdSearchView(host)
    selected = []
    closed = []
    view.suggestionSelected.connect(selected.append)
    view.closed.connect(lambda: closed.append(1))
    view.open()
    view.set_suggestions(["alpha", "beta"])
    view._items[1].clicked.emit()
    assert selected == ["beta"]
    assert closed == [1]
    assert view.isHidden()


def test_textchanged_and_submitted_signals(qtbot):
    host = _host(qtbot)
    view = MdSearchView(host)
    changes = []
    submits = []
    view.textChanged.connect(changes.append)
    view.submitted.connect(submits.append)
    view.set_text("query")
    assert changes[-1] == "query"
    view._edit.returnPressed.emit()
    assert submits == ["query"]


def test_back_button_dismisses(qtbot):
    host = _host(qtbot)
    host.show()
    view = MdSearchView(host)
    rejected = []
    view.rejected.connect(lambda: rejected.append(1))
    view.open()
    view._back.click()
    assert rejected == [1]
    assert view.isHidden()


def test_clear_button_empties_query(qtbot):
    host = _host(qtbot)
    view = MdSearchView(host)
    view.set_text("something")
    view._clear.click()
    assert view.text() == ""


def test_non_full_screen_anchors_top(qtbot):
    host = _host(qtbot)
    host.show()
    view = MdSearchView(host, full_screen=False)
    view.open()
    # spans full width, capped height, anchored at the top
    assert view._panel.width() == host.width()
    assert view._panel.height() < host.height()
    assert view._panel.y() == 0


def test_renders(qtbot):
    host = _host(qtbot)
    host.show()
    view = MdSearchView(host, view_hint_text="Search recipes")
    view.open()
    view.set_suggestions(["pasta", "pizza", "pesto"])
    assert view.grab() is not None
