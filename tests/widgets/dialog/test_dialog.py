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


def test_renders(qtbot):
    host = _host(qtbot)
    host.show()
    dlg = MdDialog(host, icon="delete", headline="Delete file?",
                   supporting_text="Cannot be undone.")
    dlg.add_action("Cancel", accept=False)
    dlg.add_action("Delete", accept=True)
    dlg.open()
    dlg.grab()
