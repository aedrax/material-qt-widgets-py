"""Demo: ``python -m material_qt.widgets.list.demo``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

from ...theme.theme_manager import ThemeManager, ThemeMode
from ..icon import MdIcon
from .list import MdList, MdListItem


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — List")
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)

        lst = MdList()
        lst.add_item(MdListItem("Inbox", supporting_text="3 new messages",
                                leading=MdIcon("inbox"),
                                trailing_supporting_text="3"))
        lst.add_item(MdListItem("Starred", leading=MdIcon("star"),
                                trailing=MdIcon("chevron_right")), divider=True)
        lst.add_item(MdListItem("Sent", leading=MdIcon("send")), divider=True)
        lst.add_item(MdListItem("Drafts", supporting_text="2 drafts",
                                leading=MdIcon("drafts")), divider=True)
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
    w.resize(420, 380)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
