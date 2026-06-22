"""Tests for MdDialog."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

from material_qt.widgets.dialog import MdDialog
from material_qt.widgets.iconbutton import MdIconButton


def _host(qtbot) -> QWidget:
    host = QWidget()
    host.resize(600, 400)
    qtbot.addWidget(host)
    return host


def test_open_covers_parent(qtbot):
    host = _host(qtbot)
    host.show()
    dlg = MdDialog(host, headline="Hi", supporting_text="Body")
    dlg.open()
    assert dlg.isVisible()
    assert dlg.size() == host.size()


def test_accept_action(qtbot):
    host = _host(qtbot)
    dlg = MdDialog(host, headline="Delete?")
    dlg.add_action("Cancel", accept=False)
    dlg.add_action("OK", accept=True)
    results = []
    dlg.accepted.connect(lambda: results.append("accept"))
    dlg.closed.connect(lambda: results.append("closed"))
    dlg.open()
    # Trigger the accept button (last added).
    dlg._actions.itemAt(dlg._actions.count() - 1).widget().click()
    assert "accept" in results and "closed" in results
    assert not dlg.isVisible()


def test_reject_action(qtbot):
    host = _host(qtbot)
    dlg = MdDialog(host, headline="Delete?")
    dlg.add_action("Cancel", accept=False)
    rejected = []
    dlg.rejected.connect(lambda: rejected.append(1))
    dlg.open()
    dlg._actions.itemAt(dlg._actions.count() - 1).widget().click()
    assert rejected == [1]


def test_close_does_not_leave_focus_ring_on_sibling(qtbot):
    # Closing the dialog (hide) while a button inside it holds focus must not make
    # Qt reassign TabFocusReason focus to a sibling, spuriously showing the
    # sibling's keyboard focus ring (cf. the gallery app-bar theme toggle).
    host = QWidget()
    host.resize(600, 400)
    layout = QVBoxLayout(host)
    sibling = MdIconButton("dark_mode")  # focus_ring=True
    layout.addWidget(sibling)
    qtbot.addWidget(host)
    host.show()
    # Focus only transfers while the top-level window is active; offscreen
    # windows aren't auto-activated, so force it for the repro.
    QApplication.setActiveWindow(host)

    dlg = MdDialog(host, headline="Delete?")
    dlg.add_action("OK", accept=True)
    dlg.open()
    ok = dlg._actions.itemAt(dlg._actions.count() - 1).widget()
    ok.setFocus(Qt.FocusReason.MouseFocusReason)
    ok.click()  # accept -> close_dialog -> hide

    assert not dlg.isVisible()
    assert not sibling.hasFocus()
    assert not sibling.focus_ring.visible


def test_barrier_not_dismissible_ignores_scrim_and_escape(qtbot):
    from PySide6.QtCore import QEvent, QPointF
    from PySide6.QtGui import QKeyEvent, QMouseEvent

    host = _host(qtbot)
    host.show()
    dlg = MdDialog(host, headline="Saving...", barrier_dismissible=False)
    rejected = []
    dlg.rejected.connect(lambda: rejected.append(1))
    dlg.open()
    # Click on the scrim (top-left corner, outside the centered panel).
    press = QMouseEvent(
        QEvent.Type.MouseButtonPress, QPointF(2, 2), Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier,
    )
    dlg.mousePressEvent(press)
    esc = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
    dlg.keyPressEvent(esc)
    assert rejected == [] and dlg.isVisible()
    # Toggling the flag back on restores dismissal.
    dlg.set_barrier_dismissible(True)
    dlg.mousePressEvent(press)
    assert rejected == [1] and not dlg.isVisible()


def test_add_option_returns_clickable_row(qtbot):
    host = _host(qtbot)
    dlg = MdDialog(host, headline="Pick one")
    fired = []
    opt = dlg.add_option("Photos")
    opt.clicked.connect(lambda: fired.append("photos"))
    opt.click()
    assert fired == ["photos"]


def test_renders(qtbot):
    host = _host(qtbot)
    host.show()
    dlg = MdDialog(host, icon="delete", headline="Delete file?",
                   supporting_text="Cannot be undone.")
    dlg.add_action("Cancel", accept=False)
    dlg.add_action("Delete", accept=True)
    dlg.open()
    dlg.grab()
