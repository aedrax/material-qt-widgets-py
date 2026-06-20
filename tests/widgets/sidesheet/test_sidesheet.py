"""Tests for MdSideSheet."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget

from material_qt.widgets.sidesheet import MdSideSheet
from material_qt.widgets.sidesheet import sidesheet as mod


def _host(qtbot) -> QWidget:
    host = QWidget()
    host.resize(800, 600)
    qtbot.addWidget(host)
    return host


def test_open_anchors_to_right_edge(qtbot):
    prev = mod.MOTION_ENABLED
    mod.MOTION_ENABLED = False
    try:
        host = _host(qtbot)
        sheet = MdSideSheet(host, title="Details")
        sheet.add_content(QLabel("Body"))
        sheet.open()
        assert not sheet.isHidden()
        g = sheet._panel.geometry()
        assert g.right() == host.width() - 1  # flush with the right edge
        assert g.height() == host.height()    # full height
    finally:
        mod.MOTION_ENABLED = prev


def test_left_side_anchors_to_left_edge(qtbot):
    prev = mod.MOTION_ENABLED
    mod.MOTION_ENABLED = False
    try:
        host = _host(qtbot)
        sheet = MdSideSheet(host, title="Filters", side="left")
        sheet.open()
        assert sheet._panel.geometry().left() == 0
    finally:
        mod.MOTION_ENABLED = prev


def test_action_shows_divider_and_returns_button(qtbot):
    host = _host(qtbot)
    sheet = MdSideSheet(host, title="Details")
    assert sheet._divider.isHidden()
    btn = sheet.add_action("Save")
    assert not sheet._divider.isHidden()
    fired = []
    btn.clicked.connect(lambda: fired.append(True))
    btn.click()
    assert fired == [True]


def test_dismiss_closes_no_motion(qtbot):
    prev = mod.MOTION_ENABLED
    mod.MOTION_ENABLED = False
    try:
        host = _host(qtbot)
        sheet = MdSideSheet(host, title="Details")
        seen = []
        sheet.closed.connect(lambda: seen.append(True))
        sheet.open()
        sheet.dismiss()
        assert seen == [True] and sheet.isHidden()
    finally:
        mod.MOTION_ENABLED = prev


def test_animated_dismiss_hides_and_emits(qtbot):
    host = _host(qtbot)
    sheet = MdSideSheet(host, title="Details")
    seen = []
    sheet.closed.connect(lambda: seen.append(True))
    sheet.open()
    qtbot.waitUntil(lambda: sheet._shown >= 0.99, timeout=2000)
    sheet.dismiss()
    qtbot.waitUntil(lambda: sheet.isHidden(), timeout=2000)
    assert seen == [True]


def test_renders(qtbot):
    prev = mod.MOTION_ENABLED
    mod.MOTION_ENABLED = False
    try:
        host = _host(qtbot)
        sheet = MdSideSheet(host, title="Details")
        sheet.add_content(QLabel("Some side sheet content."))
        sheet.add_action("Save")
        sheet.open()
        sheet.grab()
    finally:
        mod.MOTION_ENABLED = prev
