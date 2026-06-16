"""Self-contained demo for :class:`MdDivider`.

Run with::

    python -m material_qt.widgets.divider.demo
"""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...theme.theme_manager import ThemeManager, ThemeMode
from .divider import MdDivider


def _row(label: str, **kwargs) -> QWidget:
    """A labeled horizontal divider example."""
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 8, 0, 8)
    layout.setSpacing(8)

    layout.addWidget(QLabel(label))
    divider = MdDivider()
    for key, value in kwargs.items():
        setattr(divider, key, value)
    layout.addWidget(divider)
    return container


def build_demo() -> QWidget:
    root = QWidget()
    root.setWindowTitle("MdDivider demo")
    outer = QVBoxLayout(root)
    outer.setContentsMargins(24, 24, 24, 24)
    outer.setSpacing(4)

    outer.addWidget(QLabel("<b>Horizontal dividers</b>"))
    outer.addWidget(_row("full width"))
    outer.addWidget(_row("inset (both sides)", inset=True))
    outer.addWidget(_row("inset-start (leading)", inset_start=True))
    outer.addWidget(_row("inset-end (trailing)", inset_end=True))

    outer.addSpacing(16)
    outer.addWidget(QLabel("<b>Vertical divider</b>"))
    vrow = QWidget()
    vlayout = QHBoxLayout(vrow)
    vlayout.setContentsMargins(0, 0, 0, 0)
    vlayout.setSpacing(16)
    vlayout.addWidget(QLabel("left"))
    vdiv = MdDivider(orientation=Qt.Orientation.Vertical)
    vdiv.setFixedHeight(48)
    vlayout.addWidget(vdiv)
    vlayout.addWidget(QLabel("right"))
    vlayout.addStretch(1)
    outer.addWidget(vrow)

    outer.addStretch(1)

    toggle = QPushButton("Toggle light/dark")
    toggle.clicked.connect(lambda: ThemeManager.instance().toggle_light_dark())
    outer.addWidget(toggle)

    return root


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    ThemeManager.instance().set_mode(ThemeMode.LIGHT)
    ThemeManager.instance().apply_app_palette(app)
    window = build_demo()
    window.resize(420, 480)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
