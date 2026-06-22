"""MdDivider: sizing, inset geometry, theming, and orientation."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage

from material_qt.theme.theme_manager import ThemeManager, ThemeMode
from material_qt.tokens.color import ColorRole
from material_qt.widgets.divider import MdDivider
from material_qt.widgets.divider.divider import INSET_PX, THICKNESS_PX


def _grab_image(widget) -> QImage:
    return widget.grab().toImage()


def test_default_thickness_horizontal(qapp):
    d = MdDivider()
    assert d.orientation() == Qt.Orientation.Horizontal
    assert d.height() == THICKNESS_PX
    assert d.maximumHeight() == THICKNESS_PX


def test_vertical_thickness(qapp):
    d = MdDivider(orientation=Qt.Orientation.Vertical)
    assert d.orientation() == Qt.Orientation.Vertical
    assert d.width() == THICKNESS_PX
    assert d.maximumWidth() == THICKNESS_PX


def test_inset_defaults_false(qapp):
    d = MdDivider()
    assert d.inset is False
    assert d.inset_start is False
    assert d.inset_end is False


def test_full_width_line_spans_widget(qapp):
    d = MdDivider()
    d.resize(200, THICKNESS_PX)
    rect = d._line_rect()
    assert rect.left() == 0
    assert rect.width() == 200


def test_inset_both_sides(qapp):
    d = MdDivider()
    d.inset = True
    d.resize(200, THICKNESS_PX)
    rect = d._line_rect()
    assert rect.left() == INSET_PX
    assert rect.width() == 200 - 2 * INSET_PX


def test_inset_start_only(qapp):
    d = MdDivider()
    d.inset_start = True
    d.resize(200, THICKNESS_PX)
    rect = d._line_rect()
    assert rect.left() == INSET_PX
    assert rect.right() == 199


def test_inset_end_only(qapp):
    d = MdDivider()
    d.inset_end = True
    d.resize(200, THICKNESS_PX)
    rect = d._line_rect()
    assert rect.left() == 0
    assert rect.width() == 200 - INSET_PX


def test_inset_rtl_swaps_edges(qapp):
    d = MdDivider()
    d.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    d.inset_start = True  # leading == right edge in RTL
    d.resize(200, THICKNESS_PX)
    rect = d._line_rect()
    assert rect.left() == 0
    assert rect.width() == 200 - INSET_PX


def test_vertical_inset(qapp):
    d = MdDivider(orientation=Qt.Orientation.Vertical)
    d.inset = True
    d.resize(THICKNESS_PX, 200)
    rect = d._line_rect()
    assert rect.top() == INSET_PX
    assert rect.height() == 200 - 2 * INSET_PX


def test_paint_uses_outline_variant_color(qapp):
    ThemeManager.instance().set_mode(ThemeMode.LIGHT)
    d = MdDivider()
    d.resize(40, THICKNESS_PX)
    img = _grab_image(d)
    expected = ThemeManager.instance().color(ColorRole.OUTLINE_VARIANT)
    pixel = QColor(img.pixel(20, 0))
    assert pixel.red() == expected.red()
    assert pixel.green() == expected.green()
    assert pixel.blue() == expected.blue()


def test_paint_repaints_on_theme_change(qapp):
    ThemeManager.instance().set_mode(ThemeMode.LIGHT)
    d = MdDivider()
    d.resize(40, THICKNESS_PX)
    light = QColor(_grab_image(d).pixel(20, 0))

    ThemeManager.instance().set_mode(ThemeMode.DARK)
    dark = QColor(_grab_image(d).pixel(20, 0))

    expected_dark = ThemeManager.instance().color(ColorRole.OUTLINE_VARIANT)
    assert (dark.red(), dark.green(), dark.blue()) == (
        expected_dark.red(),
        expected_dark.green(),
        expected_dark.blue(),
    )
    assert light.rgb() != dark.rgb()


def test_inset_setters_trigger_update(qapp):
    d = MdDivider()
    # Setting the same value is a no-op; flipping changes state.
    d.inset = False
    assert d.inset is False
    d.inset = True
    assert d.inset is True


def test_set_orientation_switches_fixed_dimension(qapp):
    d = MdDivider()
    assert d.maximumHeight() == THICKNESS_PX
    d.set_orientation(Qt.Orientation.Vertical)
    assert d.orientation() == Qt.Orientation.Vertical
    assert d.maximumWidth() == THICKNESS_PX


def test_custom_thickness(qapp):
    d = MdDivider(thickness=4)
    assert d.thickness == 4
    assert d.height() == 4
    d.thickness = 2
    assert d.thickness == 2
    assert d.maximumHeight() == 2


def test_numeric_indent(qapp):
    d = MdDivider(indent=10, end_indent=20)
    d.resize(200, THICKNESS_PX)
    rect = d._line_rect()
    assert rect.left() == 10
    assert rect.width() == 200 - 10 - 20


def test_numeric_indent_stacks_with_boolean_inset(qapp):
    d = MdDivider(indent=8)
    d.inset_start = True
    d.resize(200, THICKNESS_PX)
    rect = d._line_rect()
    assert rect.left() == INSET_PX + 8


def test_color_role_setter(qapp):
    d = MdDivider()
    assert d.color_role == ColorRole.OUTLINE_VARIANT
    d.set_color_role(ColorRole.PRIMARY)
    assert d.color_role == ColorRole.PRIMARY


def test_color_role_paint(qapp):
    ThemeManager.instance().set_mode(ThemeMode.LIGHT)
    d = MdDivider(color_role=ColorRole.PRIMARY)
    d.resize(40, THICKNESS_PX)
    img = _grab_image(d)
    expected = ThemeManager.instance().color(ColorRole.PRIMARY)
    pixel = QColor(img.pixel(20, 0))
    assert (pixel.red(), pixel.green(), pixel.blue()) == (
        expected.red(),
        expected.green(),
        expected.blue(),
    )
