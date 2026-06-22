"""Material 3 modal bottom sheet for QtWidgets.

Ports the Material 3 modal bottom sheet (cf. Flutter's ``showModalBottomSheet``):
a scrim over the host with a ``surface-container-low`` panel that slides up from
the bottom edge, with rounded top corners (extra-large) and a drag handle at the
top. Content is added with :meth:`add_content`. Dismisses on scrim click or
Escape; ``closed`` fires when it finishes closing.

Composites the snackbar slide (no ``QGraphicsOpacityEffect``) with the dialog
scrim. :class:`MdStandardBottomSheet` is the persistent (non-modal) variant: it
docks inline at the bottom of a layout and toggles between a peek and its full
height.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QRectF, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from ...core.focus_util import drop_focus_within
from ...core.material_widget import MaterialWidgetMixin
from ...core.motion import MOTION_ENABLED, duration_ms, easing_curve
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...tokens.motion import Duration, Easing
from ...tokens.shape import CornerRadii
from ...theme.theme_manager import ThemeManager

_SCRIM_OPACITY = 0.32
_RADIUS = 28
_HANDLE_W = 32
_HANDLE_H = 4
_PAD = 16


class _SheetPanel(MaterialWidgetMixin, QWidget):
    def __init__(self, parent: QWidget | None = None, *, show_handle: bool = True) -> None:
        super().__init__(parent)
        self._show_handle = show_handle
        self._init_material(
            shape=CornerRadii(_RADIUS, _RADIUS, 0, 0),
            elevation=ElevationLevel.LEVEL1,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE_CONTAINER_LOW,
        )

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.paint_material_surface(painter)
        if not self._show_handle:
            return
        # Drag handle.
        theme = ThemeManager.instance()
        handle = theme.color(ColorRole.ON_SURFACE_VARIANT)
        handle.setAlphaF(0.4)
        painter.setBrush(handle)
        painter.setPen(Qt.PenStyle.NoPen)
        cx = self.width() / 2.0
        painter.drawRoundedRect(
            QRectF(cx - _HANDLE_W / 2.0, 12, _HANDLE_W, _HANDLE_H),
            _HANDLE_H / 2.0, _HANDLE_H / 2.0,
        )


class MdBottomSheet(QWidget):
    """A modal bottom sheet overlay."""

    closed = Signal()

    def __init__(
        self,
        parent: QWidget,
        *,
        show_drag_handle: bool = True,
        is_dismissible: bool = True,
        max_height_ratio: float = 0.6,
    ) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._shown = 0.0  # 0 = below the edge, 1 = resting
        # Whether a scrim click dismisses (Flutter's isDismissible).
        self._is_dismissible = is_dismissible
        # Cap on the panel height as a fraction of the host (Flutter's
        # constraints / scrollControlDisabledMaxHeightRatio).
        self._max_height_ratio = max_height_ratio
        self._show_drag_handle = show_drag_handle

        self._panel = _SheetPanel(self, show_handle=show_drag_handle)
        self._content = QVBoxLayout(self._panel)
        # Reserve top space for the handle only when it is shown.
        top = 28 if show_drag_handle else _PAD
        self._content.setContentsMargins(_PAD, top, _PAD, _PAD)
        self._content.setSpacing(8)

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(duration_ms(Duration.MEDIUM2))
        self._anim.setEasingCurve(easing_curve(Easing.EMPHASIZED))
        self._anim.valueChanged.connect(self._set_shown)

        parent.installEventFilter(self)
        ThemeManager.instance().themeChanged.connect(self.update)
        self.hide()

    def add_content(self, widget: QWidget) -> None:
        self._content.addWidget(widget)

    # -- open / close ------------------------------------------------------

    def open(self) -> None:
        self.setGeometry(self.parentWidget().rect())
        self.raise_()
        self.show()
        self.setFocus()
        self._reposition()
        if MOTION_ENABLED:
            self._anim.stop()
            self._anim.setStartValue(self._shown)
            self._anim.setEndValue(1.0)
            self._anim.start()
        else:
            self._set_shown(1.0)

    def dismiss(self) -> None:
        if self.isHidden():
            return
        # Drop focus before hiding (either path) so Qt doesn't reassign it to a
        # sibling with TabFocusReason, showing a spurious keyboard focus ring.
        drop_focus_within(self)
        # Animate only if there is distance to travel; a 0->0 tween emits no
        # valueChanged, so dismissing an already-collapsed sheet must hide now.
        if MOTION_ENABLED and self._shown > 0.01:
            self._anim.stop()
            self._anim.setStartValue(self._shown)
            self._anim.setEndValue(0.0)
            self._anim.start()  # _set_shown hides + emits when it reaches 0
        else:
            self._shown = 0.0
            self.hide()
            self.closed.emit()

    def _set_shown(self, value) -> None:
        self._shown = float(value)
        self._reposition()
        self.update()
        if self._shown <= 0.01 and self._anim.endValue() == 0.0 and not self.isHidden():
            self.hide()
            self.closed.emit()

    # -- geometry / scrim --------------------------------------------------

    def _reposition(self) -> None:
        host = self.parentWidget()
        if host is None:
            return
        self._panel.adjustSize()
        w = host.width()
        h = min(self._panel.sizeHint().height(), int(host.height() * self._max_height_ratio))
        resting_y = host.height() - h
        offscreen_y = host.height()
        y = int(offscreen_y + (resting_y - offscreen_y) * self._shown)
        self._panel.setGeometry(0, y, w, h)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if obj is self.parentWidget() and event.type() == QEvent.Type.Resize:
            if self.isVisible():
                self.setGeometry(self.parentWidget().rect())
                self._reposition()
        return False

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._reposition()

    @property
    def is_dismissible(self) -> bool:
        return self._is_dismissible

    def set_dismissible(self, value: bool) -> None:
        self._is_dismissible = value

    @property
    def show_drag_handle(self) -> bool:
        return self._show_drag_handle

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if (self._is_dismissible
                and not self._panel.geometry().contains(event.position().toPoint())):
            self.dismiss()

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape and self._is_dismissible:
            self.dismiss()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        scrim = QColor(ThemeManager.instance().color(ColorRole.SCRIM))
        scrim.setAlphaF(_SCRIM_OPACITY * self._shown)
        painter.fillRect(self.rect(), scrim)


class MdStandardBottomSheet(MaterialWidgetMixin, QWidget):
    """A standard (persistent, non-modal) bottom sheet for use inline in a layout.

    Unlike :class:`MdBottomSheet` there is no scrim or overlay — it docks at the
    bottom (place it last in a ``QVBoxLayout``) and toggles between a *peek*
    height (drag handle only) and its full content height; clicking the handle
    area toggles it. ``expand()`` / ``collapse()`` / :meth:`set_expanded`;
    ``toggled(bool)`` fires.
    """

    toggled = Signal(bool)

    _PEEK = 28  # collapsed height: just the drag handle

    def __init__(self, parent: QWidget | None = None, *, expanded: bool = False) -> None:
        super().__init__(parent)
        self._expanded = expanded
        self._init_material(
            shape=CornerRadii(_RADIUS, _RADIUS, 0, 0),
            elevation=ElevationLevel.LEVEL1,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE_CONTAINER_LOW,
        )
        self._content = QVBoxLayout(self)
        self._content.setContentsMargins(_PAD, 28, _PAD, _PAD)
        self._content.setSpacing(8)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(duration_ms(Duration.MEDIUM2))
        self._anim.setEasingCurve(easing_curve(Easing.EMPHASIZED))
        self._anim.valueChanged.connect(lambda v: self.setFixedHeight(int(v)))
        ThemeManager.instance().themeChanged.connect(self.update)
        self.setFixedHeight(self._full_height() if expanded else self._PEEK)

    def add_content(self, widget: QWidget) -> None:
        self._content.addWidget(widget)
        if self._expanded:
            self.setFixedHeight(self._full_height())

    def _full_height(self) -> int:
        return max(self._PEEK, self.sizeHint().height())

    @property
    def expanded(self) -> bool:
        return self._expanded

    def expand(self) -> None:
        self.set_expanded(True)

    def collapse(self) -> None:
        self.set_expanded(False)

    def set_expanded(self, expanded: bool, *, animated: bool = True) -> None:
        if expanded == self._expanded:
            return
        self._expanded = expanded
        target = self._full_height() if expanded else self._PEEK
        if animated and MOTION_ENABLED:
            self._anim.stop()
            self._anim.setStartValue(self.height())
            self._anim.setEndValue(target)
            self._anim.start()
        else:
            self.setFixedHeight(target)
        self.toggled.emit(expanded)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        # Clicking the drag-handle strip toggles the sheet.
        if event.position().y() <= 28:
            self.set_expanded(not self._expanded)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.paint_material_surface(painter)
        theme = ThemeManager.instance()
        handle = theme.color(ColorRole.ON_SURFACE_VARIANT)
        handle.setAlphaF(0.4)
        painter.setBrush(handle)
        painter.setPen(Qt.PenStyle.NoPen)
        cx = self.width() / 2.0
        painter.drawRoundedRect(
            QRectF(cx - _HANDLE_W / 2.0, 12, _HANDLE_W, _HANDLE_H),
            _HANDLE_H / 2.0, _HANDLE_H / 2.0,
        )


__all__ = ["MdBottomSheet", "MdStandardBottomSheet"]
