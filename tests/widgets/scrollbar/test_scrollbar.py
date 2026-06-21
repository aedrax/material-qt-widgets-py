"""Tests for MdScrollBar."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from material_qt.widgets.scrollbar import scrollbar as mod
from material_qt.widgets.scrollbar import (
    MdScrollBar,
    install_material_scrollbars,
    thumb_metrics,
    use_material_scrollbars,
)


# -- pure geometry (windowless seam) --------------------------------------

def test_thumb_fills_groove_when_nothing_to_scroll():
    # maximum <= minimum -> no travel, thumb spans the whole groove.
    assert thumb_metrics(0, 0, 10, 0, 200) == (0.0, 200.0)


def test_thumb_position_tracks_value():
    pos0, length = thumb_metrics(0, 100, 50, 0, 200)
    posmid, _ = thumb_metrics(0, 100, 50, 50, 200)
    posend, _ = thumb_metrics(0, 100, 50, 100, 200)
    # content = range(100) + page(50) = 150; thumb = 200 * 50/150.
    assert length == 200 * 50 / 150
    travel = 200 - length
    assert pos0 == 0.0
    assert posmid == travel * 0.5
    assert posend == travel  # flush to the bottom at the maximum


def test_thumb_length_floored_at_min():
    # A tiny page within a huge range would give a sub-pixel thumb; it's floored.
    _, length = thumb_metrics(0, 1000, 10, 500, 200, min_thumb_len=48)
    assert length == 48.0


def test_thumb_value_out_of_range_is_clamped():
    travel = 200 - thumb_metrics(0, 100, 50, 0, 200)[1]
    assert thumb_metrics(0, 100, 50, -20, 200)[0] == 0.0
    assert thumb_metrics(0, 100, 50, 999, 200)[0] == travel


# -- widget ---------------------------------------------------------------

def test_fixed_gutter_per_orientation(qtbot):
    v = MdScrollBar(Qt.Orientation.Vertical)
    h = MdScrollBar(Qt.Orientation.Horizontal)
    qtbot.addWidget(v)
    qtbot.addWidget(h)
    assert v.width() == mod.GUTTER
    assert h.height() == mod.GUTTER


def test_thumb_rect_within_gutter(qtbot):
    bar = MdScrollBar(Qt.Orientation.Vertical)
    qtbot.addWidget(bar)
    bar.setRange(0, 100)
    bar.setPageStep(20)
    bar.setValue(30)
    bar.resize(mod.GUTTER, 300)
    rect = bar._thumb_rect()
    # 8px-wide thumb hugging the right edge, inset by the 2px margin.
    assert rect.width() == mod.THICKNESS
    assert rect.x() == mod.GUTTER - mod.MARGIN - mod.THICKNESS
    assert 0 <= rect.y() <= 300 - rect.height()


def test_hover_thickens_thumb(qtbot):
    mod.MOTION_ENABLED = False  # animate instantly for a deterministic assert
    try:
        bar = MdScrollBar(Qt.Orientation.Vertical)
        qtbot.addWidget(bar)
        assert bar._thickness() == mod.THICKNESS
        bar._animate_hover(1.0)
        assert bar._thickness() == mod.THICKNESS_HOVER
    finally:
        mod.MOTION_ENABLED = True


def test_dragging_uses_drag_thumb_color(qtbot):
    bar = MdScrollBar(Qt.Orientation.Vertical)
    qtbot.addWidget(bar)
    idle = bar._thumb_color().alphaF()
    bar._dragging = True
    drag = bar._thumb_color().alphaF()
    assert drag > idle  # dragged thumb is more opaque


def test_renders(qtbot):
    bar = MdScrollBar(Qt.Orientation.Vertical)
    qtbot.addWidget(bar)
    bar.setRange(0, 100)
    bar.setPageStep(20)
    bar.resize(mod.GUTTER, 300)
    bar.grab()


# -- installers -----------------------------------------------------------

def _scroll_area(qtbot) -> QScrollArea:
    content = QWidget()
    cl = QVBoxLayout(content)
    for i in range(30):
        cl.addWidget(QLabel(f"row {i}"))
    sa = QScrollArea()
    sa.setWidgetResizable(True)
    sa.setWidget(content)
    qtbot.addWidget(sa)
    return sa


def test_use_material_scrollbars_replaces_both_axes(qtbot):
    sa = _scroll_area(qtbot)
    use_material_scrollbars(sa)
    assert isinstance(sa.verticalScrollBar(), MdScrollBar)
    assert isinstance(sa.horizontalScrollBar(), MdScrollBar)


def test_install_walks_tree_and_is_idempotent(qtbot):
    root = QWidget()
    outer = QVBoxLayout(root)
    sa = _scroll_area(qtbot)
    outer.addWidget(sa)
    qtbot.addWidget(root)

    install_material_scrollbars(root)
    bar = sa.verticalScrollBar()
    assert isinstance(bar, MdScrollBar)

    # Second sweep leaves the already-converted bar in place (no churn).
    install_material_scrollbars(root)
    assert sa.verticalScrollBar() is bar
