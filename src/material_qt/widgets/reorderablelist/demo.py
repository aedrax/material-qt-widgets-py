"""Demo: ``python -m material_qt.widgets.reorderablelist.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

from ...theme.theme_manager import ThemeManager, ThemeMode
from ..icon import MdIcon
from ..list import MdListItem
from .reorderablelist import MdReorderableList


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Reorderable list")
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)

        lst = MdReorderableList()
        for name, icon in [
            ("Reduce", "wb_sunny"),
            ("Reuse", "recycling"),
            ("Recycle", "compost"),
            ("Repair", "build"),
        ]:
            lst.add_item(MdListItem(name, leading=MdIcon(icon), interactive=False))
        lst.reordered.connect(lambda o, n: print(f"reordered {o} -> {n}"))
        root.addWidget(lst)

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
    w.resize(420, 360)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
