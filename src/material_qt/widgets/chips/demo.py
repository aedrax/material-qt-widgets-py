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
from PySide6.QtWidgets import QButtonGroup

from .chips import (
    MdAssistChip,
    MdChipSet,
    MdChoiceChip,
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

        root.addWidget(QLabel("Assist / Suggestion (+ elevated)"))
        s1 = MdChipSet()
        s1.add_chip(MdAssistChip("Add to calendar", icon="event"))
        s1.add_chip(MdSuggestionChip("Suggestion"))
        s1.add_chip(MdAssistChip("Elevated", icon="bolt", elevated=True))
        root.addWidget(s1)

        root.addWidget(QLabel("Choice (single-select)"))
        s_choice = MdChipSet()
        group = QButtonGroup(self)
        group.setExclusive(True)
        for i, name in enumerate(("Small", "Medium", "Large")):
            chip = MdChoiceChip(name, selected=(i == 0))
            group.addButton(chip)
            s_choice.add_chip(chip)
        root.addWidget(s_choice)

        root.addWidget(QLabel("Filter (selectable; last is deletable)"))
        s2 = MdChipSet()
        s2.add_chip(MdFilterChip("All", selected=True))
        s2.add_chip(MdFilterChip("Unread"))
        s2.add_chip(MdFilterChip("Starred", deletable=True))
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
