"""Tests for MdExpansionPanel."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from material_qt.core import motion
from material_qt.tokens.color import ColorRole
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


def test_subtitle_leading_trailing(qtbot):
    leading = QLabel("L")
    trailing = QLabel("T")
    p = MdExpansionPanel(
        "Section", subtitle="Subtitle here", leading=leading, trailing=trailing,
    )
    qtbot.addWidget(p)
    assert p._header._subtitle.text() == "Subtitle here"
    assert not p._header._subtitle.isHidden()
    assert p._header._leading is leading
    assert p._header._trailing is trailing


def test_no_subtitle_is_hidden(qtbot):
    p = MdExpansionPanel("Section")
    qtbot.addWidget(p)
    assert p._header._subtitle.isHidden()


def test_set_title_and_subtitle(qtbot):
    p = MdExpansionPanel("Old")
    qtbot.addWidget(p)
    p.set_title("New")
    p.set_subtitle("Now visible")
    assert p._header._title.text() == "New"
    assert p._header._subtitle.text() == "Now visible"
    assert not p._header._subtitle.isHidden()


def test_background_role(qtbot):
    p = MdExpansionPanel("Section", background_role=ColorRole.SURFACE_CONTAINER)
    qtbot.addWidget(p)
    assert p.background_role is ColorRole.SURFACE_CONTAINER
    assert p._header._surface_role is ColorRole.SURFACE_CONTAINER
    p.set_background_role(ColorRole.SURFACE_CONTAINER_HIGH)
    assert p._header._surface_role is ColorRole.SURFACE_CONTAINER_HIGH


def test_initially_expanded(qtbot):
    host = QWidget()
    host.resize(400, 300)
    lay = QVBoxLayout(host)
    p = MdExpansionPanel("Section", initially_expanded=True)
    p.add_content(QLabel("content"))
    lay.addWidget(p)
    qtbot.addWidget(host)
    assert p.expanded


def test_renders_expanded(qtbot):
    prev = motion.MOTION_ENABLED
    motion.MOTION_ENABLED = False
    try:
        host, p = _panel(qtbot)
        p.set_expanded(True)
        p.grab()
    finally:
        motion.MOTION_ENABLED = prev
