"""Tests for MdLinearProgress / MdCircularProgress."""

from __future__ import annotations

from material_qt.widgets.progress import MdCircularProgress, MdLinearProgress


def test_value_clamped(qtbot):
    p = MdLinearProgress(value=2.0)
    qtbot.addWidget(p)
    assert p.value == 1.0
    p.set_value(-1)
    assert p.value == 0.0


def test_mode_switch_starts_stops_anim(qtbot):
    p = MdLinearProgress()
    qtbot.addWidget(p)
    p.show()
    p.set_indeterminate(True)
    assert p._anim is not None
    p.set_indeterminate(False)
    assert p._anim is None


def test_hide_stops_animation(qtbot):
    p = MdCircularProgress(indeterminate=True)
    qtbot.addWidget(p)
    p.show()
    assert p._anim is not None
    p.hide()
    assert p._anim is None


def test_renders(qtbot):
    for p in (
        MdLinearProgress(value=0.6),
        MdLinearProgress(indeterminate=True),
        MdCircularProgress(value=0.4),
        MdCircularProgress(indeterminate=True),
    ):
        qtbot.addWidget(p)
        p.resize(p.sizeHint())
        p.grab()
