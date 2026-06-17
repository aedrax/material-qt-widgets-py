"""Demo: ``python -m material_qt.widgets.card.demo``."""

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
from .card import CardVariant, MdCard


def _card(variant: CardVariant, title: str) -> MdCard:
    card = MdCard(variant=variant)
    card.add_widget(QLabel(title))
    card.add_widget(QLabel("Supporting line of card content."))
    card.setFixedSize(200, 120)
    return card


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Card")
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        row = QHBoxLayout()
        row.setSpacing(16)
        row.addWidget(_card(CardVariant.ELEVATED, "Elevated"))
        row.addWidget(_card(CardVariant.FILLED, "Filled"))
        row.addWidget(_card(CardVariant.OUTLINED, "Outlined"))
        row.addStretch(1)
        root.addLayout(row)
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
    w.resize(720, 240)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
