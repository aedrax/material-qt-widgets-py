"""Demo: ``python -m material_qt.widgets.dialog.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from ...theme.theme_manager import ThemeManager, ThemeMode
from ..button import MdFilledButton
from .dialog import MdDialog


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Dialog")
        self.resize(560, 420)
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(12)

        open_btn = MdFilledButton("Open dialog")
        open_btn.clicked.connect(self._open)
        root.addWidget(open_btn)
        self._status = QLabel("(no result)")
        root.addWidget(self._status)

        toggle = MdFilledButton("Toggle light / dark")
        toggle.clicked.connect(self._toggle)
        root.addWidget(toggle)
        root.addStretch(1)
        self._dark = False

    def _open(self) -> None:
        dlg = MdDialog(
            self,
            icon="delete",
            headline="Delete file?",
            supporting_text="This will permanently remove the file. This action "
            "cannot be undone.",
        )
        dlg.add_action("Cancel", accept=False)
        dlg.add_action("Delete", accept=True)
        dlg.accepted.connect(lambda: self._status.setText("Deleted"))
        dlg.rejected.connect(lambda: self._status.setText("Cancelled"))
        dlg.open()

    def _toggle(self) -> None:
        self._dark = not self._dark
        ThemeManager.instance().set_mode(
            ThemeMode.DARK if self._dark else ThemeMode.LIGHT
        )


def main() -> int:
    app = QApplication(sys.argv)
    w = Demo()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
