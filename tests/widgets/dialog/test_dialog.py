"""Tests for MdDialog."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from material_qt.widgets.dialog import MdDialog


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


def test_renders(qtbot):
    host = _host(qtbot)
    host.show()
    dlg = MdDialog(host, icon="delete", headline="Delete file?",
                   supporting_text="Cannot be undone.")
    dlg.add_action("Cancel", accept=False)
    dlg.add_action("Delete", accept=True)
    dlg.open()
    dlg.grab()
