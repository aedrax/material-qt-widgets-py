"""Demo: ``python -m material_qt.widgets.navigationtab.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...theme.theme_manager import ThemeManager, ThemeMode
from .navigationtab import MdNavigationTab


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Navigation tab")
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)

        bar = QHBoxLayout()
        bar.setSpacing(0)
        group = QButtonGroup(self)
        tabs = [
            ("Home", "home"),
            ("Search", "search"),
            ("Saved", "bookmark"),
            ("Profile", "person"),
        ]
        for i, (label, icon) in enumerate(tabs):
            t = MdNavigationTab(label, icon=icon)
            if i == 0:
                t.setChecked(True)
            group.addButton(t)
            bar.addWidget(t)
        self._group = group
        holder = QWidget()
        holder.setLayout(bar)
        root.addWidget(holder)

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
    w.resize(480, 200)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
