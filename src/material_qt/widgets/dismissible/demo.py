"""Demo: ``python -m material_qt.widgets.dismissible.demo``."""

from __future__ import annotations

import sys

from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...theme.theme_manager import ThemeManager, ThemeMode
from ...tokens.color import ColorRole
from ..icon import MdIcon
from ..list import MdListItem
from .dismissible import DismissDirection, MdDismissible


class _Background(QWidget):
    """A flat themed panel with an edge icon, revealed behind a swipe."""

    def __init__(self, role: ColorRole, on_role: ColorRole, icon: str, align_end: bool) -> None:
        super().__init__()
        self._role = role
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)
        glyph = MdIcon(icon, color_role=on_role)
        if align_end:
            lay.addStretch(1)
            lay.addWidget(glyph)
        else:
            lay.addWidget(glyph)
            lay.addStretch(1)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.fillRect(self.rect(), ThemeManager.instance().color(self._role))


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Material Qt — Dismissible")
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        self._col = QVBoxLayout()
        self._col.setSpacing(0)
        root.addLayout(self._col)

        for name in ["Archive me", "Swipe to delete", "Try left or right", "Bye"]:
            item = MdListItem(name, leading=MdIcon("mail"), interactive=False)
            d = MdDismissible(
                item,
                direction=DismissDirection.HORIZONTAL,
                background=_Background(
                    ColorRole.PRIMARY_CONTAINER, ColorRole.ON_PRIMARY_CONTAINER,
                    "archive", align_end=False),
                secondary_background=_Background(
                    ColorRole.ERROR_CONTAINER, ColorRole.ON_ERROR_CONTAINER,
                    "delete", align_end=True),
            )
            d.dismissed.connect(lambda direction, w=name: print(f"dismissed {w!r}: {direction}"))
            self._col.addWidget(d)

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
    w.resize(440, 360)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
