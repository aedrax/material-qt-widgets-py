"""Tests for MdLoadingIndicator."""

from __future__ import annotations

from material_qt.widgets.loadingindicator import MdLoadingIndicator


def test_never_shown_does_not_animate(qtbot):
    # Regression: the loop-forever animation must not start in the constructor;
    # a never-shown indicator would tick + repaint at frame rate forever.
    li = MdLoadingIndicator()
    qtbot.addWidget(li)
    assert not li.is_running


def test_show_starts_hide_stops(qtbot):
    li = MdLoadingIndicator()
    qtbot.addWidget(li)
    li.show()
    # A one-shot animation would render once and freeze; it must loop.
    assert li._anim.loopCount() == -1
    assert li.is_running
    li.hide()
    assert not li.is_running
    # Re-showing resumes automatically (hide pauses, it does not cancel).
    li.show()
    assert li.is_running


def test_stop_and_start(qtbot):
    li = MdLoadingIndicator()
    qtbot.addWidget(li)
    li.show()
    li.stop()
    assert not li.is_running
    li.start()
    assert li.is_running


def test_stopped_indicator_stays_stopped_across_show(qtbot):
    li = MdLoadingIndicator()
    qtbot.addWidget(li)
    li.show()
    li.stop()
    li.hide()
    li.show()
    assert not li.is_running  # an explicit stop() survives hide/show
    li.start()
    assert li.is_running


def test_start_while_hidden_defers_until_shown(qtbot):
    li = MdLoadingIndicator()
    qtbot.addWidget(li)
    li.start()
    assert not li.is_running  # parked until visible
    li.show()
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
