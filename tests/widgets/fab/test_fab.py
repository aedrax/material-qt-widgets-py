"""Tests for MdFab / MdBrandedFab."""

from __future__ import annotations

from material_qt.tokens.color import ColorRole
from material_qt.tokens.elevation import ElevationLevel
from material_qt.widgets.fab import FabColor, FabSize, MdBrandedFab, MdFab


def test_sizes(qtbot):
    small = MdFab("edit", size=FabSize.SMALL)
    reg = MdFab("edit", size=FabSize.REGULAR)
    large = MdFab("edit", size=FabSize.LARGE)
    for f in (small, reg, large):
        qtbot.addWidget(f)
    assert small.sizeHint().width() == 40
    assert reg.sizeHint().width() == 56
    assert large.sizeHint().width() == 96


def test_color_variant(qtbot):
    f = MdFab("add", color=FabColor.PRIMARY)
    qtbot.addWidget(f)
    assert f._cfg.container_role == ColorRole.PRIMARY_CONTAINER
    assert f._cfg.fg_role == ColorRole.ON_PRIMARY_CONTAINER


def test_rest_elevation(qtbot):
    f = MdFab("add")
    qtbot.addWidget(f)
    assert f._rest_elevation() == ElevationLevel.LEVEL3
    low = MdFab("add", lowered=True)
    qtbot.addWidget(low)
    assert low._rest_elevation() == ElevationLevel.LEVEL1


def test_extended_is_wider(qtbot):
    f = MdFab("add", label="Compose")
    qtbot.addWidget(f)
    assert f.sizeHint().height() == 56
    assert f.sizeHint().width() > 56


def test_renders(qtbot):
    for f in (
        MdFab("edit", size=FabSize.SMALL),
        MdFab("add", color=FabColor.TERTIARY),
        MdFab("add", label="Compose"),
        MdBrandedFab(),
        MdBrandedFab(label="Create"),
    ):
        qtbot.addWidget(f)
        f.resize(f.sizeHint())
        f.grab()


def test_tooltip_and_long_press(qtbot):
    f = MdFab("add", tooltip="Add item")
    qtbot.addWidget(f)
    assert f.toolTip() == "Add item"
    assert hasattr(f, "longPressed")
    fired = []
    f.longPressed.connect(lambda: fired.append(1))
    f._emit_long_press()
    assert fired == [1]
