"""Demo: ``python -m material_qt.widgets.item.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...theme.theme_manager import ThemeManager, ThemeMode
from ..icon.icon import MdIcon
from .item import MdItem


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Item")
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(4)

        root.addWidget(MdItem("One-line item"))
        root.addWidget(
            MdItem(
                "Two-line item",
                supporting_text="Supporting text on the second line",
                leading=MdIcon("folder"),
            )
        )
        root.addWidget(
            MdItem(
                "Three-line item with trailing",
                supporting_text=(
                    "Longer supporting text that may wrap across "
                    "multiple lines in the item body."
                ),
                trailing_supporting_text="100+",
                leading=MdIcon("email"),
                trailing=MdIcon("chevron_right"),
            )
        )

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
    w.resize(460, 320)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
