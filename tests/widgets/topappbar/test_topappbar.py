"""Tests for MdTopAppBar."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QLabel

from material_qt.tokens.elevation import ElevationLevel
from material_qt.widgets.topappbar import MdTopAppBar, TopAppBarVariant


@pytest.mark.parametrize(
    ("variant", "height"),
    [
        (TopAppBarVariant.CENTER, 64),
        (TopAppBarVariant.SMALL, 64),
        (TopAppBarVariant.MEDIUM, 112),
        (TopAppBarVariant.LARGE, 152),
    ],
)
def test_variant_height(qtbot, variant, height):
    bar = MdTopAppBar("Title", variant=variant)
    qtbot.addWidget(bar)
    assert bar.height() == height


def test_set_title(qtbot):
    bar = MdTopAppBar("Old")
    qtbot.addWidget(bar)
    bar.set_title("New")
    assert bar._title.text() == "New"


def test_add_action_returns_button(qtbot):
    bar = MdTopAppBar("Title")
    qtbot.addWidget(bar)
    btn = bar.add_action("search")
    assert btn.icon_name == "search"


@pytest.mark.parametrize(
    ("variant", "expanded"),
    [(TopAppBarVariant.MEDIUM, 112), (TopAppBarVariant.LARGE, 152)],
)
def test_collapse_interpolates_height(qtbot, variant, expanded):
    bar = MdTopAppBar("Title", variant=variant)
    qtbot.addWidget(bar)
    bar.set_collapse_fraction(0.0)
    assert bar.height() == expanded
    bar.set_collapse_fraction(1.0)
    assert bar.height() == 64
    bar.set_collapse_fraction(0.5)
    assert bar.height() == round(expanded - (expanded - 64) * 0.5)


def test_collapse_fraction_clamps(qtbot):
    bar = MdTopAppBar("Title", variant=TopAppBarVariant.LARGE)
    qtbot.addWidget(bar)
    bar.set_collapse_fraction(-0.3)
    assert bar.collapse_fraction == 0.0 and bar.height() == 152
    bar.set_collapse_fraction(1.5)
    assert bar.collapse_fraction == 1.0 and bar.height() == 64


def test_collapse_noop_on_single_row(qtbot):
    bar = MdTopAppBar("Title", variant=TopAppBarVariant.SMALL)
    qtbot.addWidget(bar)
    bar.set_collapse_fraction(1.0)
    assert bar.height() == 64


def test_renders_all_variants(qtbot):
    for variant in TopAppBarVariant:
        bar = MdTopAppBar("Mail", variant=variant)
        qtbot.addWidget(bar)
        bar.add_action("search")
        bar.add_action("more_vert")
        bar.resize(400, bar.height())
        bar.grab()


def test_toolbar_height_override_shifts_height(qtbot):
    bar = MdTopAppBar("Title", variant=TopAppBarVariant.SMALL, toolbar_height=56)
    qtbot.addWidget(bar)
    assert bar.height() == 56
    # Two-row variant shifts by the same delta (-8): 112 -> 104.
    medium = MdTopAppBar("Title", variant=TopAppBarVariant.MEDIUM, toolbar_height=56)
    qtbot.addWidget(medium)
    assert medium.height() == 104
    medium.set_collapse_fraction(1.0)
    assert medium.height() == 56


def test_bottom_slot_grows_height(qtbot):
    tabs = QLabel("Tabs")
    tabs.setFixedHeight(48)
    bar = MdTopAppBar("Title", variant=TopAppBarVariant.SMALL, bottom=tabs)
    qtbot.addWidget(bar)
    assert bar.height() == 64 + 48


def test_set_bottom_after_construction(qtbot):
    bar = MdTopAppBar("Title", variant=TopAppBarVariant.SMALL)
    qtbot.addWidget(bar)
    assert bar.height() == 64
    tabs = QLabel("Tabs")
    tabs.setFixedHeight(40)
    bar.set_bottom(tabs)
    assert bar.height() == 64 + 40
    bar.set_bottom(None)
    assert bar.height() == 64


def test_bottom_persists_through_collapse(qtbot):
    tabs = QLabel("Tabs")
    tabs.setFixedHeight(48)
    bar = MdTopAppBar("Title", variant=TopAppBarVariant.MEDIUM, bottom=tabs)
    qtbot.addWidget(bar)
    assert bar.height() == 112 + 48
    bar.set_collapse_fraction(1.0)
    assert bar.height() == 64 + 48


def test_scrolled_under_elevation(qtbot):
    bar = MdTopAppBar("Title", variant=TopAppBarVariant.LARGE)
    qtbot.addWidget(bar)
    assert bar._elevation == ElevationLevel.LEVEL0
    bar.set_collapse_fraction(0.5)
    assert bar._elevation == ElevationLevel.LEVEL3
    bar.set_collapse_fraction(0.0)
    assert bar._elevation == ElevationLevel.LEVEL0
