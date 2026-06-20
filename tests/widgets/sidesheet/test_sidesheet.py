"""Tests for MdSideSheet."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget

from material_qt.widgets.sidesheet import MdSideSheet, MdStandardSideSheet
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


# -- standard (persistent) side sheet -------------------------------------

def test_standard_toggle_width(qtbot):
    s = MdStandardSideSheet(title="Filters", expanded=True)
    qtbot.addWidget(s)
    assert s.expanded and s.width() == 320
    seen = []
    s.toggled.connect(seen.append)
    s.set_expanded(False, animated=False)
    assert not s.expanded and s.width() == 0 and seen[-1] is False
    s.set_expanded(True, animated=False)
    assert s.expanded and s.width() == 320 and seen[-1] is True


def test_standard_starts_collapsed(qtbot):
    s = MdStandardSideSheet(title="Filters", expanded=False)
    qtbot.addWidget(s)
    assert not s.expanded and s.width() == 0


def test_standard_close_button_collapses(qtbot):
    s = MdStandardSideSheet(title="Filters", expanded=True)
    qtbot.addWidget(s)
    s.collapse()  # what the close button calls
    assert not s.expanded


def test_standard_renders(qtbot):
    s = MdStandardSideSheet(title="Filters", expanded=True)
    qtbot.addWidget(s)
    s.add_content(QLabel("Body"))
    s.add_action("Apply")
    s.resize(320, 400)
    s.grab()
