"""Material draggable, resizable bottom sheet for QtWidgets.

Ports Flutter's ``DraggableScrollableSheet`` (``widgets/draggable_scrollable_sheet.dart``)
— a non-modal sheet anchored to the bottom of its parent, sized as a fraction of
the parent's height, that the user can drag to resize between ``min_size`` and
``max_size`` and that hosts a scrollable content area.

Like the other ports here it **owns its state**: the current size is a fraction
exposed via :attr:`size` / :meth:`set_size` / :meth:`animate_to`, and every
change (drag, wheel, animation tick) emits :attr:`sizeChanged`. The resize math
lives in two pure, unit-testable seams: :func:`clamp_size` and
:func:`nearest_snap`; the wheel-vs-scroll decision is the pure
:func:`couple_wheel`.

Interactions:
- **Drag the handle strip** to resize freely; on release it snaps to the nearest
  snap size (``snap=True``).
- **Wheel over the content** couples to the sheet (Flutter's drag/scroll
  coupling): wheeling toward the bottom grows the sheet until ``max_size`` then
  scrolls; wheeling toward the top scrolls until the content is at its top, then
  shrinks the sheet. Wheel resize lands free (no snap).

Deferred (vs Flutter): mouse/touch finger-drag coupling over the content (only
the handle drags and the wheel couples), snap-after-wheel (only handle-release
snaps), and ``expand``/secondary-animation niceties.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, Property, QRectF, Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget
from shiboken6 import isValid

from ...core.material_widget import MaterialWidgetMixin
from ...core.motion import MOTION_ENABLED, animate
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...tokens.motion import Duration, Easing
from ...tokens.shape import CornerRadii
from ...theme.theme_manager import ThemeManager
from ..scrollbar import use_material_scrollbars

_RADIUS = 28
_HANDLE_STRIP = 28  # reserved top band that draws + drags the grabber
_HANDLE_W = 32
_HANDLE_H = 4
_PAD = 16
_WHEEL_STEP = 0.08  # sheet fraction per wheel notch when coupling
_EPS = 1e-3


def clamp_size(size: float, min_size: float, max_size: float) -> float:
    """Clamp a size fraction into ``[min_size, max_size]``."""
    return max(min_size, min(float(size), max_size))


def nearest_snap(size: float, snaps: list[float]) -> float:
    """Return the snap fraction closest to ``size`` (``snaps`` need not be sorted)."""
    if not snaps:
        return size
    return min(snaps, key=lambda s: abs(s - size))


def couple_wheel(
    angle_y: float, at_top: bool, size: float, min_size: float, max_size: float
) -> str:
    """Decide what a content wheel event does: ``"grow"``/``"shrink"``/``"scroll"``.

    ``angle_y`` is Qt's ``angleDelta().y()`` (>0 = toward the content top, <0 =
    toward the bottom). Mirrors Flutter's finger coupling: a downward wheel
    (toward the bottom) grows the sheet until ``max_size`` then scrolls; an
    upward wheel scrolls until the content is at its top, then shrinks the sheet.
    """
    if angle_y < 0:  # toward the bottom
        if size < max_size - _EPS:
            return "grow"
        return "scroll"
    if angle_y > 0:  # toward the top
        if not at_top:
            return "scroll"
        if size > min_size + _EPS:
            return "shrink"
        return "scroll"
    return "scroll"


class MdDraggableScrollableSheet(MaterialWidgetMixin, QWidget):
    """A bottom-anchored sheet the user can drag to resize, hosting scroll content."""

    sizeChanged = Signal(float)

    def __init__(
        self,
        parent: QWidget,
        *,
        initial_size: float = 0.5,
        min_size: float = 0.25,
        max_size: float = 1.0,
        snap: bool = True,
        snap_sizes: list[float] | None = None,
        show_handle: bool = True,
    ) -> None:
        super().__init__(parent)
        self._min = float(min_size)
        self._max = float(max_size)
        self._initial = clamp_size(initial_size, self._min, self._max)
        self._frac = self._initial
        self._snap = bool(snap)
        self._show_handle = show_handle
        self._snaps: list[float] = sorted({self._min, self._max, *(snap_sizes or [])})
        # handle-drag bookkeeping
        self._dragging = False
        self._press_global_y = 0.0
        self._press_frac = self._frac
        self._snap_anim = None

        self._init_material(
            shape=CornerRadii(_RADIUS, _RADIUS, 0, 0),
            elevation=ElevationLevel.LEVEL1,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE_CONTAINER_LOW,
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, _HANDLE_STRIP, 0, 0)
        lay.setSpacing(0)
        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.viewport().setAutoFillBackground(False)
        self._scroll.setStyleSheet("background: transparent;")
        self._inner = QWidget()
        self._inner.setAutoFillBackground(False)
        self._inner_lay = QVBoxLayout(self._inner)
        self._inner_lay.setContentsMargins(_PAD, 8, _PAD, _PAD)
        self._inner_lay.setSpacing(8)
        self._inner_lay.addStretch(1)
        self._scroll.setWidget(self._inner)
        use_material_scrollbars(self._scroll)
        lay.addWidget(self._scroll)

        self._scroll.viewport().installEventFilter(self)
        parent.installEventFilter(self)
        ThemeManager.instance().themeChanged.connect(self.update)
        self._reposition()

    # -- content -----------------------------------------------------------

    def add_content(self, widget: QWidget) -> None:
        self._inner_lay.insertWidget(self._inner_lay.count() - 1, widget)

    # -- controller API ----------------------------------------------------

    @property
    def size_fraction(self) -> float:
        """The current sheet size as a fraction of the parent height.

        (Flutter's ``DraggableScrollableController.size``; named ``size_fraction``
        here to avoid clashing with :meth:`QWidget.size`.)
        """
        return self._frac

    def set_size(self, fraction: float, *, animated: bool = False) -> None:
        if animated:
            self.animate_to(fraction)
        else:
            self.set_frac(fraction)

    def animate_to(self, fraction: float) -> None:
        """Animate the sheet to ``fraction`` (clamped), emitting :attr:`sizeChanged`."""
        target = clamp_size(fraction, self._min, self._max)
        self._stop_snap_anim()
        if not MOTION_ENABLED:
            self.set_frac(target)
            return
        self._snap_anim = animate(self, b"frac", target, duration=Duration.MEDIUM2,
                                  easing=Easing.EMPHASIZED)

    def _stop_snap_anim(self) -> None:
        # A running snap would keep writing `frac` under a new drag/wheel/
        # animate_to, fighting it for the sheet.
        anim = self._snap_anim
        self._snap_anim = None
        if anim is not None and isValid(anim):
            anim.stop()  # DeleteWhenStopped: the C++ object dies here

    def reset(self) -> None:
        self.animate_to(self._initial)

    # -- frac property (drives geometry; animatable) -----------------------

    def get_frac(self) -> float:
        return self._frac

    def set_frac(self, value: float) -> None:
        self._frac = clamp_size(value, self._min, self._max)
        self._reposition()
        self.sizeChanged.emit(self._frac)

    frac = Property(float, get_frac, set_frac)

    # -- geometry ----------------------------------------------------------

    def _reposition(self) -> None:
        """Set geometry from the current frac. Does NOT emit (parent-resize safe)."""
        parent = self.parentWidget()
        if parent is None:
            return
        ph, pw = parent.height(), parent.width()
        h = max(_HANDLE_STRIP + _HANDLE_H, int(ph * self._frac))
        self.setGeometry(0, ph - h, pw, h)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self.raise_()
        self._reposition()

    # -- handle drag -------------------------------------------------------

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if (event.button() == Qt.MouseButton.LeftButton
                and event.position().y() <= _HANDLE_STRIP):
            self._stop_snap_anim()
            self._dragging = True
            self._press_global_y = event.globalPosition().y()
            self._press_frac = self._frac
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if not self._dragging:
            super().mouseMoveEvent(event)
            return
        parent = self.parentWidget()
        ph = parent.height() if parent else self.height()
        # Dragging up (smaller global y) grows the sheet.
        dy = self._press_global_y - event.globalPosition().y()
        self.set_frac(self._press_frac + dy / max(1, ph))
        event.accept()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if self._dragging:
            self._dragging = False
            if self._snap:
                self.animate_to(nearest_snap(self._frac, self._snaps))
            event.accept()
            return
        super().mouseReleaseEvent(event)

    # -- wheel coupling + parent resize ------------------------------------

    def eventFilter(self, obj, event) -> bool:  # noqa: N802
        if obj is self.parentWidget() and event.type() == QEvent.Type.Resize:
            self._reposition()
            return False
        if obj is self._scroll.viewport() and event.type() == QEvent.Type.Wheel:
            return self._handle_wheel(event)
        return False

    def _handle_wheel(self, event) -> bool:
        angle = event.angleDelta().y()
        vbar = self._scroll.verticalScrollBar()
        at_top = vbar.value() <= vbar.minimum()
        mode = couple_wheel(angle, at_top, self._frac, self._min, self._max)
        if mode == "scroll":
            return False
        self._stop_snap_anim()
        step = (abs(angle) / 120.0) * _WHEEL_STEP
        self.set_frac(self._frac + step if mode == "grow" else self._frac - step)
        return True

    # -- paint -------------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.paint_material_surface(painter)
        if not self._show_handle:
            return
        handle = ThemeManager.instance().color(ColorRole.ON_SURFACE_VARIANT)
        handle.setAlphaF(0.4)
        painter.setBrush(handle)
        painter.setPen(Qt.PenStyle.NoPen)
        cx = self.width() / 2.0
        painter.drawRoundedRect(
            QRectF(cx - _HANDLE_W / 2.0, 12, _HANDLE_W, _HANDLE_H),
            _HANDLE_H / 2.0, _HANDLE_H / 2.0,
        )


__all__ = [
    "MdDraggableScrollableSheet",
    "clamp_size",
    "nearest_snap",
    "couple_wheel",
]
