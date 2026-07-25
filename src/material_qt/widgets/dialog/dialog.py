"""Material 3 dialog for QtWidgets.

Ports Material Web's ``dialog/`` — :class:`MdDialog`, a modal overlay that covers
its parent with a scrim and centers an elevated ``surface-container-high`` panel
(corner-extra-large, level-3 elevation). The panel holds an optional icon,
a ``headline-small`` headline, ``body-medium`` supporting text / content, and a
right-aligned row of text-button actions. The overlay fades in/out and dismisses
on a scrim click or Escape.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...core.material_widget import MaterialWidgetMixin
from ...core.modal_overlay import ModalOverlay
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...tokens.shape import ShapeScale
from ...theme.theme_manager import ThemeManager
from ..button import MdTextButton
from ..icon.icon import MdIcon

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


class MdDialog(ModalOverlay):
    """A modal dialog overlay."""

    accepted = Signal()

    def __init__(
        self,
        parent: QWidget,
        *,
        headline: str = "",
        icon: str = "",
        supporting_text: str = "",
        barrier_dismissible: bool = True,
    ) -> None:
        super().__init__(parent)
        # Whether a scrim click or Escape dismisses (Flutter's barrierDismissible).
        self._barrier_dismissible = barrier_dismissible
        # Theme-tracked children, restyled from ONE bound method: bound-QObject
        # connections auto-disconnect when the dialog is destroyed, unlike the
        # plain-Python closures they replace (which kept firing on the singleton
        # ThemeManager after deletion and raised RuntimeError).
        self._themed_labels: list[tuple[QLabel, ColorRole]] = []
        self._option_buttons: list[QPushButton] = []
        ThemeManager.instance().themeChanged.connect(self._restyle_themed)
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

        # The base drives a [0..1] fade (scrim alpha + a subtle panel slide). We
        # deliberately avoid a QGraphicsOpacityEffect: the panel already has a
        # QGraphicsDropShadowEffect (elevation), and nesting effects makes Qt spam
        # "painter not active" errors on every repaint.
        self._init_overlay(parent)

    def _style_label(self, label: QLabel, role: ColorRole) -> None:
        self._themed_labels.append((label, role))
        self._apply_label_color(label, role)

    @staticmethod
    def _apply_label_color(label: QLabel, role: ColorRole) -> None:
        label.setStyleSheet(f"color: {ThemeManager.instance().color(role).name()};")

    @staticmethod
    def _apply_option_style(btn: QPushButton) -> None:
        color = ThemeManager.instance().color(ColorRole.ON_SURFACE).name()
        btn.setStyleSheet(
            "QPushButton {"
            f" color: {color}; background: transparent; border: none;"
            " text-align: left; padding: 12px 0px; }"
        )

    def _restyle_themed(self) -> None:
        for label, role in self._themed_labels:
            self._apply_label_color(label, role)
        for btn in self._option_buttons:
            self._apply_option_style(btn)

    # -- content / actions -------------------------------------------------

    def add_content(self, widget: QWidget) -> None:
        self._body.addWidget(widget)

    def add_option(self, text: str) -> QPushButton:
        """Add a full-width, left-aligned tappable option row (SimpleDialog).

        Returns the button; connect its ``clicked`` signal to react. Selecting an
        option does not auto-close — call :meth:`close_dialog` (or emit
        :attr:`accepted`) from the handler if desired, mirroring Flutter's
        ``SimpleDialogOption`` whose ``onPressed`` typically pops the dialog.
        """
        btn = QPushButton(text)
        btn.setFlat(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFont(font_for_role("body-large"))
        # Left-aligned text, full row, no chrome — styled to the surface.
        self._option_buttons.append(btn)
        self._apply_option_style(btn)
        self._body.addWidget(btn)
        return btn

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
        self._close()

    def _on_reject(self) -> None:
        self.dismiss()

    # -- open / close ------------------------------------------------------

    def close_dialog(self) -> None:
        """Close without rejecting (public alias for the base close)."""
        self._close()

    # -- barrier dismiss (Flutter's barrierDismissible) --------------------

    @property
    def barrier_dismissible(self) -> bool:
        return self._barrier_dismissible

    def set_barrier_dismissible(self, value: bool) -> None:
        self._barrier_dismissible = value

    def mousePressEvent(self, event) -> None:  # noqa: N802
        # Scrim-click dismissal lives in the (un-editable) base; gate it here so a
        # non-dismissible dialog swallows the click instead of closing.
        if not self._barrier_dismissible:
            return
        super().mousePressEvent(event)

    def keyPressEvent(self, event) -> None:  # noqa: N802
        # Likewise gate Escape (the base would otherwise dismiss).
        if not self._barrier_dismissible and event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)

    def _panel_width(self) -> int:
        # Clamp to the available width (pickers use a fixed-width panel instead).
        return max(_MIN_W, min(_MAX_W, self.width() - 48))


__all__ = ["MdDialog"]
