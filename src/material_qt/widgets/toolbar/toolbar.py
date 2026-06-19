"""Material 3 toolbar (Expressive) for QtWidgets.

Ports the Material 3 Expressive toolbar: a floating or docked bar that holds a
row of action icon buttons (and optionally other controls). The floating variant
is a fully-rounded ``surface-container`` pill with level-3 elevation; the docked
variant is a flatter, less-rounded bar on ``surface-container``.

Deferred (scaffold): pairing with a FAB and the vibrant/standard color variants.
"""

from __future__ import annotations

from enum import Enum

from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QHBoxLayout, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...tokens.shape import CornerRadii, ShapeScale
from ..iconbutton import MdIconButton

_HEIGHT = 64
_PAD = 8


class ToolbarVariant(Enum):
    FLOATING = "floating"
    DOCKED = "docked"


class MdToolbar(MaterialWidgetMixin, QWidget):
    """A Material 3 floating or docked toolbar of icon buttons."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        variant: ToolbarVariant = ToolbarVariant.FLOATING,
    ) -> None:
        super().__init__(parent)
        self._variant = variant
        floating = variant is ToolbarVariant.FLOATING
        self._init_material(
            shape=CornerRadii.uniform(_HEIGHT / 2.0) if floating else ShapeScale.LARGE,
            elevation=ElevationLevel.LEVEL3 if floating else ElevationLevel.LEVEL0,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE_CONTAINER,
        )
        self.setFixedHeight(_HEIGHT)
        self._lay = QHBoxLayout(self)
        self._lay.setContentsMargins(_PAD, _PAD, _PAD, _PAD)
        self._lay.setSpacing(4)
        self._buttons: list[MdIconButton] = []

    def add_action(self, icon: str = "", *, toggle: bool = False) -> MdIconButton:
        """Append an action icon button and return it."""
        btn = MdIconButton(icon, toggle=toggle)
        self._lay.addWidget(btn)
        self._buttons.append(btn)
        return btn

    def count(self) -> int:
        return len(self._buttons)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


__all__ = ["MdToolbar", "ToolbarVariant"]
