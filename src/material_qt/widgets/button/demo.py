"""Demo for the Material buttons: ``python -m material_qt.widgets.button.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...theme.theme_manager import ThemeManager, ThemeMode
from .button import (
    MdElevatedButton,
    MdFilledButton,
    MdFilledTonalButton,
    MdOutlinedButton,
    MdTextButton,
)


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Buttons")
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(20)

        variants = [
            ("Elevated", MdElevatedButton),
            ("Filled", MdFilledButton),
            ("Tonal", MdFilledTonalButton),
            ("Outlined", MdOutlinedButton),
            ("Text", MdTextButton),
        ]
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)
        for col, (label, cls) in enumerate(variants):
            grid.addWidget(cls(label), 0, col)
            grid.addWidget(cls(label, icon="add"), 1, col)
            disabled = cls(label)
            disabled.setEnabled(False)
            grid.addWidget(disabled, 2, col)
        root.addLayout(grid)

        toggle = QPushButton("Toggle light / dark")
        toggle.clicked.connect(self._toggle)
        row = QHBoxLayout()
        row.addWidget(toggle)
        row.addStretch(1)
        root.addLayout(row)
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
    w.resize(820, 280)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
