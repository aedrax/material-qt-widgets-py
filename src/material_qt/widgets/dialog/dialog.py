"""Material 3 dialog for QtWidgets.

Ports Material Web's ``dialog/`` — :class:`MdDialog`, a modal overlay that covers
its parent with a scrim and centers an elevated ``surface-container-high`` panel
(corner-extra-large, level-3 elevation). The panel holds an optional icon,
a ``headline-small`` headline, ``body-medium`` supporting text / content, and a
right-aligned row of text-button actions. The overlay fades in/out and dismisses
on a scrim click or Escape.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ...core.focus_util import drop_focus_within
from ...core.material_widget import MaterialWidgetMixin
from ...core.motion import MOTION_ENABLED, duration_ms, easing_curve
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...tokens.motion import Duration, Easing
from ...tokens.shape import ShapeScale
from ...theme.theme_manager import ThemeManager
from ..button import MdTextButton
from ..icon.icon import MdIcon

_SCRIM_OPACITY = 0.32
_MIN_W = 280
_MAX_W = 560
_PAD = 24


class _DialogPanel(MaterialWidgetMixin, QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_material(
            shape=ShapeScale.EXTRA_LARGE,
            elevation=ElevationLevel.LEVEL3,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE_CONTAINER_HIGH,
        )

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


class MdDialog(QWidget):
    """A modal dialog overlay."""

    accepted = Signal()
    rejected = Signal()
    closed = Signal()

    def __init__(
        self,
        parent: QWidget,
        *,
        headline: str = "",
        icon: str = "",
        supporting_text: str = "",
    ) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._panel = _DialogPanel(self)
        pl = QVBoxLayout(self._panel)
        pl.setContentsMargins(_PAD, _PAD, _PAD, _PAD)
        pl.setSpacing(16)

        if icon:
            ic = MdIcon(icon, color_role=ColorRole.SECONDARY)
            ic.set_size(24)
            row = QHBoxLayout()
            row.addStretch(1)
            row.addWidget(ic)
            row.addStretch(1)
            pl.addLayout(row)

        if headline:
            h = QLabel(headline)
            h.setFont(font_for_role("headline-small"))
            self._style_label(h, ColorRole.ON_SURFACE)
            pl.addWidget(h)

        self._body = QVBoxLayout()
        self._body.setSpacing(8)
        if supporting_text:
            t = QLabel(supporting_text)
            t.setWordWrap(True)
            t.setFont(font_for_role("body-medium"))
            self._style_label(t, ColorRole.ON_SURFACE_VARIANT)
            self._body.addWidget(t)
        pl.addLayout(self._body)

        self._actions = QHBoxLayout()
        self._actions.setSpacing(8)
        self._actions.addStretch(1)
        pl.addLayout(self._actions)

        # Enter animation drives a [0..1] fade applied to the scrim alpha + a
        # subtle panel slide. We deliberately do NOT use a QGraphicsOpacityEffect
        # here: the panel already has a QGraphicsDropShadowEffect (elevation), and
        # nesting an effect inside an effect makes Qt spam "painter not active"
        # errors on every repaint.
        self._fade = 0.0
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(duration_ms(Duration.MEDIUM2))
        self._anim.setEasingCurve(easing_curve(Easing.EMPHASIZED))
        self._anim.valueChanged.connect(self._set_fade)

        parent.installEventFilter(self)
        ThemeManager.instance().themeChanged.connect(self.update)
        self.hide()

    def _style_label(self, label: QLabel, role: ColorRole) -> None:
        def apply() -> None:
            label.setStyleSheet(f"color: {ThemeManager.instance().color(role).name()};")

        apply()
        ThemeManager.instance().themeChanged.connect(apply)

    # -- content / actions -------------------------------------------------

    def add_content(self, widget: QWidget) -> None:
        self._body.addWidget(widget)

    def add_action(self, text: str, *, accept: bool | None = None) -> MdTextButton:
        """Add a text-button action. accept=True/False emits accepted/rejected
        (and closes); None just returns the button for custom handling."""
        btn = MdTextButton(text)
        self._actions.addWidget(btn)
        if accept is True:
            btn.clicked.connect(self._on_accept)
        elif accept is False:
            btn.clicked.connect(self._on_reject)
        return btn

    def _on_accept(self) -> None:
        self.accepted.emit()
        self.close_dialog()

    def _on_reject(self) -> None:
        self.rejected.emit()
        self.close_dialog()

    # -- open / close ------------------------------------------------------

    def open(self) -> None:
        self.setGeometry(self.parentWidget().rect())
        self._center_panel()
        self.raise_()
        self.show()
        self.setFocus()
        if MOTION_ENABLED:
            self._anim.stop()
            self._anim.setStartValue(0.0)
            self._anim.setEndValue(1.0)
            self._anim.start()
        else:
            self._set_fade(1.0)

    def _set_fade(self, value) -> None:
        self._fade = float(value)
        self._center_panel()
        self.update()

    def close_dialog(self) -> None:
        # Drop focus before hiding so Qt doesn't reassign it to a sibling with
        # TabFocusReason, which would show a spurious keyboard focus ring.
        drop_focus_within(self)
        self.hide()
        self.closed.emit()

    # -- geometry / scrim --------------------------------------------------

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if obj is self.parentWidget() and event.type() == QEvent.Type.Resize:
            if self.isVisible():
                self.setGeometry(self.parentWidget().rect())
                self._center_panel()
        return False

    def _center_panel(self) -> None:
        avail_w = self.width()
        w = max(_MIN_W, min(_MAX_W, avail_w - 48))
        self._panel.adjustSize()
        h = self._panel.sizeHint().height()
        # Subtle slide-up as the dialog fades in (no opacity effect needed).
        slide = int((1.0 - self._fade) * 12)
        self._panel.setGeometry(
            int((self.width() - w) / 2),
            int((self.height() - h) / 2) + slide,
            int(w),
            int(h),
        )

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._center_panel()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        # Click on the scrim (outside the panel) dismisses.
        if not self._panel.geometry().contains(event.position().toPoint()):
            self.rejected.emit()
            self.close_dialog()

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.rejected.emit()
            self.close_dialog()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        scrim = QColor(ThemeManager.instance().color(ColorRole.SCRIM))
        scrim.setAlphaF(_SCRIM_OPACITY * self._fade)
        painter.fillRect(self.rect(), scrim)


__all__ = ["MdDialog"]
