"""Tests for MdToolbar."""

from __future__ import annotations

from material_qt.widgets.toolbar import MdToolbar, ToolbarVariant


def test_add_action_returns_button(qtbot):
    tb = MdToolbar()
    qtbot.addWidget(tb)
    btn = tb.add_action("format_bold")
    assert btn.icon_name == "format_bold"
    assert tb.count() == 1


def test_renders_both_variants(qtbot):
    for variant in ToolbarVariant:
        tb = MdToolbar(variant=variant)
        qtbot.addWidget(tb)
        for icon in ["undo", "redo", "format_bold", "more_vert"]:
            tb.add_action(icon)
        tb.resize(280, 64)
        tb.grab()
