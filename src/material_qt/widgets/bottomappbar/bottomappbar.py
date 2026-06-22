"""Material 3 bottom app bar for QtWidgets.

Ports Flutter's ``BottomAppBar`` (``bottom_app_bar.dart``): a bar pinned to the
bottom of a screen that hosts a row of leading action icon buttons and,
optionally, a trailing :class:`MdFab`. When ``notch`` is enabled and a FAB is
hosted, the bar's top edge is cradled with a rounded notch around the FAB (cf.
Flutter's ``NotchedShape`` / ``notchMargin``).

Defaults follow the M3 token block in ``bottom_app_bar.dart``: height 80,
container ``surface-container``, elevation level 3. The content padding is the
M3 default ``EdgeInsets.symmetric(vertical: 12, horizontal: 16)``.

Theme-role colors only: the background is the ``surface-container`` role (cf.
Flutter ``BottomAppBar.color`` defaulting to ``ColorScheme.surfaceContainer``);
raw-``QColor`` overrides are intentionally not exposed, matching the package
convention. Action buttons expose their own ``clicked`` signal — no
callback-to-signal shim is needed.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QPainter, QPainterPath
from PySide6.QtWidgets import QHBoxLayout, QWidget

from ...core.material_widget import MaterialWidgetMixin
from ...core.shape_util import rounded_path
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...tokens.shape import ShapeScale
from ...theme.theme_manager import ThemeManager
from ..fab import MdFab
from ..iconbutton import MdIconButton

_HEIGHT = 80
_PAD_H = 16
_PAD_V = 12
_NOTCH_MARGIN = 4.0


class MdBottomAppBar(MaterialWidgetMixin, QWidget):
    """A Material 3 bottom app bar.

    Hosts leading action icon buttons (:meth:`add_action`) and an optional
    trailing :class:`MdFab` (:meth:`set_fab`). With ``notch=True`` the top edge
    is cradled around the FAB.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        notch: bool = False,
        height: int = _HEIGHT,
        elevation: ElevationLevel | int = ElevationLevel.LEVEL3,
    ) -> None:
        super().__init__(parent)
        self._notch = notch
        self._fab: MdFab | None = None
        self._buttons: list[MdIconButton] = []

        self._init_material(
            shape=ShapeScale.NONE,
            elevation=elevation,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE_CONTAINER,
        )
        self.setFixedHeight(int(height))

        # Leading actions live in the layout, left-aligned; a trailing stretch
        # keeps the trailing edge clear for the manually-positioned FAB.
        self._lay = QHBoxLayout(self)
        self._lay.setContentsMargins(_PAD_H, _PAD_V, _PAD_H, _PAD_V)
        self._lay.setSpacing(4)
        self._lay.addStretch(1)

    # -- content -----------------------------------------------------------

    def add_action(self, icon: str = "", *, toggle: bool = False) -> MdIconButton:
        """Append a leading action icon button and return it."""
        button = MdIconButton(icon, toggle=toggle)
        # Insert before the trailing stretch (which is always the last item).
        self._lay.insertWidget(self._lay.count() - 1, button)
        self._buttons.append(button)
        return button

    def set_fab(self, fab: MdFab | None) -> None:
        """Set (or clear) the trailing FAB, end-cradled by the notch.

        Mirrors Flutter's ``FloatingActionButtonLocation.endContained`` pairing.

        Unlike Flutter — where the ``Scaffold`` owns the FAB as a sibling and
        feeds its geometry to the bar — this widget hosts the FAB itself and
        positions it manually (trailing, top-aligned) so its lower half nests
        into the notch entirely within the bar's bounds.
        """
        if self._fab is not None:
            self._fab.setParent(None)
        self._fab = fab
        if fab is not None:
            fab.setParent(self)
            fab.show()
            self._position_fab()
        self.update()

    def _position_fab(self) -> None:
        """Place the FAB trailing and top-aligned within the bar's bounds."""
        fab = self._fab
        if fab is None:
            return
        fab.adjustSize()
        x = self.width() - _PAD_H - fab.width()
        # Top-aligned: the FAB sits in the top strip so the notch cradles its
        # lower half. Clamp to >= 0 so it never overhangs (Qt would clip it).
        y = max(0, _PAD_V - fab.height() // 4)
        fab.move(x, y)

    @property
    def fab(self) -> MdFab | None:
        return self._fab

    @property
    def notch(self) -> bool:
        return self._notch

    def set_notch(self, enabled: bool) -> None:
        self._notch = enabled
        self.update()

    def count(self) -> int:
        """Number of leading action buttons."""
        return len(self._buttons)

    # -- geometry ----------------------------------------------------------

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._position_fab()

    # -- painting ----------------------------------------------------------

    def _surface_path(self) -> QPainterPath:
        rect = QRectF(self.rect())
        path = rounded_path(rect, self.radii)
        if not (self._notch and self._fab is not None):
            return path
        # Subtract a rounded notch on the top edge centered on the FAB; the FAB's
        # lower half nests into it. center_x is derived from the bar width (the
        # same basis _position_fab uses), so it is correct even before the first
        # layout/relayout pass.
        fab = self._fab
        center_x = self.width() - _PAD_H - fab.width() / 2.0
        radius = fab.width() / 2.0 + _NOTCH_MARGIN
        notch = QPainterPath()
        notch.addEllipse(QPointF(center_x, rect.top()), radius, radius)
        return path.subtracted(notch)

    def paintEvent(self, event) -> None:  # noqa: N802
        # Keep the FAB tracking the current width even if no resizeEvent fired
        # (e.g. an unshown widget resized before grab()).
        self._position_fab()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        color = ThemeManager.instance().color(self._surface_role)
        painter.fillPath(self._surface_path(), color)


__all__ = ["MdBottomAppBar"]
