"""Demo: ``python -m material_qt.widgets.slider.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...theme.theme_manager import ThemeManager, ThemeMode
from .slider import MdSlider


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Slider")
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(16)

        root.addWidget(QLabel("Continuous:"))
        root.addWidget(MdSlider(value=40))

        root.addWidget(QLabel("Discrete (step 10, ticks):"))
        root.addWidget(MdSlider(value=60, step=10, ticks=True))

        root.addWidget(QLabel("Divisions (5 intervals, labeled):"))
        root.addWidget(MdSlider(value=40, divisions=5, labeled=True))

        root.addWidget(QLabel("Disabled:"))
        d = MdSlider(value=30)
        d.setEnabled(False)
        root.addWidget(d)

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
    w.resize(420, 300)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
