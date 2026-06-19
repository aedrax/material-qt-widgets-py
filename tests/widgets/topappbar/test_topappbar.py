"""Tests for MdTopAppBar."""

from __future__ import annotations

import pytest

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
