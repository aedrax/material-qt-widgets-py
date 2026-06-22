"""Tests for MdBanner."""

from __future__ import annotations

from material_qt.tokens.color import ColorRole
from material_qt.widgets.banner import MdBanner


def test_add_action_returns_clickable_button(qtbot):
    b = MdBanner("Your storage is almost full.", icon="warning")
    qtbot.addWidget(b)
    btn = b.add_action("Manage")
    fired = []
    btn.clicked.connect(lambda: fired.append(True))
    btn.click()
    assert fired == [True]


def test_elevation_property(qtbot):
    b = MdBanner("Message", elevation=2)
    qtbot.addWidget(b)
    assert b.elevation == 2
    b.set_elevation(3)
    assert b.elevation == 3


def test_background_role(qtbot):
    b = MdBanner("Message", background_role=ColorRole.SURFACE_CONTAINER)
    qtbot.addWidget(b)
    assert b.background_role == ColorRole.SURFACE_CONTAINER
    assert b._surface_role == ColorRole.SURFACE_CONTAINER
    b.set_background_role(ColorRole.SURFACE_CONTAINER_HIGH)
    assert b.background_role == ColorRole.SURFACE_CONTAINER_HIGH
    assert b._surface_role == ColorRole.SURFACE_CONTAINER_HIGH


def test_divider_role(qtbot):
    b = MdBanner("Message", divider_role=ColorRole.OUTLINE)
    qtbot.addWidget(b)
    assert b.divider_role == ColorRole.OUTLINE
    assert b._divider._color_role == ColorRole.OUTLINE
    b.set_divider_role(ColorRole.OUTLINE_VARIANT)
    assert b._divider._color_role == ColorRole.OUTLINE_VARIANT


def test_renders(qtbot):
    b = MdBanner("A two-line banner message that wraps.", icon="info")
    qtbot.addWidget(b)
    b.add_action("Dismiss")
    b.add_action("Action")
    b.resize(400, b.sizeHint().height())
    b.grab()
