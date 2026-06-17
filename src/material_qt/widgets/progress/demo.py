"""Demo: ``python -m material_qt.widgets.progress.demo``."""

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
from .progress import MdCircularProgress, MdLinearProgress


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Progress")
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(16)

        root.addWidget(QLabel("Linear determinate (60%):"))
        root.addWidget(MdLinearProgress(value=0.6))
        root.addWidget(QLabel("Linear indeterminate:"))
        root.addWidget(MdLinearProgress(indeterminate=True))

        circ = QHBoxLayout()
        circ.setSpacing(24)
        circ.addWidget(MdCircularProgress(value=0.25))
        circ.addWidget(MdCircularProgress(value=0.7))
        circ.addWidget(MdCircularProgress(indeterminate=True))
        circ.addStretch(1)
        root.addWidget(QLabel("Circular (25% / 70% / indeterminate):"))
        root.addLayout(circ)

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
