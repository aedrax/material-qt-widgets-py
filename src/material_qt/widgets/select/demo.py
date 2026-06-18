"""Demo: ``python -m material_qt.widgets.select.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

from ...theme.theme_manager import ThemeManager, ThemeMode
from .select import MdFilledSelect, MdOutlinedSelect


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Select")
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(20)

        self._status = QLabel("(no selection)")

        filled = MdFilledSelect(label="Fruit", supporting_text="Pick one")
        for f in ("Apple", "Banana", "Cherry", "Date"):
            filled.add_option(f)
        filled.changed.connect(lambda v: self._status.setText(f"Chose: {v}"))
        filled.setMinimumWidth(280)
        root.addWidget(filled)

        outlined = MdOutlinedSelect(label="Country")
        for c in ("USA", "Canada", "Mexico"):
            outlined.add_option(c)
        outlined.set_value("Canada")
        outlined.setMinimumWidth(280)
        root.addWidget(outlined)

        root.addWidget(self._status)
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
