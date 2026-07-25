"""Tests for ModalOverlay's fade lifecycle, via a minimal concrete subclass."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QAbstractAnimation
from PySide6.QtWidgets import QWidget

from material_qt.core import modal_overlay as mod
from material_qt.core.modal_overlay import ModalOverlay


class _Overlay(ModalOverlay):
    """Smallest possible subclass honouring the ModalOverlay contract."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self._panel = QWidget(self)
        self._panel.resize(200, 100)
        self._init_overlay(parent)


@pytest.fixture()
def no_motion():
    """Disable animation so open/close settle synchronously.

    ``MOTION_ENABLED`` is imported by-name into the modal_overlay module, so
    the binding must be patched there.
    """
    prev = mod.MOTION_ENABLED
    mod.MOTION_ENABLED = False
    try:
        yield
    finally:
        mod.MOTION_ENABLED = prev


def _host(qtbot) -> QWidget:
    host = QWidget()
    host.resize(600, 400)
    qtbot.addWidget(host)
    return host


def test_close_stops_fade_animation(qtbot):
    # Regression: _close() during fade-in left the tween running, ticking
    # _set_fade (adjustSize + update per frame) on a hidden overlay until the
    # tween ran out.
    host = _host(qtbot)
    ov = _Overlay(host)
    ov.open()
    assert ov._anim.state() == QAbstractAnimation.State.Running
    ov._close()
    assert ov._anim.state() == QAbstractAnimation.State.Stopped
    assert ov.isHidden()


def test_reopen_mid_fade_resumes_from_current_value(qtbot):
    # Regression: open() always restarted the scrim fade from 0.0, so
    # re-opening mid-fade blinked the scrim back to transparent.
    host = _host(qtbot)
    ov = _Overlay(host)
    ov.open()
    qtbot.waitUntil(lambda: ov._fade > 0.2, timeout=2000)
    ov.open()
    assert float(ov._anim.startValue()) >= 0.2
    assert ov._fade >= 0.2


def test_close_resets_fade_so_next_open_fades_in(qtbot):
    host = _host(qtbot)
    ov = _Overlay(host)
    ov.open()
    qtbot.waitUntil(
        lambda: ov._anim.state() == QAbstractAnimation.State.Stopped, timeout=2000
    )
    assert ov._fade == 1.0
    ov._close()
    assert ov._fade == 0.0


def test_open_close_without_motion(qtbot, no_motion):
    host = _host(qtbot)
    ov = _Overlay(host)
    ov.open()
    assert ov._fade == 1.0 and not ov.isHidden()
    ov._close()
    assert ov.isHidden() and ov._fade == 0.0
