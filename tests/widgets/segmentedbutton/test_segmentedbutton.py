"""Tests for segmented buttons."""

from __future__ import annotations

from material_qt.widgets.segmentedbutton import (
    MdSegmentedButton,
    MdSegmentedButtonSet,
)
from material_qt.widgets.segmentedbutton.segmentedbutton import _Pos


def test_positions_assigned(qtbot):
    s = MdSegmentedButtonSet()
    qtbot.addWidget(s)
    segs = [MdSegmentedButton(t) for t in ("A", "B", "C")]
    for seg in segs:
        s.add_segment(seg)
    assert segs[0]._pos == _Pos.FIRST
    assert segs[1]._pos == _Pos.MIDDLE
    assert segs[2]._pos == _Pos.LAST


def test_single_select_exclusive(qtbot):
    s = MdSegmentedButtonSet()
    qtbot.addWidget(s)
    a, b = MdSegmentedButton("A"), MdSegmentedButton("B")
    s.add_segment(a)
    s.add_segment(b)
    a.setChecked(True)
    b.setChecked(True)
    assert b.isChecked() and not a.isChecked()


def test_multi_select_independent(qtbot):
    s = MdSegmentedButtonSet(multi=True)
    qtbot.addWidget(s)
    a, b = MdSegmentedButton("A"), MdSegmentedButton("B")
    s.add_segment(a)
    s.add_segment(b)
    a.setChecked(True)
    b.setChecked(True)
    assert a.isChecked() and b.isChecked()


def test_changed_signal_emits_indices(qtbot):
    s = MdSegmentedButtonSet(multi=True)
    qtbot.addWidget(s)
    a, b = MdSegmentedButton("A"), MdSegmentedButton("B")
    s.add_segment(a)
    s.add_segment(b)
    seen = []
    s.changed.connect(seen.append)
    a.click()
    b.click()
    assert seen[-1] == [0, 1]


def test_selection_changed_emits_values(qtbot):
    s = MdSegmentedButtonSet(multi=True)
    qtbot.addWidget(s)
    s.add_segment(MdSegmentedButton("A", value="a"))
    s.add_segment(MdSegmentedButton("B", value="b"))
    seen = []
    s.selectionChanged.connect(seen.append)
    s.segments()[1].click()
    assert seen[-1] == ["b"]


def test_value_defaults_to_index(qtbot):
    s = MdSegmentedButtonSet()
    qtbot.addWidget(s)
    a, b = MdSegmentedButton("A"), MdSegmentedButton("B")
    s.add_segment(a)
    s.add_segment(b)
    assert [seg.value() for seg in s.segments()] == [0, 1]


def test_empty_disallowed_keeps_last_selected(qtbot):
    s = MdSegmentedButtonSet()  # single-select, empty disallowed (default)
    qtbot.addWidget(s)
    a, b = MdSegmentedButton("A"), MdSegmentedButton("B")
    s.add_segment(a)
    s.add_segment(b)
    a.setChecked(True)
    # Clicking the only selected segment must not clear it.
    a.click()
    assert a.isChecked()
    assert s.selected_indices() == [0]


def test_empty_allowed_can_clear(qtbot):
    s = MdSegmentedButtonSet(empty_selection_allowed=True)
    qtbot.addWidget(s)
    a, b = MdSegmentedButton("A"), MdSegmentedButton("B")
    s.add_segment(a)
    s.add_segment(b)
    a.click()
    assert s.selected_indices() == [0]
    a.click()
    assert s.selected_indices() == []


def test_single_select_empty_allowed_is_exclusive(qtbot):
    s = MdSegmentedButtonSet(empty_selection_allowed=True)  # single by default
    qtbot.addWidget(s)
    a, b = MdSegmentedButton("A"), MdSegmentedButton("B")
    s.add_segment(a)
    s.add_segment(b)
    a.click()
    b.click()
    assert s.selected_indices() == [1]


