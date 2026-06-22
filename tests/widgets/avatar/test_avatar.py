"""Tests for MdCircleAvatar."""

from __future__ import annotations

from PySide6.QtGui import QColor, QPixmap

from material_qt.tokens.color import ColorRole
from material_qt.widgets.avatar import MdCircleAvatar


def test_default_radius_and_size(qtbot):
    a = MdCircleAvatar(text="AB")
    qtbot.addWidget(a)
    assert a.radius == 20
    # radius=20 -> 40px circle.
    assert a.size().width() == 40
    assert a.size().height() == 40


def test_radius_setter_resizes(qtbot):
    a = MdCircleAvatar(text="AB", radius=24)
    qtbot.addWidget(a)
    assert a.size().width() == 48
    a.radius = 12
    assert a.size().width() == 24


def test_text_property(qtbot):
    a = MdCircleAvatar(text="JS")
    qtbot.addWidget(a)
    assert a.text == "JS"
    a.set_text("KL")
    assert a.text == "KL"


def test_color_roles(qtbot):
    a = MdCircleAvatar(
        text="X",
        background_role=ColorRole.TERTIARY_CONTAINER,
        foreground_role=ColorRole.ON_TERTIARY_CONTAINER,
    )
    qtbot.addWidget(a)
    assert a.background_role == ColorRole.TERTIARY_CONTAINER
    assert a.foreground_role == ColorRole.ON_TERTIARY_CONTAINER


def test_image_from_pixmap(qtbot):
    pm = QPixmap(40, 40)
    pm.fill(QColor("red"))
    a = MdCircleAvatar(image=pm)
    qtbot.addWidget(a)
    assert a.pixmap is not None and not a.pixmap.isNull()


def test_null_pixmap_falls_back(qtbot):
    a = MdCircleAvatar(text="AB", image=QPixmap())  # null pixmap
    qtbot.addWidget(a)
    assert a.pixmap is None


def test_set_image_none_clears(qtbot):
    pm = QPixmap(10, 10)
    pm.fill(QColor("blue"))
    a = MdCircleAvatar(image=pm)
    qtbot.addWidget(a)
    a.set_image(None)
    assert a.pixmap is None


def test_renders_text(qtbot):
    a = MdCircleAvatar(text="AB")
    qtbot.addWidget(a)
    a.grab()


def test_renders_image(qtbot):
    pm = QPixmap(40, 40)
    pm.fill(QColor("green"))
    a = MdCircleAvatar(image=pm)
    qtbot.addWidget(a)
    a.grab()
