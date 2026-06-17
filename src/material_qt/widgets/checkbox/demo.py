"""Demo: ``python -m material_qt.widgets.checkbox.demo``."""

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
from .checkbox import MdCheckbox


def _row(label: str, cb: MdCheckbox) -> QWidget:
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(cb)
    lay.addWidget(QLabel(label))
    lay.addStretch(1)
    return w


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Checkbox")
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)

        unchecked = MdCheckbox()
        checked = MdCheckbox(checked=True)
        indet = MdCheckbox()
        indet.set_indeterminate(True)
        err = MdCheckbox(checked=True, error=True)
        disabled = MdCheckbox(checked=True)
        disabled.setEnabled(False)

        root.addWidget(_row("Unchecked", unchecked))
        root.addWidget(_row("Checked", checked))
        root.addWidget(_row("Indeterminate", indet))
        root.addWidget(_row("Error", err))
        root.addWidget(_row("Disabled", disabled))

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
