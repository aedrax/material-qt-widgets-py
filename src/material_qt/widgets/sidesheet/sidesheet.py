"""Material 3 modal side sheet for QtWidgets.

A side sheet is a full-height panel anchored to a side edge (right by default,
or left). The modal variant slides in over a scrim with a ``surface-container-low``
panel whose *leading* corners are rounded, a header (title + close icon),
scrollable content (:meth:`add_content`), and optional trailing action buttons
(:meth:`add_action`). Dismisses on scrim click, the close button, or Escape;
``closed`` fires when it finishes closing.

Mirrors :class:`MdBottomSheet` (scrim + slide, no ``QGraphicsOpacityEffect``)
but slides horizontally. :class:`MdStandardSideSheet` is the persistent
(non-modal) variant: it docks inline in a layout and toggles its width.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from ...core.focus_util import drop_focus_within
from ...core.material_widget import MaterialWidgetMixin
from ...core.motion import MOTION_ENABLED, duration_ms, easing_curve
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...tokens.motion import Duration, Easing
from ...tokens.shape import CornerRadii
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..button import MdTextButton
from ..divider import MdDivider
from ..iconbutton import MdIconButton

_SCRIM_OPACITY = 0.32
_RADIUS = 28
_WIDTH = 320
_PAD = 16


class _SideSheetPanel(MaterialWidgetMixin, QWidget):
    def __init__(self, side: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        # Round only the leading (inner) corners; the outer edge is flush.
        radii = (CornerRadii(_RADIUS, 0, 0, _RADIUS) if side == "right"
                 else CornerRadii(0, _RADIUS, _RADIUS, 0))
        self._init_material(
            shape=radii,
            elevation=ElevationLevel.LEVEL1,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE_CONTAINER_LOW,
        )

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.paint_material_surface(painter)


class MdSideSheet(QWidget):
    """A modal side sheet overlay."""

    closed = Signal()

    def __init__(self, parent: QWidget, *, title: str = "", side: str = "right") -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._side = side if side in ("right", "left") else "right"
        self._shown = 0.0  # 0 = off the edge, 1 = resting

        self._panel = _SideSheetPanel(self._side, self)
        self._panel.setFixedWidth(_WIDTH)
        pl = QVBoxLayout(self._panel)
        pl.setContentsMargins(_PAD, _PAD, _PAD, _PAD)
        pl.setSpacing(8)

        header = QHBoxLayout()
        self._title = QLabel(title)
        self._title.setFont(font_for_role(TypescaleRole.TITLE_LARGE))
        close = MdIconButton("close")
        close.clicked.connect(self.dismiss)
        header.addWidget(self._title)
        header.addStretch(1)
        header.addWidget(close)
        pl.addLayout(header)

        self._content = QVBoxLayout()
        self._content.setSpacing(8)
        pl.addLayout(self._content)
        pl.addStretch(1)

        self._divider = MdDivider()
        self._divider.hide()
        pl.addWidget(self._divider)
        self._actions = QHBoxLayout()
        self._actions.addStretch(1)
        pl.addLayout(self._actions)

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(duration_ms(Duration.MEDIUM2))
        self._anim.setEasingCurve(easing_curve(Easing.EMPHASIZED))
        self._anim.valueChanged.connect(self._set_shown)

        parent.installEventFilter(self)
        self._restyle()
        ThemeManager.instance().themeChanged.connect(self._restyle)
        ThemeManager.instance().themeChanged.connect(self.update)
        self.hide()

    def _restyle(self) -> None:
        c = ThemeManager.instance().color(ColorRole.ON_SURFACE).name()
        self._title.setStyleSheet(f"color: {c};")

    def add_content(self, widget: QWidget) -> None:
        self._content.addWidget(widget)

    def add_action(self, text: str) -> MdTextButton:
        """Append a trailing action button (shows a divider above the row)."""
        self._divider.show()
        btn = MdTextButton(text)
        self._actions.addWidget(btn)
        return btn

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
        w = min(_WIDTH, host.width())
        h = host.height()
        if self._side == "right":
            offscreen, resting = host.width(), host.width() - w
        else:
            offscreen, resting = -w, 0
        x = int(offscreen + (resting - offscreen) * self._shown)
        self._panel.setGeometry(x, 0, w, h)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if obj is self.parentWidget() and event.type() == QEvent.Type.Resize:
            if self.isVisible():
                self.setGeometry(self.parentWidget().rect())
                self._reposition()
        return False

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._reposition()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if not self._panel.geometry().contains(event.position().toPoint()):
            self.dismiss()

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.dismiss()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        scrim = QColor(ThemeManager.instance().color(ColorRole.SCRIM))
        scrim.setAlphaF(_SCRIM_OPACITY * self._shown)
        painter.fillRect(self.rect(), scrim)


class MdStandardSideSheet(MaterialWidgetMixin, QWidget):
    """A standard (persistent, non-modal) side sheet for use inline in a layout.

    Unlike :class:`MdSideSheet` there is no scrim or overlay — it docks beside
    the content (place it in a ``QHBoxLayout``) and toggles by animating its
    width between 0 and :data:`_WIDTH`, so the neighbouring content reflows.
    ``expand()`` / ``collapse()`` / :meth:`set_expanded`; ``toggled(bool)`` fires.
    """

    toggled = Signal(bool)

    def __init__(self, parent: QWidget | None = None, *, title: str = "",
                 side: str = "right", expanded: bool = True) -> None:
        super().__init__(parent)
        self._side = side if side in ("right", "left") else "right"
        self._expanded = expanded
        radii = (CornerRadii(_RADIUS, 0, 0, _RADIUS) if self._side == "right"
                 else CornerRadii(0, _RADIUS, _RADIUS, 0))
        self._init_material(
            shape=radii, ripple=False, focus_ring=False,
            surface_role=ColorRole.SURFACE_CONTAINER_LOW,
        )
        pl = QVBoxLayout(self)
        pl.setContentsMargins(_PAD, _PAD, _PAD, _PAD)
        pl.setSpacing(8)
        header = QHBoxLayout()
        self._title = QLabel(title)
        self._title.setFont(font_for_role(TypescaleRole.TITLE_LARGE))
        close = MdIconButton("close")
        close.clicked.connect(self.collapse)
        header.addWidget(self._title)
        header.addStretch(1)
        header.addWidget(close)
        pl.addLayout(header)
        self._content = QVBoxLayout()
        self._content.setSpacing(8)
        pl.addLayout(self._content)
        pl.addStretch(1)
        self._divider = MdDivider()
        self._divider.hide()
        pl.addWidget(self._divider)
        self._actions = QHBoxLayout()
        self._actions.addStretch(1)
        pl.addLayout(self._actions)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setFixedWidth(_WIDTH if expanded else 0)
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(duration_ms(Duration.MEDIUM2))
        self._anim.setEasingCurve(easing_curve(Easing.EMPHASIZED))
        self._anim.valueChanged.connect(lambda v: self.setFixedWidth(int(v)))
        self._restyle()
        ThemeManager.instance().themeChanged.connect(self._restyle)
        ThemeManager.instance().themeChanged.connect(self.update)

    def _restyle(self) -> None:
        c = ThemeManager.instance().color(ColorRole.ON_SURFACE).name()
        self._title.setStyleSheet(f"color: {c};")

    def add_content(self, widget: QWidget) -> None:
        self._content.addWidget(widget)

    def add_action(self, text: str) -> MdTextButton:
        self._divider.show()
        btn = MdTextButton(text)
        self._actions.addWidget(btn)
        return btn

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
        target = _WIDTH if expanded else 0
        if animated and MOTION_ENABLED:
            self._anim.stop()
            self._anim.setStartValue(self.width())
            self._anim.setEndValue(target)
            self._anim.start()
        else:
            self.setFixedWidth(target)
        self.toggled.emit(expanded)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.paint_material_surface(painter)


__all__ = ["MdSideSheet", "MdStandardSideSheet"]
