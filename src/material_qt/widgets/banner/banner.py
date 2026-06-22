"""Material 3 banner for QtWidgets.

Ports the Material 3 banner (``MaterialBanner``): a non-modal, inline message on a
``surface`` container with an optional leading icon, ``body-medium``
``on-surface`` supporting text, a trailing row of text-button actions, and a
``outline-variant`` divider along the bottom edge. Banners stay until dismissed
by an action. Each action returns its :class:`MdTextButton`; convenience signals
are not used — connect the returned button's ``clicked``.
"""

from __future__ import annotations

from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.shape import ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..button import MdTextButton
from ..divider import MdDivider
from ..icon.icon import MdIcon

_PAD = 16


class MdBanner(MaterialWidgetMixin, QWidget):
    """An inline, non-modal banner with text and actions."""

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        icon: str = "",
        elevation: int = 0,
        background_role: ColorRole = ColorRole.SURFACE,
        divider_role: ColorRole = ColorRole.OUTLINE_VARIANT,
    ) -> None:
        super().__init__(parent)
        self._background_role = background_role
        self._divider_role = divider_role
        self._init_material(
            shape=ShapeScale.NONE,
            ripple=False,
            focus_ring=False,
            elevation=elevation,
            surface_role=background_role,
        )
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        body = QHBoxLayout()
        body.setContentsMargins(_PAD, _PAD, _PAD, _PAD)
        body.setSpacing(_PAD)

        if icon:
            ic = MdIcon(icon, color_role=ColorRole.PRIMARY)
            ic.set_size(24)
            body.addWidget(ic, 0)

        self._text = QLabel(text)
        self._text.setWordWrap(True)
        self._text.setFont(font_for_role(TypescaleRole.BODY_MEDIUM))
        body.addWidget(self._text, 1)

        self._actions = QHBoxLayout()
        self._actions.setSpacing(8)
        body.addLayout(self._actions, 0)

        outer.addLayout(body)
        self._divider = MdDivider()
        self._divider._color_role = self._divider_role
        outer.addWidget(self._divider)

        self._restyle()
        ThemeManager.instance().themeChanged.connect(self._restyle)

    def _restyle(self) -> None:
        c = ThemeManager.instance().color(ColorRole.ON_SURFACE).name()
        self._text.setStyleSheet(f"color: {c};")

    # -- theme / elevation -------------------------------------------------
    # ``elevation`` and :meth:`set_elevation` come from MaterialWidgetMixin.

    @property
    def elevation(self) -> int:
        """Banner elevation level (Flutter ``elevation``)."""
        return int(self._elevation)

    @property
    def background_role(self) -> ColorRole:
        """Container fill color role (Flutter ``backgroundColor``)."""
        return self._background_role

    def set_background_role(self, role: ColorRole) -> None:
        self._background_role = role
        self._surface_role = role
        self.update()

    @property
    def divider_role(self) -> ColorRole:
        """Bottom-edge divider color role (Flutter ``dividerColor``)."""
        return self._divider_role

    def set_divider_role(self, role: ColorRole) -> None:
        self._divider_role = role
        self._divider._color_role = role
        self._divider.update()

    def add_action(self, text: str) -> MdTextButton:
        """Append a trailing text-button action and return it."""
        btn = MdTextButton(text)
        self._actions.addWidget(btn)
        return btn

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


__all__ = ["MdBanner"]
