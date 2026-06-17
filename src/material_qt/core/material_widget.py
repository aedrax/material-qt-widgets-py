"""MaterialWidgetMixin: wires theme, shape, typography, interaction, ripple,
focus ring, and elevation onto a QWidget; plus a concrete MaterialWidget base.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget

from ..tokens.color import ColorRole
from ..tokens.elevation import ElevationLevel
from ..tokens.shape import CornerRadii, ShapeScale
from ..tokens.typography import TypescaleRole
from ..theme.theme_manager import ThemeManager
from .elevation import ElevationPainter, apply_elevation
from .focus_ring import FocusRingController
from .interaction_state import InteractionState
from .ripple import RippleController
from .shape_util import rounded_path
from .state_layer import StateLayerPainter
from .typography_util import apply as apply_typography


class MaterialWidgetMixin:
    """Mixin adding Material foundation behavior to a ``QWidget`` subclass.

    Call :meth:`_init_material` from ``__init__`` after the QWidget base is
    constructed. Wires:

    * theme reactivity (``themeChanged`` -> ``update``);
    * an :class:`InteractionState` reflecting enable/hover/press/focus;
    * a shape (:class:`CornerRadii`) used to clip the surface, ripple and ring;
    * an optional :class:`RippleController` and :class:`FocusRingController`;
    * elevation via :func:`apply_elevation`;
    * an optional default typescale font.
    """

    def _init_material(
        self,
        *,
        shape: ShapeScale | CornerRadii | None = ShapeScale.NONE,
        typescale: TypescaleRole | None = None,
        elevation: ElevationLevel | int = ElevationLevel.LEVEL0,
        ripple: bool = True,
        focus_ring: bool = True,
        ripple_role: ColorRole = ColorRole.ON_SURFACE,
        surface_role: ColorRole = ColorRole.SURFACE,
    ) -> None:
        widget = self._as_widget()
        widget.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        if isinstance(shape, CornerRadii):
            self._radii = shape
        elif shape is None:
            self._radii = CornerRadii.uniform(0.0)
        else:
            self._radii = CornerRadii.from_scale(shape)

        self._surface_role = surface_role
        self._elevation = ElevationLevel(int(elevation))
        self._elevation_painter = ElevationPainter()

        self.interaction = InteractionState(widget)
        self.interaction.changed.connect(widget.update)

        self._state_painter = StateLayerPainter(color_role=ripple_role)

        self.ripple: RippleController | None = None
        if ripple:
            self.ripple = RippleController(widget, color_role=ripple_role)
            self.ripple.set_radii(self._radii)

        self.focus_ring: FocusRingController | None = None
        if focus_ring:
            self.focus_ring = FocusRingController(widget)
            self.focus_ring.set_radii(self._radii)
            if widget.focusPolicy() == Qt.FocusPolicy.NoFocus:
                widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        if typescale is not None:
            apply_typography(widget, typescale)

        # Theme reactivity.
        ThemeManager.instance().themeChanged.connect(widget.update)

        # Elevation always uses a QGraphicsDropShadowEffect — a real soft shadow
        # that extends beyond the widget bounds. It composites correctly over the
        # ripple/focus child overlays (verified), so it is not disabled for ripple
        # widgets. The stroke-based ElevationPainter produced a hard, clipped edge.
        self._apply_elevation_effect = True
        apply_elevation(widget, self._elevation)

    # -- helpers -----------------------------------------------------------

    def _as_widget(self) -> QWidget:
        assert isinstance(self, QWidget), "MaterialWidgetMixin requires a QWidget"
        return self

    @property
    def radii(self) -> CornerRadii:
        return self._radii

    def set_radii(self, radii: CornerRadii) -> None:
        self._radii = radii
        if self.ripple is not None:
            self.ripple.set_radii(radii)
        if self.focus_ring is not None:
            self.focus_ring.set_radii(radii)
        self._as_widget().update()

    def set_elevation(self, level: ElevationLevel | int) -> None:
        self._elevation = ElevationLevel(int(level))
        if self._apply_elevation_effect:
            apply_elevation(self._as_widget(), self._elevation)
        self._as_widget().update()

    def clip_path(self):
        widget = self._as_widget()
        return rounded_path(QRectF(widget.rect()), self._radii)

    def paint_material_surface(self, painter: QPainter) -> None:
        """Paint the themed surface fill clipped to the widget's shape.

        Subclasses can call this from ``paintEvent`` to draw the base surface;
        the ripple/state layers are painted by their own overlays on top.
        """
        widget = self._as_widget()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        path = rounded_path(QRectF(widget.rect()), self._radii)
        if self._elevation != ElevationLevel.LEVEL0 and not self._apply_elevation_effect:
            self._elevation_painter.paint(painter, path, self._elevation)
        color = ThemeManager.instance().color(self._surface_role)
        painter.fillPath(path, color)


class MaterialWidget(MaterialWidgetMixin, QWidget):
    """Concrete Material surface widget.

    Paints a themed, shaped surface and hosts ripple + focus-ring overlays.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        shape: ShapeScale | CornerRadii | None = ShapeScale.MEDIUM,
        typescale: TypescaleRole | None = None,
        elevation: ElevationLevel | int = ElevationLevel.LEVEL0,
        ripple: bool = True,
        focus_ring: bool = True,
        ripple_role: ColorRole = ColorRole.ON_SURFACE,
        surface_role: ColorRole = ColorRole.SURFACE,
    ) -> None:
        super().__init__(parent)
        self._init_material(
            shape=shape,
            typescale=typescale,
            elevation=elevation,
            ripple=ripple,
            focus_ring=focus_ring,
            ripple_role=ripple_role,
            surface_role=surface_role,
        )

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


__all__ = ["MaterialWidget", "MaterialWidgetMixin"]
