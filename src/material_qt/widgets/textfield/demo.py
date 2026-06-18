"""Demo: ``python -m material_qt.widgets.textfield.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

from ...theme.theme_manager import ThemeManager, ThemeMode
from .textfield import MdFilledTextField, MdOutlinedTextField


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Text field")
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(20)
        root.addWidget(
            MdFilledTextField(label="Name", supporting_text="As it appears on your ID")
        )
        root.addWidget(MdOutlinedTextField(label="Email", text="a@b.com"))
        root.addWidget(
            MdOutlinedTextField(label="Password", password=True, error=True,
                                supporting_text="At least 8 characters")
        )
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
    w.resize(420, 320)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
