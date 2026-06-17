"""Demo: ``python -m material_qt.widgets.chips.demo``."""

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
from .chips import (
    MdAssistChip,
    MdChipSet,
    MdFilterChip,
    MdInputChip,
    MdSuggestionChip,
)


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Chips")
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(14)

        root.addWidget(QLabel("Assist / Suggestion"))
        s1 = MdChipSet()
        s1.add_chip(MdAssistChip("Add to calendar", icon="event"))
        s1.add_chip(MdSuggestionChip("Suggestion"))
        root.addWidget(s1)

        root.addWidget(QLabel("Filter (selectable)"))
        s2 = MdChipSet()
        s2.add_chip(MdFilterChip("All", selected=True))
        s2.add_chip(MdFilterChip("Unread"))
        s2.add_chip(MdFilterChip("Starred"))
        root.addWidget(s2)

        root.addWidget(QLabel("Input (removable)"))
        s3 = MdChipSet()
        for name in ("Alice", "Bob", "Carol"):
            s3.add_chip(MdInputChip(name, icon="person"))
        root.addWidget(s3)

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
    w.resize(520, 320)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
