"""Tests for MdExpansionPanel."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from material_qt.core import motion
from material_qt.widgets.expansionpanel import MdExpansionPanel


def _panel(qtbot):
    """Return (host, panel); keep ``host`` referenced so it is not GC'd. The
    panel is laid out in the host so it has a real width when content is
    measured at expand time."""
    host = QWidget()
    host.resize(400, 300)
    lay = QVBoxLayout(host)
    p = MdExpansionPanel("Section", expanded=False)
    p.add_content(QLabel("Some expandable content goes here."))
    lay.addWidget(p)
    lay.addStretch(1)
    qtbot.addWidget(host)
    return host, p


def test_starts_collapsed(qtbot):
    host, p = _panel(qtbot)
    assert not p.expanded
    assert p._content.maximumHeight() == 0


def test_toggle_expands_and_emits(qtbot):
    prev = motion.MOTION_ENABLED
    motion.MOTION_ENABLED = False
    try:
        host, p = _panel(qtbot)
        seen = []
        p.toggled.connect(seen.append)
        content_h = p._content.sizeHint().height()
        assert content_h > 0
        p.toggle()
        assert p.expanded and seen == [True]
        # Expanded: content is no longer clamped to 0 (can show its full height).
        assert p._content.maximumHeight() >= content_h
        p.toggle()
        assert not p.expanded and seen == [True, False]
        assert p._content.maximumHeight() == 0
    finally:
        motion.MOTION_ENABLED = prev


def test_idempotent_set(qtbot):
    host, p = _panel(qtbot)
    seen = []
    p.toggled.connect(seen.append)
    p.set_expanded(False)  # already collapsed -> no-op, no signal
    assert seen == []


def test_renders_expanded(qtbot):
    prev = motion.MOTION_ENABLED
    motion.MOTION_ENABLED = False
    try:
        host, p = _panel(qtbot)
        p.set_expanded(True)
        p.grab()
    finally:
        motion.MOTION_ENABLED = prev
