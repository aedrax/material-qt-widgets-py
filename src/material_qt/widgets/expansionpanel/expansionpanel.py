"""Material 3 expansion panel for QtWidgets.

An expandable panel (cf. Flutter's ``ExpansionTile``): a clickable header
(``title-medium`` title, optional ``body-medium`` subtitle, optional leading and
trailing widgets, plus a chevron that flips) over collapsible content that
animates its height open/closed. ``toggled(bool)`` fires on expand/collapse.

The content's expanded height is measured at expand time (after layout has given
the panel a real width), so wrapped-text content is not clipped. Panels are
independent — exclusive-accordion grouping (Flutter's ``ExpansionPanelList`` with
``ExpansionPanelRadio``) is deferred.
"""

from __future__ import annotations

from PySide6.QtCore import QAbstractAnimation, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from shiboken6 import isValid

from ...core.material_widget import MaterialWidgetMixin
from ...core.motion import animate
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.motion import Duration, Easing
from ...tokens.shape import ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..icon.icon import MdIcon

_PAD = 16
_HEADER_H = 56
_MAX = 16777215  # QWIDGETSIZE_MAX


class _Header(MaterialWidgetMixin, QWidget):
    clicked = Signal()

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        *,
        leading: QWidget | None = None,
        trailing: QWidget | None = None,
        show_trailing_icon: bool = True,
        surface_role: ColorRole = ColorRole.SURFACE,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._init_material(
            shape=ShapeScale.NONE, ripple=True, focus_ring=False,
            surface_role=surface_role,
        )
        self.setMinimumHeight(_HEADER_H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(_PAD, 0, _PAD, 0)
        lay.setSpacing(_PAD)

        # Optional leading widget (e.g. an avatar or icon).
        self._leading = leading
        if leading is not None:
            lay.addWidget(leading, 0)

        # Title (+ optional subtitle) stacked vertically.
        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)
        self._title = QLabel(title)
        self._title.setFont(font_for_role(TypescaleRole.TITLE_MEDIUM))
        text_col.addWidget(self._title)
        self._subtitle = QLabel(subtitle)
        self._subtitle.setFont(font_for_role(TypescaleRole.BODY_MEDIUM))
        self._subtitle.setVisible(bool(subtitle))
        text_col.addWidget(self._subtitle)
        lay.addLayout(text_col, 1)

        # Optional trailing widget, then the rotating chevron.
        self._trailing = trailing
        if trailing is not None:
            lay.addWidget(trailing, 0)
        self._chevron = MdIcon("expand_more", color_role=ColorRole.ON_SURFACE_VARIANT)
        self._chevron.set_size(24)
        self._chevron.setVisible(show_trailing_icon)
        lay.addWidget(self._chevron, 0)

        self._restyle()
        ThemeManager.instance().themeChanged.connect(self._restyle)

    def set_surface_role(self, role: ColorRole) -> None:
        self._surface_role = role
        self.update()

    def _restyle(self) -> None:
        tm = ThemeManager.instance()
        self._title.setStyleSheet(f"color: {tm.color(ColorRole.ON_SURFACE).name()};")
        self._subtitle.setStyleSheet(
            f"color: {tm.color(ColorRole.ON_SURFACE_VARIANT).name()};"
        )

    def set_title(self, title: str) -> None:
        self._title.setText(title)

    def set_subtitle(self, subtitle: str) -> None:
        self._subtitle.setText(subtitle)
        self._subtitle.setVisible(bool(subtitle))

    def set_expanded(self, expanded: bool) -> None:
        self._chevron.set_name("expand_less" if expanded else "expand_more")

    def mousePressEvent(self, event) -> None:  # noqa: N802
        self.clicked.emit()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


