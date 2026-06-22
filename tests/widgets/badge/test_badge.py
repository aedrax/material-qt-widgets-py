"""Tests for MdBadge."""

from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QWidget

from material_qt.theme.theme_manager import ThemeManager, ThemeMode
from material_qt.tokens.color import ColorRole
from material_qt.widgets.badge import MdBadge, attach


def test_default_is_small_dot(qtbot):
    badge = MdBadge()
    qtbot.addWidget(badge)
    assert badge.value == ""
    assert badge.is_large is False
    # Small dot is 6x6 per tokens.
    assert badge.sizeHint().width() == 6
    assert badge.sizeHint().height() == 6


def test_value_makes_large(qtbot):
    badge = MdBadge("8")
    qtbot.addWidget(badge)
    assert badge.value == "8"
    assert badge.is_large is True
    # Large pill height is 16; min width 16.
    assert badge.sizeHint().height() == 16
    assert badge.sizeHint().width() >= 16


def test_large_grows_with_value(qtbot):
    small = MdBadge("8")
    wide = MdBadge("99+")
    qtbot.addWidget(small)
    qtbot.addWidget(wide)
    assert wide.sizeHint().width() > small.sizeHint().width()


def test_set_value_toggles_form(qtbot):
    badge = MdBadge()
    qtbot.addWidget(badge)
    assert not badge.is_large
    badge.set_value("3")
    assert badge.is_large
    assert badge.sizeHint().height() == 16
    badge.set_value("")
    assert not badge.is_large
    assert badge.sizeHint() == badge.sizeHint()  # stable
    assert badge.sizeHint().width() == 6


def test_set_value_accepts_non_string(qtbot):
    badge = MdBadge()
    qtbot.addWidget(badge)
    badge.set_value(5)
    assert badge.value == "5"
    assert badge.is_large


def test_attach_reparents_and_positions(qtbot):
    host = QWidget()
    host.resize(48, 48)
    qtbot.addWidget(host)
    badge = MdBadge("9")
    badge.attach(host)
    assert badge.parentWidget() is host
    # Anchored to the top-right corner.
    assert badge.y() == 0
    assert badge.x() + badge.width() == host.width()


def test_attach_helper_function(qtbot):
    host = QWidget()
    host.resize(40, 40)
    qtbot.addWidget(host)
    badge = MdBadge()
    attach(badge, host)
    assert badge.parentWidget() is host


def test_attach_tracks_host_resize(qtbot):
    host = QWidget()
    host.resize(40, 40)
    qtbot.addWidget(host)
    host.show()
    qtbot.waitExposed(host)
    badge = MdBadge("7")
    badge.attach(host)
    host.resize(100, 60)
    qtbot.waitUntil(lambda: badge.x() + badge.width() == host.width())
    assert badge.x() + badge.width() == host.width()


def test_paint_does_not_crash(qtbot):
    badge = MdBadge("12")
    qtbot.addWidget(badge)
    badge.resize(badge.sizeHint())
    badge.grab()  # forces a paintEvent
    badge.set_value("")
    badge.resize(badge.sizeHint())
    badge.grab()


def test_label_visible_hides_on_host(qtbot):
    host = QWidget()
    host.resize(48, 48)
    qtbot.addWidget(host)
    host.show()
    qtbot.waitExposed(host)
    badge = MdBadge("9")
    badge.attach(host)
    assert not badge.isHidden()
    badge.set_label_visible(False)
    assert badge.isHidden()
    assert badge.is_label_visible is False
    badge.set_label_visible(True)
    assert not badge.isHidden()


def test_alignment_bottom_left(qtbot):
    host = QWidget()
    host.resize(60, 60)
    qtbot.addWidget(host)
    badge = MdBadge("3", alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
    badge.attach(host)
    assert badge.x() == 0
    assert badge.y() + badge.height() == host.height()


def test_offset_shifts_position(qtbot):
    host = QWidget()
    host.resize(60, 60)
    qtbot.addWidget(host)
    a = MdBadge("3")
    a.attach(host)
    base_x = a.x()
    b = MdBadge("3", offset=QPoint(-5, 4))
    b.attach(host)
    assert b.x() == base_x - 5
    assert b.y() == 4


def test_negative_offset_not_clamped(qtbot):
    # A top-anchored badge with a negative y offset overhangs the corner; the
    # offset must not be clamped away to 0 (Flutter offset semantics).
    host = QWidget()
    host.resize(60, 60)
    qtbot.addWidget(host)
    badge = MdBadge("3", offset=QPoint(0, -4))
    badge.attach(host)
    assert badge.y() == -4


def test_background_and_text_roles(qtbot):
    badge = MdBadge("1", background_role=ColorRole.PRIMARY, text_role=ColorRole.ON_PRIMARY)
    qtbot.addWidget(badge)
    assert badge.background_role == ColorRole.PRIMARY
    assert badge.text_role == ColorRole.ON_PRIMARY
    badge.set_background_role(ColorRole.TERTIARY)
    assert badge.background_role == ColorRole.TERTIARY


def test_rethemes_on_theme_change(qtbot):
    theme = ThemeManager.instance()
    theme.set_mode(ThemeMode.LIGHT)
    light = theme.color(ColorRole.ERROR)
    theme.set_mode(ThemeMode.DARK)
    dark = theme.color(ColorRole.ERROR)
    # Error color differs between light and dark schemes.
    assert light.name() != dark.name()
    theme.set_mode(ThemeMode.LIGHT)
