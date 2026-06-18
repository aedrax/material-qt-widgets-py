"""Tests for MdSplitButton."""

from __future__ import annotations

from material_qt.tokens.color import ColorRole
from material_qt.widgets.menu import MdMenu, MdMenuItem
from material_qt.widgets.splitbutton import MdSplitButton, SplitButtonColor


def test_leading_click_signal(qtbot):
    sb = MdSplitButton("Save")
    qtbot.addWidget(sb)
    seen = []
    sb.clicked.connect(lambda: seen.append(1))
    sb._leading.click()
    assert seen == [1]


def test_trailing_click_signal(qtbot):
    sb = MdSplitButton("Save")
    qtbot.addWidget(sb)
    seen = []
    sb.trailing_clicked.connect(lambda: seen.append(1))
    sb._trailing.click()
    assert seen == [1]


def test_color_variant_spec(qtbot):
    sb = MdSplitButton("Save", color=SplitButtonColor.TONAL)
    qtbot.addWidget(sb)
    assert sb._spec.container == ColorRole.SECONDARY_CONTAINER
    out = MdSplitButton("Save", color=SplitButtonColor.OUTLINED)
    qtbot.addWidget(out)
    assert out._spec.container is None
    assert out._spec.outline == ColorRole.OUTLINE


def test_trailing_opens_menu(qtbot):
    sb = MdSplitButton("Save")
    qtbot.addWidget(sb)
    menu = MdMenu(sb)
    menu.add_item(MdMenuItem("Save as draft"))
    sb.set_menu(menu)
    sb._trailing.click()
    assert menu.isVisible()
    menu.close()


def test_disabled_propagates(qtbot):
    sb = MdSplitButton("Save")
    qtbot.addWidget(sb)
    sb.setEnabled(False)
    assert not sb._leading.isEnabled()
    assert not sb._trailing.isEnabled()


def test_renders(qtbot):
    for color in SplitButtonColor:
        sb = MdSplitButton("Save", color=color, icon="save")
        qtbot.addWidget(sb)
        sb.resize(sb.sizeHint())
        sb.grab()
