"""Demo: ``python -m material_qt.widgets.switch.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...theme.theme_manager import ThemeManager, ThemeMode
from .switch import MdSwitch


def _row(label: str, sw: MdSwitch) -> QWidget:
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(sw)
    lay.addWidget(QLabel(label))
    lay.addStretch(1)
    return w


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Switch")
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.addWidget(_row("Off", MdSwitch()))
        root.addWidget(_row("On", MdSwitch(checked=True)))
        off_d = MdSwitch()
        off_d.setEnabled(False)
        on_d = MdSwitch(checked=True)
        on_d.setEnabled(False)
        root.addWidget(_row("Disabled off", off_d))
        root.addWidget(_row("Disabled on", on_d))
        toggle = QPushButton("Toggle light / dark")
        toggle.clicked.connect(self._toggle)
        root.addWidget(toggle)
        root.addStretch(1)
        self._dark = False

    def _toggle(self) -> None:
        self._dark = not self._dark
        ThemeManager.instance().set_mode(
            ThemeMode.DARK if self._dark else ThemeMode.LIGHT
        )


def main() -> int:
    app = QApplication(sys.argv)
    w = Demo()
    w.resize(360, 320)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
