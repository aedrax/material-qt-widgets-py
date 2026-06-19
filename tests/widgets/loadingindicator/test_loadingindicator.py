"""Tests for MdLoadingIndicator."""

from __future__ import annotations

from material_qt.widgets.loadingindicator import MdLoadingIndicator


def test_runs_and_loops_forever(qtbot):
    li = MdLoadingIndicator()
    qtbot.addWidget(li)
    # A one-shot animation would render once and freeze; it must loop.
    assert li._anim.loopCount() == -1
    assert li.is_running


def test_stop_and_start(qtbot):
    li = MdLoadingIndicator()
    qtbot.addWidget(li)
    li.stop()
    assert not li.is_running
    li.start()
    assert li.is_running


def test_t_is_drivable_and_wraps(qtbot):
    li = MdLoadingIndicator()
    qtbot.addWidget(li)
    li.stop()
    li.set_t(0.25)
    assert li.get_t() == 0.25
    li.set_t(1.5)  # wraps into [0, 1)
    assert li.get_t() == 0.5


def test_renders(qtbot):
    li = MdLoadingIndicator()
    qtbot.addWidget(li)
    li.set_t(0.3)
    li.grab()
