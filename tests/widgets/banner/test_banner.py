"""Tests for MdBanner."""

from __future__ import annotations

from material_qt.widgets.banner import MdBanner


def test_add_action_returns_clickable_button(qtbot):
    b = MdBanner("Your storage is almost full.", icon="warning")
    qtbot.addWidget(b)
    btn = b.add_action("Manage")
    fired = []
    btn.clicked.connect(lambda: fired.append(True))
    btn.click()
    assert fired == [True]


def test_renders(qtbot):
    b = MdBanner("A two-line banner message that wraps.", icon="info")
    qtbot.addWidget(b)
    b.add_action("Dismiss")
    b.add_action("Action")
    b.resize(400, b.sizeHint().height())
    b.grab()
