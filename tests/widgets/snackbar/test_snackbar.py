"""Tests for MdSnackbar."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QWidget

from material_qt.widgets.snackbar import MdSnackbar
from material_qt.widgets.snackbar import snackbar as snackbar_mod


@pytest.fixture()
def no_motion():
    """Disable animation so open/dismiss settle synchronously.

    ``MOTION_ENABLED`` is imported by-name into the snackbar module, so the
    binding must be patched there (patching ``core.motion`` would not be seen).
    """
    prev = snackbar_mod.MOTION_ENABLED
    snackbar_mod.MOTION_ENABLED = False
    try:
        yield
    finally:
        snackbar_mod.MOTION_ENABLED = prev


def _host(qtbot) -> QWidget:
    host = QWidget()
    host.resize(800, 600)
    qtbot.addWidget(host)
    return host


def test_open_shows_and_positions_at_bottom(qtbot, no_motion):
    host = _host(qtbot)
    sb = MdSnackbar(host, "Saved")
    sb.open()
    # isVisible() depends on the (unshown) host; isHidden() tracks the widget's
    # own shown state.
    assert not sb.isHidden()
    # Resting position: above the bottom margin, within the host.
    assert sb.geometry().bottom() <= host.height()
    assert sb.geometry().top() > 0


def test_action_emits_and_dismisses(qtbot, no_motion):
    host = _host(qtbot)
    sb = MdSnackbar(host, "Deleted", action_label="Undo")
    fired = []
    sb.action.connect(lambda: fired.append(True))
    sb.open()
    sb._on_action(None)
    assert fired == [True]
    assert not sb.isVisible()


def test_dismiss_emits_dismissed_once(qtbot, no_motion):
    host = _host(qtbot)
    sb = MdSnackbar(host, "Hi")
    seen = []
    sb.dismissed.connect(lambda: seen.append(True))
    sb.open()
    sb.dismiss()
    sb.dismiss()  # second dismiss is a no-op (already hidden)
    assert seen == [True] and not sb.isVisible()


def test_animated_dismiss_hides_and_emits(qtbot):
    # Motion ON: exercises the auto-dismiss timer + the animated _set_shown
    # guard (the primary real-world path, not covered by the no_motion tests).
    host = _host(qtbot)
    sb = MdSnackbar(host, "Saved", duration=50)
    seen = []
    sb.dismissed.connect(lambda: seen.append(True))
    sb.open()
    qtbot.waitUntil(lambda: sb.isHidden(), timeout=2000)
    assert seen == [True]


def test_fixed_behavior_spans_full_width(qtbot, no_motion):
    host = _host(qtbot)
    sb = MdSnackbar(host, "Saved", behavior="fixed")
    sb.open()
    assert sb.behavior == "fixed"
    # Fixed snackbars are flush full-width with no horizontal margin.
    assert sb.geometry().left() == 0
    assert sb.geometry().width() == host.width()
    assert sb.geometry().bottom() >= host.height() - 1


def test_floating_behavior_is_inset(qtbot, no_motion):
    host = _host(qtbot)
    sb = MdSnackbar(host, "Saved")  # default floating
    sb.open()
    assert sb.behavior == "floating"
    assert sb.geometry().left() > 0
    assert sb.geometry().width() < host.width()


def test_close_icon_dismisses_without_action(qtbot, no_motion):
    host = _host(qtbot)
    sb = MdSnackbar(host, "Saved", show_close_icon=True)
    actions, dismissed = [], []
    sb.action.connect(lambda: actions.append(True))
    sb.dismissed.connect(lambda: dismissed.append(True))
    sb.open()
    assert sb._close_icon is not None
    sb._on_close_icon(None)
    assert actions == [] and dismissed == [True] and sb.isHidden()


def test_close_icon_receives_real_click(qtbot, no_motion):
    # The icon must actually receive press events (icons can be mouse-transparent).
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    host = _host(qtbot)
    sb = MdSnackbar(host, "Saved", show_close_icon=True)
    dismissed = []
    sb.dismissed.connect(lambda: dismissed.append(True))
    sb.open()
    QTest.mouseClick(sb._close_icon, Qt.MouseButton.LeftButton)
    assert dismissed == [True] and sb.isHidden()


def test_immediate_dismiss_with_motion_on_hides_and_emits(qtbot):
    # Regression: dismiss() in the same event-loop turn as open() (shown still
    # ~0) used to start a 0->0 tween that emits no valueChanged, leaving the
    # snackbar stuck visible forever and `dismissed` never fired.
    host = _host(qtbot)
    sb = MdSnackbar(host, "Saved")
    seen = []
    sb.dismissed.connect(lambda: seen.append(True))
    sb.open()
    sb.dismiss()
    assert seen == [True]
    assert sb.isHidden()


def test_open_replaces_snackbar_on_same_host(qtbot):
    # Motion ON: the replacement must be deterministic even mid-animation —
    # the older snackbar is hidden immediately (no exit tween) and emits
    # `dismissed` before the new one shows.
    host = _host(qtbot)
    a = MdSnackbar(host, "First")
    b = MdSnackbar(host, "Second")
    a_seen, b_seen = [], []
    a.dismissed.connect(lambda: a_seen.append(True))
    b.dismissed.connect(lambda: b_seen.append(True))
    a.open()
    b.open()
    assert a_seen == [True] and a.isHidden()
    assert b_seen == [] and not b.isHidden()


def test_replaced_snackbar_timer_does_not_dismiss_replacement(qtbot, no_motion):
    # The older snackbar's auto-dismiss timer must be stopped on replacement,
    # so it cannot dismiss "through" the newer snackbar.
    host = _host(qtbot)
    a = MdSnackbar(host, "First", duration=1)
    b = MdSnackbar(host, "Second", duration=0)
    a.open()
    b.open()
    assert not a._dismiss_timer.isActive()
    qtbot.wait(50)
    assert not b.isHidden()


def test_reopen_same_snackbar_is_not_self_dismissed(qtbot, no_motion):
    host = _host(qtbot)
    sb = MdSnackbar(host, "Hi")
    seen = []
    sb.dismissed.connect(lambda: seen.append(True))
    sb.open()
    sb.open()
    assert seen == [] and not sb.isHidden()


def test_snackbars_on_different_hosts_coexist(qtbot, no_motion):
    host_a = _host(qtbot)
    host_b = _host(qtbot)
    a = MdSnackbar(host_a, "A")
    b = MdSnackbar(host_b, "B")
    a.open()
    b.open()
    assert not a.isHidden() and not b.isHidden()


def test_open_survives_deleted_predecessor(qtbot, no_motion):
    # A registry entry whose C++ object was deleted (dismissed -> deleteLater,
    # the documented one-shot pattern) must be skipped, not crash open().
    host = _host(qtbot)
    a = MdSnackbar(host, "First")
    a.dismissed.connect(a.deleteLater)
    a.open()
    a.dismiss()
    qtbot.wait(10)  # let deferred deletion run
    b = MdSnackbar(host, "Second")
    b.open()
    assert not b.isHidden()


def test_renders(qtbot):
    host = _host(qtbot)
    sb = MdSnackbar(host, "Message text", action_label="Action", show_close_icon=True)
    sb.open()
    sb.grab()
