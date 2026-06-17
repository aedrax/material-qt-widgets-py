"""Demo: ``python -m material_qt.widgets.field.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...theme.theme_manager import ThemeManager, ThemeMode
from .field import FieldVariant, MdField


def _field(variant: FieldVariant, label: str, **kw) -> MdField:
    field = MdField(variant=variant, label=label, **kw)
    edit = QLineEdit()
    edit.setFrame(False)
    edit.setStyleSheet("background: transparent; border: none;")
    edit.textChanged.connect(lambda t: field.set_populated(bool(t)))
    field.set_content(edit)
    return field


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Field")
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(20)
        root.addWidget(_field(FieldVariant.FILLED, "Filled label",
                              supporting_text="Supporting text"))
        root.addWidget(_field(FieldVariant.OUTLINED, "Outlined label"))
        root.addWidget(_field(FieldVariant.OUTLINED, "Error field",
                              supporting_text="Required", error=True))
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
