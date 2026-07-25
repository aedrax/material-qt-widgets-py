"""Demo: ``python -m material_qt.widgets.draggablesheet.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

from ...theme.theme_manager import ThemeManager, ThemeMode
from .draggablesheet import MdDraggableScrollableSheet


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Draggable scrollable sheet")
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.addWidget(QLabel("Body content sits behind the sheet."))
        toggle = QPushButton("Toggle light / dark")
        toggle.clicked.connect(self._toggle)
        root.addWidget(toggle)
        root.addStretch(1)
        self._dark = False

        self._sheet = MdDraggableScrollableSheet(
            self, initial_size=0.4, min_size=0.2, max_size=0.95,
            snap_sizes=[0.4, 0.7])
        for i in range(30):
            self._sheet.add_content(QLabel(f"Item {i + 1}"))
        self._sheet.sizeChanged.connect(
            lambda f: self.setWindowTitle(f"Sheet — {f:.0%}"))

    def _toggle(self) -> None:
        self._dark = not self._dark
        ThemeManager.instance().set_mode(
            ThemeMode.DARK if self._dark else ThemeMode.LIGHT)

    def resizeEvent(self, event):  # noqa: N802
        super().resizeEvent(event)
        self._sheet.raise_()


def main() -> int:
    app = QApplication(sys.argv)
    w = Demo()
    w.resize(440, 560)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
