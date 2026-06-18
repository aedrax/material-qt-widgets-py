"""Demo: ``python -m material_qt.widgets.splitbutton.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

from ...theme.theme_manager import ThemeManager, ThemeMode
from ..menu import MdMenu, MdMenuItem
from .splitbutton import MdSplitButton, SplitButtonColor


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Split button")
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(16)

        self._status = QLabel("(no action)")
        for color in SplitButtonColor:
            sb = MdSplitButton("Save", color=color, icon="save")
            menu = MdMenu(sb)
            for label in ("Save as draft", "Save and close", "Save a copy"):
                menu.add_item(MdMenuItem(label))
            menu.selected.connect(lambda t: self._status.setText(f"Menu: {t}"))
            sb.set_menu(menu)
            sb.clicked.connect(lambda c=color: self._status.setText(f"{c.value}: Save"))
            row = QVBoxLayout()
            row.addWidget(QLabel(color.value))
            row.addWidget(sb)
            holder = QWidget()
            holder.setLayout(row)
            root.addWidget(holder)

        root.addWidget(self._status)
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
    w.resize(420, 420)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
