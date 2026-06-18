"""Demo: ``python -m material_qt.widgets.tabs.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

from ...theme.theme_manager import ThemeManager, ThemeMode
from .tabs import MdTabs


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Tabs")
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        root.addWidget(QLabel("Primary"))
        primary = MdTabs()
        primary.add_tab("Flights", icon="flight")
        primary.add_tab("Trips", icon="luggage")
        primary.add_tab("Explore", icon="explore")
        root.addWidget(primary)

        root.addWidget(QLabel("Secondary"))
        secondary = MdTabs(secondary=True)
        for t in ("Overview", "Specifications", "Reviews"):
            secondary.add_tab(t)
        root.addWidget(secondary)

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
    w.resize(520, 280)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
