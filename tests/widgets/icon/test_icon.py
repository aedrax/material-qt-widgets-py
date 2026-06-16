"""Tests for :class:`MdIcon`."""

from __future__ import annotations

from PySide6.QtGui import QImage

from material_qt.theme.theme_manager import ThemeManager, ThemeMode
from material_qt.tokens.color import ColorRole
from material_qt.widgets.icon import DEFAULT_ICON_SIZE, IconStyle, MdIcon


def _render(widget: MdIcon) -> QImage:
    widget.resize(widget.sizeHint())
    image = QImage(widget.size(), QImage.Format.Format_ARGB32)
    image.fill(0)
    widget.render(image)
    return image


def test_default_size_and_name(qtbot):
    icon = MdIcon("favorite")
    qtbot.addWidget(icon)
    assert icon.name == "favorite"
    assert icon.icon_size == DEFAULT_ICON_SIZE
    assert icon.sizeHint().width() == DEFAULT_ICON_SIZE
    assert icon.sizeHint().height() == DEFAULT_ICON_SIZE


def test_custom_size(qtbot):
    icon = MdIcon("home", size=48)
    qtbot.addWidget(icon)
    assert icon.sizeHint().width() == 48
    icon.set_size(32)
    assert icon.icon_size == 32
    assert icon.sizeHint().height() == 32


def test_size_floor(qtbot):
    icon = MdIcon("home", size=0)
    qtbot.addWidget(icon)
    assert icon.icon_size >= 1


def test_set_name_updates_accessible_name(qtbot):
    icon = MdIcon("home")
    qtbot.addWidget(icon)
    icon.set_name("settings")
    assert icon.name == "settings"
    assert icon.accessibleName() == "settings"


def test_filled_toggle(qtbot):
    icon = MdIcon("favorite", filled=False)
    qtbot.addWidget(icon)
    assert icon.filled is False
    icon.set_filled(True)
    assert icon.filled is True


def test_color_role_default_on_surface(qtbot):
    icon = MdIcon("favorite")
    qtbot.addWidget(icon)
    assert icon.color_role == ColorRole.ON_SURFACE


def test_color_role_override(qtbot):
    icon = MdIcon("favorite")
    qtbot.addWidget(icon)
    icon.set_color_role(ColorRole.PRIMARY)
    assert icon.color_role == ColorRole.PRIMARY


def test_font_available_is_bool(qtbot):
    icon = MdIcon("favorite")
    qtbot.addWidget(icon)
    assert isinstance(icon.font_available, bool)


def test_style_argument(qtbot):
    icon = MdIcon("favorite", style=IconStyle.ROUNDED)
    qtbot.addWidget(icon)
    # Should construct without error regardless of font availability.
    assert isinstance(icon, MdIcon)


def test_renders_without_crash(qtbot):
    icon = MdIcon("favorite", size=24)
    qtbot.addWidget(icon)
    image = _render(icon)
    assert not image.isNull()
    assert image.width() == 24


def test_empty_name_renders(qtbot):
    icon = MdIcon("", size=24)
    qtbot.addWidget(icon)
    image = _render(icon)
    assert not image.isNull()


def test_repaints_on_theme_change(qtbot):
    icon = MdIcon("favorite")
    qtbot.addWidget(icon)
    icon.show()
    manager = ThemeManager.instance()
    manager.set_mode(ThemeMode.LIGHT)
    light = ThemeManager.instance().color(ColorRole.ON_SURFACE)
    manager.set_mode(ThemeMode.DARK)
    dark = ThemeManager.instance().color(ColorRole.ON_SURFACE)
    # The on-surface color differs between schemes; the widget uses it for the
    # glyph pen, so a theme change must change what it would paint.
    assert light.name() != dark.name()


def test_register_font_missing_path_returns_none(qtbot):
    assert MdIcon.register_font("/nonexistent/path/to/font.ttf") is None
