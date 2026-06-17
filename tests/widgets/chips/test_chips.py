"""Tests for Material chips."""

from __future__ import annotations

from material_qt.tokens.color import ColorRole
from material_qt.widgets.chips import (
    MdAssistChip,
    MdChipSet,
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
