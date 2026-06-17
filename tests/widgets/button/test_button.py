"""Tests for Material buttons."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QMouseEvent

from material_qt.tokens.color import ColorRole
from material_qt.tokens.elevation import ElevationLevel
from material_qt.widgets.button import (
    MdElevatedButton,
    MdFilledButton,
    MdOutlinedButton,
    MdTextButton,
)


def test_clicked_signal(qtbot):
    b = MdFilledButton("OK")
    qtbot.addWidget(b)
    clicks = []
    b.clicked.connect(lambda: clicks.append(1))
    b.click()
    assert clicks == [1]


def test_disabled_blocks_click(qtbot):
    b = MdFilledButton("OK")
    qtbot.addWidget(b)
    b.setEnabled(False)
    clicks = []
    b.clicked.connect(lambda: clicks.append(1))
    b.click()
    assert clicks == []


def test_variant_styles(qtbot):
    assert MdFilledButton.STYLE.container_role == ColorRole.PRIMARY
    assert MdFilledButton.STYLE.label_role == ColorRole.ON_PRIMARY
    assert MdElevatedButton.STYLE.elevation == ElevationLevel.LEVEL1
    assert MdElevatedButton.STYLE.hover_elevation == ElevationLevel.LEVEL2
    assert MdOutlinedButton.STYLE.container_role is None
    assert MdOutlinedButton.STYLE.outline_role == ColorRole.OUTLINE
    assert MdTextButton.STYLE.container_role is None


def test_height_and_icon_width(qtbot):
    b = MdFilledButton("Save")
    qtbot.addWidget(b)
    h = b.sizeHint().height()
    assert h == 40
    w_no_icon = b.sizeHint().width()
    b.set_icon("add")
    assert b.sizeHint().width() > w_no_icon


def test_has_ripple_and_focus(qtbot):
    b = MdFilledButton("x")
    qtbot.addWidget(b)
    assert b.ripple is not None
    assert b.focus_ring is not None


def test_renders_without_crash(qtbot):
    for cls in (MdFilledButton, MdElevatedButton, MdOutlinedButton, MdTextButton):
        b = cls("Hi", icon="add")
        qtbot.addWidget(b)
        b.resize(b.sizeHint())
        b.grab()  # forces a paintEvent
