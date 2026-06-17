"""Demo: ``python -m material_qt.widgets.iconbutton.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...theme.theme_manager import ThemeManager, ThemeMode
from .iconbutton import (
    MdFilledIconButton,
    MdFilledTonalIconButton,
    MdIconButton,
    MdOutlinedIconButton,
)


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Icon buttons")
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(16)

        variants = [
            ("Standard", MdIconButton),
            ("Filled", MdFilledIconButton),
            ("Tonal", MdFilledTonalIconButton),
            ("Outlined", MdOutlinedIconButton),
        ]
        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(12)
        grid.addWidget(QLabel("static"), 0, 0)
        grid.addWidget(QLabel("toggle (on)"), 0, 1)
        grid.addWidget(QLabel("disabled"), 0, 2)
        for r, (label, cls) in enumerate(variants, start=1):
            grid.addWidget(QLabel(label), r, 3)
            grid.addWidget(cls("favorite"), r, 0)
            grid.addWidget(
                cls("favorite", toggle=True, selected_icon="favorite", checked=True),
                r,
                1,
            )
            d = cls("favorite")
            d.setEnabled(False)
            grid.addWidget(d, r, 2)
        root.addLayout(grid)

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
    w.resize(420, 320)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
