"""Tests for MdTooltip."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPointF
from PySide6.QtGui import QEnterEvent
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from material_qt.widgets.tooltip import MdTooltip


def _hover_enter(btn) -> None:
    """Deliver an Enter event through the event system so installed event
    filters run (``btn.event(...)`` would bypass them)."""
    pos = QPointF(5, 5)
    QApplication.sendEvent(btn, QEnterEvent(pos, pos, btn.mapToGlobal(pos.toPoint())))


def _target(qtbot):
    """Return (host, button); the caller must keep ``host`` referenced so it is
    not garbage-collected mid-test."""
    host = QWidget()
    host.resize(400, 300)
    btn = QPushButton("Hover me", host)
    btn.move(150, 120)
    qtbot.addWidget(host)
    return host, btn


def test_attach_returns_tooltip(qtbot):
    host, btn = _target(qtbot)
    tip = MdTooltip.attach(btn, "Help text")
    assert isinstance(tip, MdTooltip)
    assert tip.isHidden()


def test_wait_then_show_on_enter(qtbot):
    host, btn = _target(qtbot)
    tip = MdTooltip(btn, "Help text", wait_ms=0, show_ms=0)
    _hover_enter(btn)
    qtbot.waitUntil(lambda: not tip.isHidden(), timeout=500)
    assert not tip.isHidden()


def test_leave_hides(qtbot):
    host, btn = _target(qtbot)
    tip = MdTooltip(btn, "Help text", wait_ms=0, show_ms=0)
    _hover_enter(btn)
    qtbot.waitUntil(lambda: not tip.isHidden(), timeout=500)
    QApplication.sendEvent(btn, QEvent(QEvent.Type.Leave))
    assert tip.isHidden()


def test_auto_hides_after_show_ms(qtbot):
    host, btn = _target(qtbot)
    tip = MdTooltip(btn, "Help text", wait_ms=0, show_ms=30)
    _hover_enter(btn)
    qtbot.waitUntil(lambda: not tip.isHidden(), timeout=500)
    qtbot.waitUntil(lambda: tip.isHidden(), timeout=1000)
    assert tip.isHidden()


def test_prefer_below_property(qtbot):
    host, btn = _target(qtbot)
    tip = MdTooltip(btn, "Help text", prefer_below=True, margin=8)
    assert tip.prefer_below is True
    assert tip.margin == 8
    tip.set_prefer_below(False)
    assert tip.prefer_below is False


def test_prefer_below_positions_under_target(qtbot):
    host, btn = _target(qtbot)
    host.show()
    qtbot.waitExposed(host)
    below = MdTooltip(btn, "Help text", wait_ms=0, prefer_below=True)
    below._show_tooltip()
    above = MdTooltip(btn, "Help text", wait_ms=0, prefer_below=False)
    above._show_tooltip()
    # When preferring below, the tooltip sits lower than when preferring above.
    assert below.y() > above.y()


def test_renders(qtbot):
    host, btn = _target(qtbot)
    tip = MdTooltip(btn, "Help text", wait_ms=0)
    tip._show_tooltip()
    tip.grab()


def test_reparents_to_window_when_attached_before_parenting(qtbot):
    # Regression: tooltips are often attached inside a widget builder, before the
    # target is added to its window (so target.window() is briefly the target
    # itself). The tooltip must rebind to the real top-level window on show, or
    # it's parented to — and clipped by — the target and never appears.
    from PySide6.QtWidgets import QVBoxLayout

    btn = QPushButton("Hover me")  # no parent yet
    tip = MdTooltip(btn, "Help text", wait_ms=0, show_ms=0)
    assert tip.parentWidget() is btn  # stale parent captured at construction

    host = QWidget()
    host.resize(400, 300)
    QVBoxLayout(host).addWidget(btn)
    qtbot.addWidget(host)
    host.show()
    qtbot.waitExposed(host)

    tip._show_tooltip()
    assert tip.parentWidget() is host  # rebound to the real window
    assert not tip.isHidden()
    # Positioned within the window, not off in the button's coordinate space.
    assert 0 <= tip.x() <= host.width() - tip.width()
    assert 0 <= tip.y() <= host.height() - tip.height()


def test_target_deleted_during_wait_no_error(qtbot):
    """Regression: the wait-timer callback dereferenced the dead target and
    raised RuntimeError when the target was deleteLater'd mid-hover."""
    host, btn = _target(qtbot)
    tip = MdTooltip(btn, "Help text", wait_ms=30, show_ms=0)
    _hover_enter(btn)
    btn.deleteLater()
    qtbot.wait(100)  # let the wait timer fire against the dead target
    assert tip.isHidden()


def test_target_destroyed_while_showing_hides(qtbot):
    host, btn = _target(qtbot)
    tip = MdTooltip(btn, "Help text", wait_ms=0, show_ms=0)
    _hover_enter(btn)
    qtbot.waitUntil(lambda: not tip.isHidden(), timeout=500)
    btn.deleteLater()
    qtbot.wait(20)
    assert tip.isHidden()