class MdExpansionPanel(QWidget):
    """An expandable header + collapsible content panel.

    Mirrors Flutter ``ExpansionTile``: ``title``/``subtitle`` text, optional
    ``leading``/``trailing`` widgets, ``initially_expanded`` (Flutter's
    ``initiallyExpanded``), a ``background_role`` theme color behind the header
    (Flutter's ``backgroundColor``), and a ``toggled(bool)`` Signal in place of
    ``onExpansionChanged``.
    """

    toggled = Signal(bool)

    def __init__(
        self,
        title: str = "",
        parent: QWidget | None = None,
        *,
        subtitle: str = "",
        leading: QWidget | None = None,
        trailing: QWidget | None = None,
        show_trailing_icon: bool = True,
        initially_expanded: bool = False,
        background_role: ColorRole = ColorRole.SURFACE,
        expanded: bool | None = None,
    ) -> None:
        super().__init__(parent)
        self._expanded = False
        self._background_role = background_role
        # In-flight height animation (+ its on_finished), so a new toggle can
        # cancel it instead of racing it.
        self._anim: QPropertyAnimation | None = None
        self._anim_on_finished = None
        # ``expanded`` kept as a back-compat alias for ``initially_expanded``.
        if expanded is not None:
            initially_expanded = expanded

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self._header = _Header(
            title,
            subtitle,
            leading=leading,
            trailing=trailing,
            show_trailing_icon=show_trailing_icon,
            surface_role=background_role,
        )
        self._header.clicked.connect(self.toggle)
        lay.addWidget(self._header)

        self._content = QWidget()
        self._content_lay = QVBoxLayout(self._content)
        self._content_lay.setContentsMargins(_PAD, 0, _PAD, _PAD)
        self._content_lay.setSpacing(8)
        self._content.setMaximumHeight(0)
        lay.addWidget(self._content)

        if initially_expanded:
            self.set_expanded(True, animated=False)

    # -- content -----------------------------------------------------------

    def add_content(self, widget: QWidget) -> None:
        self._content_lay.addWidget(widget)

    # -- header text / decorations -----------------------------------------

    def set_title(self, title: str) -> None:
        self._header.set_title(title)

    def set_subtitle(self, subtitle: str) -> None:
        self._header.set_subtitle(subtitle)

    @property
    def background_role(self) -> ColorRole:
        return self._background_role

    def set_background_role(self, role: ColorRole) -> None:
        """Set the theme color role painted behind the header (cf.
        Flutter ``backgroundColor``)."""
        self._background_role = role
        self._header.set_surface_role(role)

    # -- expansion ---------------------------------------------------------

    @property
    def expanded(self) -> bool:
        return self._expanded

    def toggle(self) -> None:
        self.set_expanded(not self._expanded)

    def set_expanded(self, expanded: bool, *, animated: bool = True) -> None:
        if expanded == self._expanded:
            return
        self._expanded = expanded
        self._header.set_expanded(expanded)
        # Cancel any in-flight height animation first so the terminal state
        # always matches this (the last) request — a finishing expand must not
        # unclamp (setMaximumHeight(_MAX)) a panel that was just collapsed.
        self._cancel_anim()
        if expanded:
            # Measure now — after layout has given the panel its width.
            target = self._content.sizeHint().height()
            if animated:
                def on_finished() -> None:
                    self._anim = None
                    self._anim_on_finished = None
                    self._content.setMaximumHeight(_MAX)
                self._anim_on_finished = on_finished
                self._anim = animate(self._content, b"maximumHeight", target,
                                     duration=Duration.MEDIUM2,
                                     easing=Easing.EMPHASIZED,
                                     start=0, on_finished=on_finished)
            else:
                self._content.setMaximumHeight(_MAX)
        else:
            start = self._content.height()
            self._content.setMaximumHeight(start)
            if animated:
                def on_finished() -> None:
                    self._anim = None
                    self._anim_on_finished = None
                self._anim_on_finished = on_finished
                self._anim = animate(self._content, b"maximumHeight", 0,
                                     duration=Duration.MEDIUM2,
                                     easing=Easing.EMPHASIZED,
                                     start=start, on_finished=on_finished)
            else:
                self._content.setMaximumHeight(0)
        self.toggled.emit(expanded)

    def _cancel_anim(self) -> None:
        anim, cb = self._anim, self._anim_on_finished
        self._anim = None
        self._anim_on_finished = None
        if anim is None or not isValid(anim):
            return
        if anim.state() == QAbstractAnimation.State.Stopped:
            return  # already finished (DeleteWhenStopped: C++ side is dying)
        # stop() fires ``finished``; disconnect first so the *old* request's
        # callback can't unclamp/clear state for the new one.
        if cb is not None:
            anim.finished.disconnect(cb)
        anim.stop()  # DeleteWhenStopped: the C++ object dies here


__all__ = ["MdExpansionPanel"]
