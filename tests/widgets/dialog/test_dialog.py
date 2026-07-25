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
    # The sibling held focus when the dialog opened, so the overlay's focus
    # restore intentionally hands focus back to it — but with OtherFocusReason,
    # which must not light up its keyboard focus ring.
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


def test_tab_is_confined_to_the_open_dialog(qtbot):
    # With a modal open, the mouse is blocked by the scrim — Tab must not walk
    # into widgets behind it either. Tab from the last button wraps to the
    # first focusable inside the dialog; Backtab wraps the other way.
    from PySide6.QtCore import QEvent
    from PySide6.QtGui import QKeyEvent

    host = QWidget()
    host.resize(600, 400)
    layout = QVBoxLayout(host)
    background = MdIconButton("dark_mode")
    layout.addWidget(background)
    qtbot.addWidget(host)
    host.show()
    QApplication.setActiveWindow(host)

    dlg = MdDialog(host, headline="Delete?")
    cancel = dlg.add_action("Cancel", accept=False)
    ok = dlg.add_action("OK", accept=True)
    dlg.open()

    ok.setFocus(Qt.FocusReason.TabFocusReason)
    assert ok.hasFocus()
    tab = QKeyEvent(
        QEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier
    )
    QApplication.sendEvent(ok, tab)
    fw = QApplication.focusWidget()
    assert fw is not background
    assert dlg.isAncestorOf(fw)
    assert fw is cancel  # wrapped to the first focusable inside the dialog

    backtab = QKeyEvent(
        QEvent.Type.KeyPress, Qt.Key.Key_Backtab, Qt.KeyboardModifier.ShiftModifier
    )
    QApplication.sendEvent(cancel, backtab)
    assert QApplication.focusWidget() is ok  # wrapped back to the last


def test_focus_returns_to_previous_owner_on_close(qtbot):
    # The widget focused before open() (e.g. the button that launched the
    # dialog) regains focus when the dialog closes.
    host = QWidget()
    host.resize(600, 400)
    layout = QVBoxLayout(host)
    trigger = MdIconButton("dark_mode")
    layout.addWidget(trigger)
    qtbot.addWidget(host)
    host.show()
    QApplication.setActiveWindow(host)
    trigger.setFocus(Qt.FocusReason.MouseFocusReason)
    assert trigger.hasFocus()

    dlg = MdDialog(host, headline="Delete?")
    ok = dlg.add_action("OK", accept=True)
    dlg.open()
    ok.setFocus(Qt.FocusReason.TabFocusReason)
    assert not trigger.hasFocus()
    dlg.close_dialog()

    assert not dlg.isVisible()
    assert trigger.hasFocus()
    # Restored with OtherFocusReason — no keyboard focus ring appears.
    assert not trigger.focus_ring.visible


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


def test_theme_toggle_after_delete_does_not_raise(qtbot):
    """Regression: label/option restyles were plain closures on the singleton
    ThemeManager, so a theme change after the dialog died raised RuntimeError."""
    from material_qt.theme.theme_manager import ThemeManager

    host = _host(qtbot)
    dlg = MdDialog(host, headline="Hi", supporting_text="Body")
    dlg.add_option("Photos")
    dlg.deleteLater()
    qtbot.wait(20)  # process the deferred delete
    ThemeManager.instance().toggle_light_dark()  # must not raise
    ThemeManager.instance().toggle_light_dark()


def test_labels_and_options_restyle_on_theme_change(qtbot):
    from material_qt.theme.theme_manager import ThemeManager

    host = _host(qtbot)
    dlg = MdDialog(host, headline="Hi")
    opt = dlg.add_option("Photos")
    before = opt.styleSheet()
    ThemeManager.instance().toggle_light_dark()
    assert opt.styleSheet() != before
