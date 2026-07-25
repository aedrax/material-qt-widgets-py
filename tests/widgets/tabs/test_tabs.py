"""Tests for MdTabs / MdTab."""

from __future__ import annotations

from PySide6.QtGui import QColor

from material_qt.widgets.tabs import MdTabs


def test_first_tab_selected_by_default(qtbot):
    t = MdTabs()
    qtbot.addWidget(t)
    a = t.add_tab("A")
    t.add_tab("B")
    assert a.isChecked()


def test_exclusive_selection_and_signal(qtbot):
    t = MdTabs()
    qtbot.addWidget(t)
    a = t.add_tab("A")
    b = t.add_tab("B")
    seen = []
    t.changed.connect(seen.append)
    b.setChecked(True)
    assert b.isChecked() and not a.isChecked()
    assert seen[-1] == 1


def test_indicator_moves(qtbot):
    t = MdTabs()
    qtbot.addWidget(t)
    a = t.add_tab("Alpha")
    b = t.add_tab("Bravo")
    t.resize(300, 48)
    t.show()
    a.setChecked(True)
    b.setChecked(True)
    # After selecting b, the indicator target center is to the right of a's.
    cx_b, _ = t._indicator_target(b)
    cx_a, _ = t._indicator_target(a)
    assert cx_b > cx_a


def test_renders_primary_and_secondary(qtbot):
    for secondary in (False, True):
        t = MdTabs(secondary=secondary)
        qtbot.addWidget(t)
        t.add_tab("One", icon="" if secondary else "flight")
        t.add_tab("Two")
        t.resize(300, 48)
        t.grab()


def test_indicator_positioned_after_show(qtbot):
    # Regression: the indicator must sit under the active tab on first display,
    # not at a stale pre-layout position.
    from PySide6.QtWidgets import QVBoxLayout, QWidget
    host = QWidget()
    host.resize(600, 48)
    lay = QVBoxLayout(host)
    lay.setContentsMargins(0, 0, 0, 0)
    t = MdTabs()
    qtbot.addWidget(host)
    a = t.add_tab("Alpha")
    t.add_tab("Bravo")
    t.add_tab("Charlie")
    lay.addWidget(t)
    host.show()
    qtbot.waitExposed(host)
    cx, _ = t._indicator_target(a)
    assert abs(t._ind - cx) < 1.0


def test_resize_during_selection_animation_resnaps(qtbot):
    # Regression: _reposition_indicator skips while the selection animation
    # runs, so a resize mid-slide left the indicator at the stale pre-resize
    # position until the next selection. It must re-snap when the slide lands.
    t = MdTabs()
    qtbot.addWidget(t)
    t.add_tab("Alpha")
    b = t.add_tab("Bravo")
    t.add_tab("Charlie")
    t.resize(300, 48)
    t.show()
    qtbot.waitExposed(t)
    t.set_selected_index(1)
    assert t._anim.state() == t._anim.State.Running  # motion ON: it slides
    t.resize(500, 48)  # mid-animation layout change
    qtbot.waitUntil(lambda: t._anim.state() != t._anim.State.Running,
                    timeout=1000)
    cx, w = t._indicator_target(b)
    assert abs(t._ind - cx) < 1.0
    assert abs(t._ind_w - w) < 1.0


def test_selected_index_round_trip(qtbot):
    t = MdTabs()
    qtbot.addWidget(t)
    t.add_tab("A")
    t.add_tab("B")
    t.add_tab("C")
    assert t.selected_index == 0
    t.selected_index = 2
    assert t.selected_index == 2
    t.set_selected_index(1)
    assert t.selected_index == 1
    t.set_selected_index(99)
    assert t.selected_index == 1


def test_scrollable_tabs_overflow_and_render(qtbot):
    t = MdTabs(scrollable=True)
    qtbot.addWidget(t)
    assert t.is_scrollable
    for i in range(10):
        t.add_tab(f"Section {i}")
    t.resize(300, 48)
    t.show()
    # the inner strip is wider than the viewport -> it scrolls.
    assert t._strip.sizeHint().width() > 300
    # selecting a far tab keeps it visible without raising, and the indicator
    # (painted in strip coords alongside the tabs) settles under that tab.
    t.set_selected_index(9)
    qtbot.waitUntil(lambda: t._anim.state() != t._anim.State.Running, timeout=1000)
    far = t._tabs[9]
    assert far.geometry().left() <= t._ind <= far.geometry().right()
    t.grab()


def test_scrollable_toggle(qtbot):
    t = MdTabs()
    qtbot.addWidget(t)
    t.add_tab("A")
    assert not t.is_scrollable
    t.set_scrollable(True)
    assert t.is_scrollable


def test_indicator_and_label_color_overrides(qtbot):
    t = MdTabs()
    qtbot.addWidget(t)
    tab = t.add_tab("A")
    t.set_indicator_color(QColor("#ff0000"))
    t.set_indicator_weight(5.0)
    t.set_label_color(QColor("#00ff00"))
    t.set_unselected_label_color(QColor("#0000ff"))
    t.set_divider_color(QColor("#123456"))
    assert t._indicator_color == QColor("#ff0000")
    assert t._indicator_weight == 5.0
    assert tab._label_color == QColor("#00ff00")
    assert tab._unselected_label_color == QColor("#0000ff")
    t.resize(200, 48)
    t.grab()


def test_indicator_size(qtbot):
    t = MdTabs()
    qtbot.addWidget(t)
    a = t.add_tab("A long label")
    t.add_tab("B")
    t.resize(400, 48)
    t.show()
    t.set_indicator_size("tab")
    _, w_tab = t._indicator_target(a)
    t.set_indicator_size("label")
    _, w_label = t._indicator_target(a)
    assert w_tab >= w_label  # full-tab indicator is at least the label width
