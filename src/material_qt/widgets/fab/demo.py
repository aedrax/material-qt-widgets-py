"""Demo: ``python -m material_qt.widgets.fab.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...theme.theme_manager import ThemeManager, ThemeMode
from .fab import FabColor, FabSize, MdBrandedFab, MdFab


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — FAB")
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(18)

        sizes = QHBoxLayout()
        sizes.setSpacing(20)
        sizes.addWidget(MdFab("edit", size=FabSize.SMALL))
        sizes.addWidget(MdFab("edit", size=FabSize.REGULAR))
        sizes.addWidget(MdFab("edit", size=FabSize.LARGE))
        sizes.addWidget(MdBrandedFab())
        sizes.addStretch(1)
        root.addWidget(QLabel("Sizes (small / regular / large / branded):"))
        root.addLayout(sizes)

        colors = QHBoxLayout()
        colors.setSpacing(16)
        for c in (FabColor.SURFACE, FabColor.PRIMARY, FabColor.SECONDARY, FabColor.TERTIARY):
            colors.addWidget(MdFab("add", color=c))
        colors.addStretch(1)
        root.addWidget(QLabel("Colors (surface / primary / secondary / tertiary):"))
        root.addLayout(colors)

        ext = QHBoxLayout()
        ext.setSpacing(16)
        ext.addWidget(MdFab("add", label="Compose", color=FabColor.PRIMARY))
        ext.addWidget(MdBrandedFab(label="Create"))
        ext.addStretch(1)
        root.addWidget(QLabel("Extended:"))
        root.addLayout(ext)

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
    w.resize(520, 420)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
