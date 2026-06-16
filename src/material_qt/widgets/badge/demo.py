"""Self-contained MdBadge demo.

Run with::

    python -m material_qt.widgets.badge.demo

Shows dot and numeric badges attached to icon/button placeholders, plus a
light/dark theme toggle.
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

from material_qt.theme.theme_manager import ThemeManager
from material_qt.widgets.badge import MdBadge


def _anchor(text: str) -> QWidget:
    """A simple square icon/button placeholder to host a badge."""
    host = QPushButton(text)
    host.setFixedSize(48, 48)
    return host


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    ThemeManager.instance().apply_app_palette(app)

    window = QWidget()
    window.setWindowTitle("MdBadge demo")
    root = QVBoxLayout(window)
    root.setContentsMargins(32, 32, 32, 32)
    root.setSpacing(24)

    row = QHBoxLayout()
    row.setSpacing(32)

    # Dot badge (no value).
    dot_host = _anchor("A")
    MdBadge().attach(dot_host)
    row.addWidget(dot_host)

    # Small numeric badge.
    small_host = _anchor("B")
    MdBadge("8").attach(small_host)
    row.addWidget(small_host)

    # Larger numeric badge.
    large_host = _anchor("C")
    MdBadge("99+").attach(large_host)
    row.addWidget(large_host)

    row.addStretch(1)
    root.addLayout(row)

    toggle = QPushButton("Toggle light/dark")
    toggle.clicked.connect(lambda: ThemeManager.instance().toggle_light_dark())
    toggle.clicked.connect(lambda: ThemeManager.instance().apply_app_palette(app))
    root.addWidget(toggle, alignment=Qt.AlignmentFlag.AlignLeft)

    hint = QLabel("Dot, '8', and '99+' badges anchored to button corners.")
    root.addWidget(hint)

    window.resize(360, 200)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
