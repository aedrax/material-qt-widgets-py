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


def test_renders(qtbot):
    host = _host(qtbot)
    sb = MdSnackbar(host, "Message text", action_label="Action")
    sb.open()
    sb.grab()
