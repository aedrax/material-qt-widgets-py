"""Tests for Material icon buttons."""

from __future__ import annotations

from material_qt.tokens.color import ColorRole
from material_qt.widgets.iconbutton import (
    MdFilledIconButton,
    MdIconButton,
    MdOutlinedIconButton,
)


def test_clicked(qtbot):
    b = MdFilledIconButton("favorite")
    qtbot.addWidget(b)
    clicks = []
    b.clicked.connect(lambda: clicks.append(1))
    b.click()
    assert clicks == [1]


def test_toggle_swaps_colors(qtbot):
    b = MdFilledIconButton("favorite", toggle=True)
    qtbot.addWidget(b)
    assert b._container_role() == ColorRole.SURFACE_CONTAINER_HIGHEST  # unselected
    b.setChecked(True)
    assert b._container_role() == ColorRole.PRIMARY  # selected


def test_toggle_selected_icon(qtbot):
    b = MdIconButton("a", toggle=True, selected_icon="b")
    qtbot.addWidget(b)
    assert b._current_icon() == "a"
    b.setChecked(True)
    assert b._current_icon() == "b"


def test_size_and_render(qtbot):
    for cls in (MdIconButton, MdFilledIconButton, MdOutlinedIconButton):
        b = cls("favorite")
        qtbot.addWidget(b)
        assert b.sizeHint().width() == 40 and b.sizeHint().height() == 40
        b.resize(b.sizeHint())
        b.grab()


def test_tooltip_and_long_press(qtbot):
    b = MdIconButton("favorite", tooltip="Like")
    qtbot.addWidget(b)
    assert b.toolTip() == "Like"
    fired = []
    b.longPressed.connect(lambda: fired.append(1))
    b._emit_long_press()
    assert fired == [1]
