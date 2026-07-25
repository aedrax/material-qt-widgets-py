"""Tests for MdBottomAppBar."""

from __future__ import annotations

from material_qt.widgets.bottomappbar import MdBottomAppBar
from material_qt.widgets.fab import MdFab


def test_default_height(qtbot):
    bar = MdBottomAppBar()
    qtbot.addWidget(bar)
    assert bar.height() == 80


def test_custom_height(qtbot):
    bar = MdBottomAppBar(height=64)
    qtbot.addWidget(bar)
    assert bar.height() == 64


def test_add_action_returns_button(qtbot):
    bar = MdBottomAppBar()
    qtbot.addWidget(bar)
    btn = bar.add_action("search")
    assert btn.icon_name == "search"
    assert bar.count() == 1


def test_actions_are_ordered_before_fab(qtbot):
    bar = MdBottomAppBar(notch=True)
    qtbot.addWidget(bar)
    bar.add_action("menu")
    bar.add_action("search")
    fab = MdFab("add")
    bar.set_fab(fab)
    assert bar.fab is fab
    assert bar.count() == 2


def test_set_fab_replaces_previous(qtbot):
    bar = MdBottomAppBar()
    qtbot.addWidget(bar)
    first = MdFab("add")
    bar.set_fab(first)
    second = MdFab("edit")
    bar.set_fab(second)
    assert bar.fab is second
    assert first.parent() is None


def test_clear_fab(qtbot):
    bar = MdBottomAppBar()
    qtbot.addWidget(bar)
    bar.set_fab(MdFab("add"))
    bar.set_fab(None)
    assert bar.fab is None


def test_set_notch_toggles(qtbot):
    bar = MdBottomAppBar()
    qtbot.addWidget(bar)
    assert bar.notch is False
    bar.set_notch(True)
    assert bar.notch is True


def test_renders_with_notch_and_fab(qtbot):
    bar = MdBottomAppBar(notch=True)
    qtbot.addWidget(bar)
    for icon in ["menu", "search", "favorite"]:
        bar.add_action(icon)
    bar.set_fab(MdFab("add"))
    bar.resize(400, 80)
    bar.grab()


def test_renders_without_notch(qtbot):
    bar = MdBottomAppBar()
    qtbot.addWidget(bar)
    bar.add_action("menu")
    bar.resize(400, 80)
    bar.grab()


def test_fab_positioned_trailing_after_resize(qtbot):
    bar = MdBottomAppBar(notch=True)
    qtbot.addWidget(bar)
    fab = MdFab("add")
    bar.set_fab(fab)
    bar.resize(400, 80)
    bar.grab()  # triggers paint, which positions the FAB for the current width
    # Trailing: right edge within the bar, near the right padding.
    assert fab.x() + fab.width() <= 400
    assert fab.x() > 200
    # Top-aligned and fully within bounds (no overhang Qt would clip).
    assert fab.y() >= 0
    assert fab.y() + fab.height() <= 80


def test_set_fab_deletes_replaced_fab(qtbot):
    """Regression: the replaced FAB was setParent(None) but never deleted,
    leaking a hidden parentless top-level."""
    from shiboken6 import isValid

    bar = MdBottomAppBar(notch=True)
    qtbot.addWidget(bar)
    old = MdFab("add")
    bar.set_fab(old)
    new = MdFab("edit")
    bar.set_fab(new)
    qtbot.wait(20)  # process the deferred delete
    assert not isValid(old)
    assert bar.fab is new
