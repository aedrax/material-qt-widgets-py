"""Tests for MdBottomSheet."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget

from material_qt.widgets.bottomsheet import MdBottomSheet, MdStandardBottomSheet
from material_qt.widgets.bottomsheet import bottomsheet as mod


def _host(qtbot) -> QWidget:
    host = QWidget()
    host.resize(600, 800)
    qtbot.addWidget(host)
    return host


def test_open_shows_panel_at_bottom(qtbot):
    prev = mod.MOTION_ENABLED
    mod.MOTION_ENABLED = False
    try:
        host = _host(qtbot)
        sheet = MdBottomSheet(host)
        sheet.add_content(QLabel("Sheet content"))
        sheet.open()
        assert not sheet.isHidden()
        # Panel rests against the bottom edge of the host.
        assert sheet._panel.geometry().bottom() <= host.height() + 1
        assert sheet._panel.geometry().bottom() >= host.height() - 1
    finally:
        mod.MOTION_ENABLED = prev


def test_dismiss_closes_no_motion(qtbot):
    prev = mod.MOTION_ENABLED
    mod.MOTION_ENABLED = False
    try:
        host = _host(qtbot)
        sheet = MdBottomSheet(host)
        seen = []
        sheet.closed.connect(lambda: seen.append(True))
        sheet.open()
        sheet.dismiss()
        assert seen == [True] and sheet.isHidden()
    finally:
        mod.MOTION_ENABLED = prev


def test_animated_dismiss_hides_and_emits(qtbot):
    # Motion ON: the animated slide-out must reach hidden and emit closed.
    host = _host(qtbot)
    sheet = MdBottomSheet(host)
    sheet.add_content(QLabel("Content"))
    seen = []
    sheet.closed.connect(lambda: seen.append(True))
    sheet.open()
    qtbot.waitUntil(lambda: sheet._shown >= 0.99, timeout=2000)  # let it slide in
    sheet.dismiss()
    qtbot.waitUntil(lambda: sheet.isHidden(), timeout=2000)  # and back out
    assert seen == [True]


def test_renders(qtbot):
    prev = mod.MOTION_ENABLED
    mod.MOTION_ENABLED = False
    try:
        host = _host(qtbot)
        sheet = MdBottomSheet(host)
        sheet.add_content(QLabel("Sheet content"))
        sheet.open()
        sheet.grab()
    finally:
        mod.MOTION_ENABLED = prev


# -- standard (persistent) bottom sheet -----------------------------------

def test_standard_toggle_height(qtbot):
    s = MdStandardBottomSheet()
    qtbot.addWidget(s)
    big = QLabel("x")
    big.setFixedHeight(200)
    s.add_content(big)
    assert not s.expanded and s.height() == s._PEEK  # starts collapsed (peek)
    seen = []
    s.toggled.connect(seen.append)
    s.set_expanded(True, animated=False)
    assert s.expanded and s.height() > s._PEEK and seen[-1] is True
    s.set_expanded(False, animated=False)
    assert not s.expanded and s.height() == s._PEEK and seen[-1] is False


def test_standard_renders(qtbot):
    s = MdStandardBottomSheet(expanded=True)
    qtbot.addWidget(s)
    s.add_content(QLabel("Persistent bottom sheet content."))
    s.resize(400, s.height())
    s.grab()
