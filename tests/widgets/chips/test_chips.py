"""Tests for Material chips."""

from __future__ import annotations

from PySide6.QtGui import QColor, QFont, QPixmap

from material_qt.tokens.color import ColorRole
from material_qt.widgets.chips import (
    MdAssistChip,
    MdChip,
    MdChipSet,
    MdChoiceChip,
    MdFilterChip,
    MdInputChip,
    MdSuggestionChip,
)


def test_filter_selectable(qtbot):
    c = MdFilterChip("All")
    qtbot.addWidget(c)
    assert c.isCheckable()
    assert c._container_role() is None
    c.setChecked(True)
    assert c._container_role() == ColorRole.SECONDARY_CONTAINER
    assert c._show_leading_check() is True


def test_assist_has_icon_width(qtbot):
    plain = MdAssistChip("Hi")
    withicon = MdAssistChip("Hi", icon="event")
    for c in (plain, withicon):
        qtbot.addWidget(c)
    assert withicon.sizeHint().width() > plain.sizeHint().width()


def test_input_chip_removed_signal_and_set(qtbot):
    cs = MdChipSet()
    qtbot.addWidget(cs)
    chip = MdInputChip("Alice", icon="person")
    cs.add_chip(chip)
    removed = []
    chip.removed.connect(lambda: removed.append(1))
    chip.removed.emit()
    assert removed == [1]


def test_chip_set_add_remove(qtbot):
    cs = MdChipSet()
    qtbot.addWidget(cs)
    chip = MdInputChip("X")
    cs.add_chip(chip)
    # add_chip inserts before the trailing stretch.
    assert cs._lay.count() == 2
    cs.remove_chip(chip)
    assert cs._lay.count() == 1


def test_renders(qtbot):
    for c in (
        MdAssistChip("Assist", icon="event"),
        MdSuggestionChip("Suggestion"),
        MdFilterChip("Filter", selected=True),
        MdInputChip("Input", icon="person"),
    ):
        qtbot.addWidget(c)
        c.resize(c.sizeHint())
        c.grab()


def test_filter_chip_expands_when_selected(qtbot):
    """Regression: selecting a filter chip adds a checkmark, so its size hint
    must grow (and updateGeometry fire) or the label gets clipped."""
    c = MdFilterChip("Unread")
    qtbot.addWidget(c)
    unselected_w = c.sizeHint().width()
    c.setChecked(True)
    assert c.sizeHint().width() > unselected_w


# -- avatar (Flutter `avatar`) --------------------------------------------


def _solid_pixmap(size: int = 24) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(QColor("red"))
    return pm


def test_avatar_widens_size_hint(qtbot):
    plain = MdAssistChip("Bob")
    withavatar = MdAssistChip("Bob", avatar=_solid_pixmap())
    for c in (plain, withavatar):
        qtbot.addWidget(c)
    assert withavatar.avatar is not None
    assert withavatar.sizeHint().width() > plain.sizeHint().width()


def test_set_avatar_setter(qtbot):
    c = MdInputChip("Carol")
    qtbot.addWidget(c)
    before = c.sizeHint().width()
    c.set_avatar(_solid_pixmap())
    assert c.avatar is not None
    assert c.sizeHint().width() > before
    c.set_avatar(None)
    assert c.avatar is None
    assert c.sizeHint().width() == before


# -- idiomatic property setters -------------------------------------------


def test_set_label_updates_text_and_width(qtbot):
    c = MdAssistChip("Hi")
    qtbot.addWidget(c)
    narrow = c.sizeHint().width()
    c.set_label("A much longer label")
    assert c.label == "A much longer label"
    assert c.sizeHint().width() > narrow


def test_set_label_style_font(qtbot):
    c = MdAssistChip("Hi")
    qtbot.addWidget(c)
    big = QFont(c.font())
    big.setPointSize(c.font().pointSize() + 12)
    base = c.sizeHint().width()
    c.set_label_style(big)
    assert c.sizeHint().width() > base


def test_set_selected_proxies_checked(qtbot):
    c = MdFilterChip("On")
    qtbot.addWidget(c)
    assert c.selected is False
    c.set_selected(True)
    assert c.isChecked() is True
    assert c.selected is True


def test_set_leading_and_trailing_icon(qtbot):
    c = MdAssistChip("Go")
    qtbot.addWidget(c)
    base = c.sizeHint().width()
    c.set_leading_icon("event")
    assert c.sizeHint().width() > base
    with_lead = c.sizeHint().width()
    c.set_trailing_icon("close")
    assert c.sizeHint().width() > with_lead


