"""Material 3 item (labs) for QtWidgets.

Ports Material Web's ``labs/item`` — a non-interactive content layout primitive
with five slots: leading (start), a text block of headline (``body-large``,
``on-surface``) + supporting text (``body-medium``, ``on-surface-variant``),
trailing supporting text (``label-small``), and trailing (end). It is the layout
building block the future list-item composes. Text colors track the theme.
"""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager

_H_PAD = 16
_V_PAD = 8
_GAP = 16
_TEXT_GAP = 2


class _ThemedLabel(QLabel):
    """A QLabel whose text color follows a theme role."""

    def __init__(self, text: str, role: ColorRole, typescale: TypescaleRole) -> None:
        super().__init__(text)
        self._role = role
        self.setFont(font_for_role(typescale))
        self.setWordWrap(True)
        ThemeManager.instance().themeChanged.connect(self._apply_color)
        self._apply_color()

    def _apply_color(self) -> None:
        color = ThemeManager.instance().color(self._role)
        self.setStyleSheet(f"color: {color.name()};")


class MdItem(QWidget):
    """A Material 3 item: leading / headline + supporting / trailing slots."""

    def __init__(
        self,
        headline: str = "",
        parent: QWidget | None = None,
        *,
        supporting_text: str = "",
        trailing_supporting_text: str = "",
        leading: QWidget | None = None,
        trailing: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._row = QHBoxLayout(self)
        self._row.setContentsMargins(_H_PAD, _V_PAD, _H_PAD, _V_PAD)
        self._row.setSpacing(_GAP)

        self._leading: QWidget | None = None
        self._trailing: QWidget | None = None

        # Leading slot.
        self._leading_holder = QWidget()
        self._leading_layout = QHBoxLayout(self._leading_holder)
        self._leading_layout.setContentsMargins(0, 0, 0, 0)
        self._row.addWidget(self._leading_holder)
        self._leading_holder.hide()

        # Text block.
        text_box = QVBoxLayout()
        text_box.setContentsMargins(0, 0, 0, 0)
        text_box.setSpacing(_TEXT_GAP)
        self._headline = _ThemedLabel(
            headline, ColorRole.ON_SURFACE, TypescaleRole.BODY_LARGE
        )
        self._supporting = _ThemedLabel(
            supporting_text, ColorRole.ON_SURFACE_VARIANT, TypescaleRole.BODY_MEDIUM
        )
        text_box.addWidget(self._headline)
        text_box.addWidget(self._supporting)
        self._supporting.setVisible(bool(supporting_text))
        self._row.addLayout(text_box, 1)

        # Trailing supporting text.
        self._trailing_supporting = _ThemedLabel(
            trailing_supporting_text,
            ColorRole.ON_SURFACE_VARIANT,
            TypescaleRole.LABEL_SMALL,
        )
        self._trailing_supporting.setVisible(bool(trailing_supporting_text))
        self._row.addWidget(self._trailing_supporting)

        # Trailing slot.
        self._trailing_holder = QWidget()
        self._trailing_layout = QHBoxLayout(self._trailing_holder)
        self._trailing_layout.setContentsMargins(0, 0, 0, 0)
        self._row.addWidget(self._trailing_holder)
        self._trailing_holder.hide()

        if leading is not None:
            self.set_leading(leading)
        if trailing is not None:
            self.set_trailing(trailing)

    # -- slots -------------------------------------------------------------

    def set_headline(self, text: str) -> None:
        self._headline.setText(text)

    def set_supporting_text(self, text: str) -> None:
        self._supporting.setText(text)
        self._supporting.setVisible(bool(text))

    def set_trailing_supporting_text(self, text: str) -> None:
        self._trailing_supporting.setText(text)
        self._trailing_supporting.setVisible(bool(text))

    def set_leading(self, widget: QWidget | None) -> None:
        self._leading = self._swap(self._leading_layout, self._leading_holder, widget)

    def set_trailing(self, widget: QWidget | None) -> None:
        self._trailing = self._swap(
            self._trailing_layout, self._trailing_holder, widget
        )

    @staticmethod
    def _swap(layout: QHBoxLayout, holder: QWidget, widget: QWidget | None) -> QWidget | None:
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
        if widget is None:
            holder.hide()
            return None
        layout.addWidget(widget)
        holder.show()
        return widget


__all__ = ["MdItem"]
