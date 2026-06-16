"""Self-contained demo for :class:`MdIcon`.

Run with::

    python -m material_qt.widgets.icon.demo

Shows several icons at a couple of sizes, outlined vs filled, with a button to
toggle light/dark themes. If no Material Symbols font is installed, the icons
fall back to a labelled placeholder box (see the note printed on launch).
"""

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
from .icon import MdIcon

_ICON_NAMES = ["favorite", "settings", "home", "check_box", "delete", "search"]


class _Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MdIcon demo")
        root = QVBoxLayout(self)

        probe = MdIcon("favorite")
        status = (
            f"Material Symbols font: {probe.font_family}"
            if probe.font_available
            else "No Material Symbols font found - rendering placeholder boxes."
        )
        root.addWidget(QLabel(status))

        grid = QGridLayout()
        root.addLayout(grid)
        # Header row.
        grid.addWidget(QLabel("name"), 0, 0)
        grid.addWidget(QLabel("18px"), 0, 1)
        grid.addWidget(QLabel("24px"), 0, 2)
        grid.addWidget(QLabel("40px"), 0, 3)
        grid.addWidget(QLabel("filled 40px"), 0, 4)
        for row, name in enumerate(_ICON_NAMES, start=1):
            grid.addWidget(QLabel(name), row, 0)
            grid.addWidget(MdIcon(name, size=18), row, 1)
            grid.addWidget(MdIcon(name, size=24), row, 2)
            grid.addWidget(MdIcon(name, size=40), row, 3)
            grid.addWidget(MdIcon(name, size=40, filled=True), row, 4)

        controls = QHBoxLayout()
        root.addLayout(controls)
        toggle = QPushButton("Toggle light / dark")
        toggle.clicked.connect(ThemeManager.instance().toggle_light_dark)
        controls.addWidget(toggle)
        controls.addStretch(1)


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    ThemeManager.instance().set_mode(ThemeMode.LIGHT)
    ThemeManager.instance().apply_app_palette(app)
    demo = _Demo()
    demo.resize(420, 360)
    demo.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
