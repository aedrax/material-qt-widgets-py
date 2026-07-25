"""Tests for Material buttons."""

from __future__ import annotations

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QMouseEvent

from material_qt.tokens.color import ColorRole
from material_qt.tokens.elevation import ElevationLevel
from material_qt.widgets.button import (
    IconAlignment,
    MdElevatedButton,
    MdFilledButton,
    MdOutlinedButton,
    MdTextButton,
)


def test_clicked_signal(qtbot):
    b = MdFilledButton("OK")
    qtbot.addWidget(b)
    clicks = []
    b.clicked.connect(lambda: clicks.append(1))
    b.click()
    assert clicks == [1]


def test_disabled_blocks_click(qtbot):
    b = MdFilledButton("OK")
    qtbot.addWidget(b)
    b.setEnabled(False)
    clicks = []
    b.clicked.connect(lambda: clicks.append(1))
    b.click()
    assert clicks == []


def test_variant_styles(qtbot):
    assert MdFilledButton.STYLE.container_role == ColorRole.PRIMARY
    assert MdFilledButton.STYLE.label_role == ColorRole.ON_PRIMARY
    assert MdElevatedButton.STYLE.elevation == ElevationLevel.LEVEL1
    assert MdElevatedButton.STYLE.hover_elevation == ElevationLevel.LEVEL2
    assert MdOutlinedButton.STYLE.container_role is None
    assert MdOutlinedButton.STYLE.outline_role == ColorRole.OUTLINE
    assert MdTextButton.STYLE.container_role is None


def test_height_and_icon_width(qtbot):
    b = MdFilledButton("Save")
    qtbot.addWidget(b)
    h = b.sizeHint().height()
    assert h == 40
    w_no_icon = b.sizeHint().width()
    b.set_icon("add")
    assert b.sizeHint().width() > w_no_icon


def test_has_ripple_and_focus(qtbot):
    b = MdFilledButton("x")
    qtbot.addWidget(b)
    assert b.ripple is not None
    assert b.focus_ring is not None


def test_renders_without_crash(qtbot):
    for cls in (MdFilledButton, MdElevatedButton, MdOutlinedButton, MdTextButton):
        b = cls("Hi", icon="add")
        qtbot.addWidget(b)
        b.resize(b.sizeHint())
        b.grab()  # forces a paintEvent


def test_tooltip_kwarg(qtbot):
    b = MdFilledButton("OK", tooltip="Confirm")
    qtbot.addWidget(b)
    assert b.toolTip() == "Confirm"


def test_icon_alignment(qtbot):
    b = MdFilledButton("Next", icon="arrow_forward", icon_alignment=IconAlignment.END)
    qtbot.addWidget(b)
    assert b.icon_alignment is IconAlignment.END
    b.resize(b.sizeHint())
    b.grab()  # END layout must paint without crashing
    b.set_icon_alignment(IconAlignment.START)
    assert b.icon_alignment is IconAlignment.START


def test_long_press_signal(qtbot):
    b = MdFilledButton("Hold")
    qtbot.addWidget(b)
    b.resize(b.sizeHint())
    fired = []
    b.longPressed.connect(lambda: fired.append(1))
    press = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPointF(5, 5),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    b.mousePressEvent(press)
    # Fire the timer synchronously rather than waiting the real timeout.
    b._emit_long_press()
    assert fired == [1]


def test_long_press_cancelled_on_release(qtbot):
    b = MdFilledButton("Hold")
    qtbot.addWidget(b)
    b.resize(b.sizeHint())
    press = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPointF(5, 5),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    b.mousePressEvent(press)
    assert b._long_press_timer.isActive()
    release = QMouseEvent(
        QMouseEvent.Type.MouseButtonRelease,
        QPointF(5, 5),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )
    b.mouseReleaseEvent(release)
    assert not b._long_press_timer.isActive()