# -- theme-role color overrides -------------------------------------------


def test_background_and_selected_color_roles(qtbot):
    c = MdFilterChip("Tag")
    qtbot.addWidget(c)
    # Default unselected container is transparent (outlined).
    assert c._container_role() is None
    c.set_background_color(ColorRole.SURFACE_CONTAINER_HIGH)
    assert c._container_role() == ColorRole.SURFACE_CONTAINER_HIGH
    c.set_selected(True)
    # Default selected role.
    assert c._container_role() == ColorRole.SECONDARY_CONTAINER
    c.set_selected_color(ColorRole.TERTIARY_CONTAINER)
    assert c._container_role() == ColorRole.TERTIARY_CONTAINER


# -- checkmark styling -----------------------------------------------------


def test_show_checkmark_toggle(qtbot):
    c = MdFilterChip("X", selected=True)
    qtbot.addWidget(c)
    assert c._show_leading_check() is True
    width_with_check = c.sizeHint().width()
    c.set_show_checkmark(False)
    assert c._show_leading_check() is False
    assert c.sizeHint().width() < width_with_check


def test_checkmark_color_accepts_role(qtbot):
    c = MdFilterChip("X", selected=True)
    qtbot.addWidget(c)
    c.set_checkmark_color(ColorRole.PRIMARY)
    assert c._checkmark_role == ColorRole.PRIMARY
    c.resize(c.sizeHint())
    c.grab()  # renders the custom-colored checkmark without error


# -- ChoiceChip (single-select) -------------------------------------------


def test_choice_chip_fills_without_checkmark(qtbot):
    c = MdChoiceChip("Small")
    qtbot.addWidget(c)
    assert c.isCheckable()
    assert c._container_role() is None
    c.set_selected(True)
    assert c._container_role() == ColorRole.SECONDARY_CONTAINER
    # Unlike a filter chip, a choice chip shows no leading checkmark.
    assert c._show_leading_check() is False


def test_choice_chip_initial_selected(qtbot):
    c = MdChoiceChip("Medium", selected=True)
    qtbot.addWidget(c)
    assert c.isChecked() is True


# -- deletable FilterChip (Flutter onDeleted) -----------------------------


def test_filter_chip_deletable_emits_removed(qtbot):
    c = MdFilterChip("Dismissable", deletable=True)
    qtbot.addWidget(c)
    assert c._trailing_icon == "close"
    seen = []
    c.removed.connect(lambda: seen.append(1))
    c.removed.emit()
    assert seen == [1]


def test_filter_chip_not_deletable_by_default(qtbot):
    c = MdFilterChip("Plain")
    qtbot.addWidget(c)
    assert c._trailing_icon == ""


def test_chip_set_removes_deletable_filter_chip(qtbot):
    cs = MdChipSet()
    qtbot.addWidget(cs)
    chip = MdFilterChip("Tag", deletable=True)
    cs.add_chip(chip)
    assert cs._lay.count() == 2
    chip.removed.emit()
    assert cs._lay.count() == 1


# -- elevated variant ------------------------------------------------------


def test_elevated_chip_has_filled_body_no_outline_and_shadow(qtbot):
    c = MdAssistChip("Lifted", elevated=True)
    qtbot.addWidget(c)
    assert c._outline_visible() is False
    # Elevated chips fill their body (so the drop shadow is chip-shaped, not
    # text-shaped) — they must NOT be transparent.
    assert c._container_role() == ColorRole.SURFACE_CONTAINER_LOW
    assert c.graphicsEffect() is not None
    c.resize(c.sizeHint())
    c.grab()


def test_elevated_filter_chip_filled_when_unselected(qtbot):
    c = MdFilterChip("Lifted", elevated=True)
    qtbot.addWidget(c)
    assert c._outline_visible() is False
    assert c._container_role() == ColorRole.SURFACE_CONTAINER_LOW
    c.set_selected(True)
    assert c._container_role() == ColorRole.SECONDARY_CONTAINER


# -- enabled state ---------------------------------------------------------


def test_disabled_chip_renders(qtbot):
    c = MdAssistChip("Off", icon="event")
    qtbot.addWidget(c)
    c.setEnabled(False)
    assert c.isEnabled() is False
    c.resize(c.sizeHint())
    c.grab()


def test_base_chip_clicked_signal(qtbot):
    c = MdChip("Tap")
    qtbot.addWidget(c)
    clicks = []
    c.clicked.connect(lambda: clicks.append(1))
    c.click()
    assert clicks == [1]
