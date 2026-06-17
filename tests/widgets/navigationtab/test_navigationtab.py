"""Tests for MdNavigationTab."""

from __future__ import annotations

from material_qt.widgets.navigationtab import MdNavigationTab


def test_checkable_active(qtbot):
    t = MdNavigationTab("Home", icon="home")
    qtbot.addWidget(t)
    assert t.isCheckable()
    t.setChecked(True)
    assert t.isChecked()


def test_active_icon_fallback(qtbot):
    t = MdNavigationTab("Home", icon="home")
    qtbot.addWidget(t)
    assert t._active_icon == "home"
    t2 = MdNavigationTab("Home", icon="home_outline", active_icon="home")
    qtbot.addWidget(t2)
    assert t2._active_icon == "home"


def test_size_and_render(qtbot):
    t = MdNavigationTab("Profile", icon="person")
    qtbot.addWidget(t)
    assert t.sizeHint().height() == 64
    t.setChecked(True)
    t.resize(t.sizeHint())
    t.grab()
