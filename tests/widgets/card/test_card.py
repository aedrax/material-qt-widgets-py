"""Tests for MdCard."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel

from material_qt.tokens.color import ColorRole
from material_qt.tokens.elevation import ElevationLevel
from material_qt.widgets.card import CardVariant, MdCard


def test_variant_spec(qtbot):
    elevated = MdCard(variant=CardVariant.ELEVATED)
    outlined = MdCard(variant=CardVariant.OUTLINED)
    for c in (elevated, outlined):
        qtbot.addWidget(c)
    assert elevated._surface_role == ColorRole.SURFACE_CONTAINER_LOW
    assert elevated._elevation == ElevationLevel.LEVEL1
    assert outlined._outline_role == ColorRole.OUTLINE_VARIANT


def test_content(qtbot):
    card = MdCard()
    qtbot.addWidget(card)
    card.add_widget(QLabel("Hello"))
    assert card.content_layout().count() == 1


def test_renders(qtbot):
    for v in CardVariant:
        c = MdCard(variant=v)
        qtbot.addWidget(c)
        c.add_widget(QLabel("x"))
        c.resize(200, 120)
        c.grab()