def test_multi_empty_disallowed_keeps_one(qtbot):
    s = MdSegmentedButtonSet(multi=True)  # empty disallowed by default
    qtbot.addWidget(s)
    a, b = MdSegmentedButton("A"), MdSegmentedButton("B")
    s.add_segment(a)
    s.add_segment(b)
    a.click()
    b.click()
    assert s.selected_indices() == [0, 1]
    a.click()
    assert s.selected_indices() == [1]
    b.click()  # would empty the set — must be refused
    assert s.selected_indices() == [1]


def test_show_selected_icon_toggle(qtbot):
    s = MdSegmentedButtonSet(show_selected_icon=False)
    qtbot.addWidget(s)
    a = MdSegmentedButton("A")
    s.add_segment(a)
    a.setChecked(True)
    assert not a._show_selected_icon
    s.set_show_selected_icon(True)
    assert a._show_selected_icon


def test_custom_selected_icon(qtbot):
    s = MdSegmentedButtonSet(selected_icon="done_all")
    qtbot.addWidget(s)
    a = MdSegmentedButton("A")
    s.add_segment(a)
    assert a._selected_icon == "done_all"


def test_set_selected_indices(qtbot):
    s = MdSegmentedButtonSet(multi=True)
    qtbot.addWidget(s)
    for t in ("A", "B", "C"):
        s.add_segment(MdSegmentedButton(t))
    s.set_selected_indices([0, 2])
    assert s.selected_indices() == [0, 2]


def test_tooltip_and_enabled_segment(qtbot):
    s = MdSegmentedButtonSet()
    qtbot.addWidget(s)
    seg = MdSegmentedButton("A", tooltip="hi", enabled=False)
    s.add_segment(seg)
    assert seg.toolTip() == "hi"
    assert not seg.isEnabled()


def test_grouped_switch_emits_once(qtbot):
    # Default single-select uses an exclusive QButtonGroup; switching selection
    # must report exactly one change, not two (old off + new on).
    s = MdSegmentedButtonSet()
    qtbot.addWidget(s)
    a, b = MdSegmentedButton("A"), MdSegmentedButton("B")
    s.add_segment(a)
    s.add_segment(b)
    a.click()  # select A
    seen = []
    s.changed.connect(seen.append)
    b.click()  # switch to B
    assert seen == [[1]]


def test_set_selected_indices_does_not_emit(qtbot):
    s = MdSegmentedButtonSet()  # grouped single-select
    qtbot.addWidget(s)
    a, b = MdSegmentedButton("A"), MdSegmentedButton("B")
    s.add_segment(a)
    s.add_segment(b)
    a.setChecked(True)
    seen = []
    s.changed.connect(seen.append)
    s.set_selected_indices([1])
    assert seen == []
    assert s.selected_indices() == [1]


def test_explicit_none_value_preserved(qtbot):
    s = MdSegmentedButtonSet()
    qtbot.addWidget(s)
    seg = MdSegmentedButton("All", value=None)
    other = MdSegmentedButton("One")
    s.add_segment(seg)
    s.add_segment(other)
    assert seg.value() is None  # not overwritten with the index
    assert other.value() == 1   # unset -> index fallback


def test_checked_segment_widens_and_announces_geometry_change(qtbot):
    """Regression: checking a segment adds the leading checkmark (+26px in the
    size hint) but only update() was called — without updateGeometry() a snug
    layout kept the stale hint and clipped the check + label."""
    s = MdSegmentedButtonSet()
    qtbot.addWidget(s)
    a, b = MdSegmentedButton("Day"), MdSegmentedButton("Week")
    s.add_segment(a)
    s.add_segment(b)
    seg_before = a.sizeHint().width()
    set_before = s.sizeHint().width()  # caches the layout's size hint
    a.setChecked(True)
    assert a.sizeHint().width() > seg_before
    # updateGeometry() must invalidate the parent layout so the set's own
    # size hint reflects the wider segment.
    assert s.sizeHint().width() > set_before


def test_renders(qtbot):
    s = MdSegmentedButtonSet()
    qtbot.addWidget(s)
    for i, t in enumerate(("Day", "Week", "Month")):
        seg = MdSegmentedButton(t)
        if i == 0:
            seg.setChecked(True)
        s.add_segment(seg)
    s.resize(s.sizeHint())
    s.grab()
