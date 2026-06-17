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
