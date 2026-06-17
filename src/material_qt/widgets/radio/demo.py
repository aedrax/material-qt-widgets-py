"""Demo: ``python -m material_qt.widgets.radio.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...theme.theme_manager import ThemeManager, ThemeMode
from .radio import MdRadio


def _row(label: str, radio: MdRadio) -> QWidget:
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(radio)
    lay.addWidget(QLabel(label))
    lay.addStretch(1)
    return w


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Radio")
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)

        # Group (mutually exclusive via autoExclusive within this parent).
        group = QWidget()
        gl = QVBoxLayout(group)
        gl.setContentsMargins(0, 0, 0, 0)
        # Radios wrapped in row widgets land in different parents, so use a
        # QButtonGroup to enforce single-selection exclusivity.
        self._group = QButtonGroup(self)
        for i, name in enumerate(("Apple", "Banana", "Cherry")):
            r = MdRadio(checked=(i == 0))
            self._group.addButton(r)
            gl.addWidget(_row(name, r))
        root.addWidget(QLabel("Single selection group:"))
        root.addWidget(group)

        disabled = MdRadio(checked=True)
        disabled.setEnabled(False)
        root.addWidget(_row("Disabled (selected)", disabled))

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
    w.resize(360, 320)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
