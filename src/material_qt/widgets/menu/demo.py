"""Demo: ``python -m material_qt.widgets.menu.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from ...theme.theme_manager import ThemeManager, ThemeMode
from ..button import MdFilledButton
from .menu import MdMenu, MdMenuItem


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Menu")
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(12)

        self._trigger = MdFilledButton("Open menu")
        self._trigger.clicked.connect(self._open_menu)
        root.addWidget(self._trigger)
        self._status = QLabel("(no selection)")
        root.addWidget(self._status)

        toggle = MdFilledButton("Toggle light / dark")
        toggle.clicked.connect(self._toggle)
        root.addWidget(toggle)
        root.addStretch(1)
        self._dark = False

    def _open_menu(self) -> None:
        menu = MdMenu(self)
        for label, icon in [("Cut", "content_cut"), ("Copy", "content_copy"),
                            ("Paste", "content_paste"), ("Delete", "delete")]:
            menu.add_item(MdMenuItem(label, leading_icon=icon))
        menu.selected.connect(lambda t: self._status.setText(f"Selected: {t}"))
        menu.open_at(self._trigger)

    def _toggle(self) -> None:
        self._dark = not self._dark
        ThemeManager.instance().set_mode(
            ThemeMode.DARK if self._dark else ThemeMode.LIGHT
        )


def main() -> int:
    app = QApplication(sys.argv)
    w = Demo()
    w.resize(360, 220)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
