"""Tests for MdLinearProgress / MdCircularProgress."""

from __future__ import annotations

from material_qt.tokens.color import ColorRole
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


def test_color_and_track_roles(qtbot):
    p = MdLinearProgress(color_role=ColorRole.SECONDARY,
                         track_role=ColorRole.SURFACE_CONTAINER)
    qtbot.addWidget(p)
    assert p.color_role == ColorRole.SECONDARY
    assert p.track_role == ColorRole.SURFACE_CONTAINER
    p.set_color_role(ColorRole.TERTIARY)
    assert p.color_role == ColorRole.TERTIARY


def test_linear_min_height_affects_size(qtbot):
    p = MdLinearProgress(min_height=10)
    qtbot.addWidget(p)
    assert p.min_height == 10
    assert p.sizeHint().height() == 10
    assert p.minimumSizeHint().height() == 10


def test_linear_border_radius_default_and_override(qtbot):
    p = MdLinearProgress(min_height=8)
    qtbot.addWidget(p)
    assert p.border_radius == 4  # half of thickness
    p.set_border_radius(2)
    assert p.border_radius == 2


def test_circular_stroke_width(qtbot):
    p = MdCircularProgress(stroke_width=8)
    qtbot.addWidget(p)
    assert p.stroke_width == 8
    p.set_stroke_width(2)
    assert p.stroke_width == 2


def test_renders(qtbot):
    for p in (
        MdLinearProgress(value=0.6),
        MdLinearProgress(indeterminate=True),
        MdLinearProgress(value=0.6, min_height=12, border_radius=0),
        MdCircularProgress(value=0.4),
        MdCircularProgress(indeterminate=True),
        MdCircularProgress(value=0.4, stroke_width=8),
    ):
        qtbot.addWidget(p)
        p.resize(p.sizeHint())
        p.grab()
