"""Tests for MdRefreshIndicator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel

from material_qt.tokens.color import ColorRole
from material_qt.widgets.refreshindicator import MdRefreshIndicator
from material_qt.widgets.refreshindicator import refreshindicator as mod


def test_default_state(qtbot):
    w = MdRefreshIndicator()
    qtbot.addWidget(w)
    assert w.is_refreshing is False
    assert w.displacement == 40
    assert w.color_role == ColorRole.PRIMARY
    assert w.child is None


def test_set_child(qtbot):
    w = MdRefreshIndicator()
    qtbot.addWidget(w)
    label = QLabel("content")
    w.set_child(label)
    assert w.child is label
    assert label.parentWidget() is w


def test_child_via_constructor(qtbot):
    label = QLabel("content")
    w = MdRefreshIndicator(label)
    qtbot.addWidget(w)
    assert w.child is label


def test_begin_reveals_spinner_no_signal(qtbot):
    w = MdRefreshIndicator()
    qtbot.addWidget(w)
    fired = []
    w.refresh.connect(lambda: fired.append(True))
    w.begin()
    assert w.is_refreshing is True
    assert not w._spinner.isHidden()
    assert fired == []


def test_trigger_emits_refresh(qtbot):
    w = MdRefreshIndicator()
    qtbot.addWidget(w)
    fired = []
    w.refresh.connect(lambda: fired.append(True))
    w.trigger()
    assert w.is_refreshing is True
    assert fired == [True]


def test_end_clears_refreshing(qtbot):
    w = MdRefreshIndicator()
    qtbot.addWidget(w)
    w.begin()
    assert w.is_refreshing is True
    w.end()
    assert w.is_refreshing is False


def test_finish_is_alias_for_end(qtbot):
    w = MdRefreshIndicator()
    qtbot.addWidget(w)
    w.begin()
    w.finish()
    assert w.is_refreshing is False


def test_end_hides_spinner_without_motion(qtbot, monkeypatch):
    # No-motion branch runs the dismiss synchronously and hides the spinner.
    monkeypatch.setattr(mod, "MOTION_ENABLED", False)
    w = MdRefreshIndicator()
    qtbot.addWidget(w)
    w.begin()
    assert not w._spinner.isHidden()
    w.end()
    assert w.is_refreshing is False
    assert w._spinner.isHidden()


def test_end_hides_spinner_with_motion(qtbot):
    # Motion-ON branch hides the spinner once the dismiss animation finishes.
    w = MdRefreshIndicator()
    qtbot.addWidget(w)
    w.show()
    qtbot.waitExposed(w)
    w.begin()
    w.end()
    qtbot.waitUntil(lambda: w._spinner.isHidden(), timeout=2000)
    assert w._spinner.isHidden()


def test_spinner_is_indeterminate_and_loops(qtbot):
    w = MdRefreshIndicator()
    qtbot.addWidget(w)
    w.show()
    qtbot.waitExposed(w)
    w.begin()
    assert w._spinner.indeterminate is True
    # The looping spinner must use an infinite loop count, not a one-shot
    # (a default loopCount of 1 animates once then freezes).
    assert w._spinner._anim is not None
    assert w._spinner._anim.loopCount() == -1


def test_set_displacement(qtbot):
    w = MdRefreshIndicator()
    qtbot.addWidget(w)
    w.set_displacement(80)
    assert w.displacement == 80


def test_set_color_role(qtbot):
    w = MdRefreshIndicator()
    qtbot.addWidget(w)
    w.set_color_role(ColorRole.SECONDARY)
    assert w.color_role == ColorRole.SECONDARY


def test_renders(qtbot):
    w = MdRefreshIndicator(QLabel("hello"))
    qtbot.addWidget(w)
    w.resize(300, 300)
    w.begin()
    assert w.grab() is not None