def test_long_press_suppresses_click(qtbot):
    """A fired long press must NOT also emit clicked (matches Flutter onTap)."""
    b = MdFilledButton("Hold")
    qtbot.addWidget(b)
    b.resize(b.sizeHint())
    longs, clicks = [], []
    b.longPressed.connect(lambda: longs.append(1))
    b.clicked.connect(lambda: clicks.append(1))
    press = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPointF(5, 5),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    b.mousePressEvent(press)
    b._emit_long_press()  # fire the timer synchronously
    release = QMouseEvent(
        QMouseEvent.Type.MouseButtonRelease,
        QPointF(5, 5),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )
    b.mouseReleaseEvent(release)
    assert longs == [1]
    assert clicks == []  # long press consumed the release


def test_short_press_still_clicks(qtbot):
    """A normal press/release (no long press) still emits clicked."""
    b = MdFilledButton("Tap")
    qtbot.addWidget(b)
    b.resize(b.sizeHint())
    clicks = []
    b.clicked.connect(lambda: clicks.append(1))
    press = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPointF(5, 5),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    release = QMouseEvent(
        QMouseEvent.Type.MouseButtonRelease,
        QPointF(5, 5),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )
    b.mousePressEvent(press)
    b.mouseReleaseEvent(release)
    assert clicks == [1]


def test_return_key_activates(qtbot):
    """Regression: Return/Enter showed a keyboard ripple but activated nothing
    (QAbstractButton only clicks on Space)."""
    from PySide6.QtCore import QEvent
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QApplication

    b = MdFilledButton("OK")
    qtbot.addWidget(b)
    clicks = []
    b.clicked.connect(lambda: clicks.append(1))
    # sendEvent so the ripple's event filter (which routes the click) runs.
    QApplication.sendEvent(
        b, QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
    )
    QApplication.sendEvent(
        b, QKeyEvent(QEvent.Type.KeyRelease, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
    )
    assert clicks == [1]
    # An auto-repeated Return must not fire again.
    QApplication.sendEvent(
        b,
        QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Return,
            Qt.KeyboardModifier.NoModifier,
            "",
            True,  # autorep
        ),
    )
    assert clicks == [1]


def test_space_key_still_activates_once(qtbot):
    from PySide6.QtCore import QEvent
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QApplication

    b = MdFilledButton("OK")
    qtbot.addWidget(b)
    clicks = []
    b.clicked.connect(lambda: clicks.append(1))
    QApplication.sendEvent(
        b, QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier)
    )
    QApplication.sendEvent(
        b, QKeyEvent(QEvent.Type.KeyRelease, Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier)
    )
    assert clicks == [1]  # Qt's own Space handling; no double-fire


def test_return_key_ignored_when_disabled(qtbot):
    from PySide6.QtCore import QEvent
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QApplication

    b = MdFilledButton("OK")
    qtbot.addWidget(b)
    b.setEnabled(False)
    clicks = []
    b.clicked.connect(lambda: clicks.append(1))
    QApplication.sendEvent(
        b, QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
    )
    assert clicks == []


def test_autofocus_on_show(qtbot):
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

    host = QWidget()
    layout = QVBoxLayout(host)
    other = MdFilledButton("Other")
    target = MdFilledButton("Target", autofocus=True)
    layout.addWidget(other)
    layout.addWidget(target)
    qtbot.addWidget(host)
    host.show()
    QApplication.setActiveWindow(host)  # offscreen needs an active window
    qtbot.waitExposed(host)
    assert target.hasFocus()


def test_no_autofocus_by_default(qtbot):
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

    host = QWidget()
    layout = QVBoxLayout(host)
    other = MdFilledButton("Other")
    target = MdFilledButton("Target")  # autofocus defaults to False
    layout.addWidget(other)
    layout.addWidget(target)
    qtbot.addWidget(host)
    host.show()
    QApplication.setActiveWindow(host)
    qtbot.waitExposed(host)
    assert not target.hasFocus()
