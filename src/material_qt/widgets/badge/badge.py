"""MdBadge: Material 3 labs badge.

A small overlay indicator shown at the top-right corner of an anchor widget.
Two forms, matching the web component (``labs/badge``):

* a *small* badge -- a 6px error-colored dot, shown when ``value`` is empty;
* a *large* badge -- a 16px-tall error-colored pill showing a numeric/string
  ``value`` in on-error ``label-small`` typography.

Colors come from the Material tokens (``error`` background, ``on-error`` text),
the pill shape is ``corner-full``, and typography is ``label-small`` -- all
resolved live from :class:`ThemeManager` so the badge re-themes automatically.

Use :meth:`MdBadge.attach` (or :func:`attach`) to overlay a badge on a host
widget's top-right corner; the badge tracks the host's size/visibility.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QPoint, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter
from PySide6.QtWidgets import QSizePolicy, QWidget

from ...core.shape_util import rounded_path
from ...core.typography_util import font_for
from ...tokens.color import ColorRole
from ...tokens.shape import CornerRadii
from ...tokens.typography import TypescaleRole, spec_for
from ...theme.theme_manager import ThemeManager

# Hardcoded sizes from tokens/md-comp-badge: small dot 6px, large pill 16px.
_SMALL_SIZE = 6
_LARGE_SIZE = 16
# Horizontal padding inside the large pill (web: `padding: 0 4px`).
_LARGE_PADDING = 4


class MdBadge(QWidget):
    """A Material 3 badge: a small dot or a large value pill.

    Set :attr:`value` to a non-empty string to render the large form showing
    that value; leave it empty for the small dot form.
    """

    def __init__(
        self,
        value: str = "",
        parent: QWidget | None = None,
        *,
        is_label_visible: bool = True,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
        offset: QPoint | None = None,
        background_role: ColorRole = ColorRole.ERROR,
        text_role: ColorRole = ColorRole.ON_ERROR,
    ) -> None:
        super().__init__(parent)
        self._value = ""
        self._is_label_visible = bool(is_label_visible)
        self._alignment = alignment
        self._offset = offset if offset is not None else QPoint(0, 0)
        self._background_role = background_role
        self._text_role = text_role
        self._tracker: _HostTracker | None = None
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # A badge is always its intrinsic size; never let a layout stretch it.
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        ThemeManager.instance().themeChanged.connect(self.update)
        self.set_value(value)

    # -- value -------------------------------------------------------------

    @property
    def value(self) -> str:
        """The displayed value; empty string means the small dot form."""
        return self._value

    def set_value(self, value: str) -> None:
        """Set the badge value (empty -> small dot, non-empty -> large pill)."""
        value = "" if value is None else str(value)
        if value == self._value:
            return
        self._value = value
        self.updateGeometry()
        self.update()
        self._reposition_on_host()

    @property
    def is_large(self) -> bool:
        """Whether the badge renders the large (value) form."""
        return bool(self._value)

    # -- visibility / placement / theme -----------------------------------

    @property
    def is_label_visible(self) -> bool:
        """Whether the badge is shown at all (Flutter ``isLabelVisible``)."""
        return self._is_label_visible

    def set_label_visible(self, visible: bool) -> None:
        """Show/hide the badge; when False the badge stays hidden on its host."""
        self._is_label_visible = bool(visible)
        if not self._is_label_visible:
            self.hide()
        elif self.parentWidget() is not None and self.parentWidget().isVisible():
            self.show()
        self._reposition_on_host()
        self.update()

    @property
    def alignment(self) -> Qt.AlignmentFlag:
        """Anchor corner on the host (Flutter ``alignment``; default top-right)."""
        return self._alignment

    def set_alignment(self, alignment: Qt.AlignmentFlag) -> None:
        self._alignment = alignment
        self._reposition_on_host()

    @property
    def offset(self) -> QPoint:
        """Pixel offset from the anchor corner (Flutter ``offset``)."""
        return self._offset

    def set_offset(self, offset: QPoint) -> None:
        self._offset = offset
        self._reposition_on_host()

    @property
    def background_role(self) -> ColorRole:
        """Fill color role (Flutter ``backgroundColor``)."""
        return self._background_role

    def set_background_role(self, role: ColorRole) -> None:
        self._background_role = role
        self.update()

    @property
    def text_role(self) -> ColorRole:
        """Label color role (Flutter ``textColor``)."""
        return self._text_role

    def set_text_role(self, role: ColorRole) -> None:
        self._text_role = role
        self.update()

    # -- typography --------------------------------------------------------

    def _label_font(self) -> QFont:
        return font_for(spec_for(TypescaleRole.LABEL_SMALL))

    # -- sizing ------------------------------------------------------------

    def sizeHint(self) -> QSize:  # noqa: N802
        if not self.is_large:
            return QSize(_SMALL_SIZE, _SMALL_SIZE)
        metrics = QFontMetrics(self._label_font())
        text_w = metrics.horizontalAdvance(self._value)
        width = max(_LARGE_SIZE, text_w + 2 * _LARGE_PADDING)
        return QSize(width, _LARGE_SIZE)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return self.sizeHint()

    # -- painting ----------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        theme = ThemeManager.instance()
        bg: QColor = theme.color(self._background_role)

        rect = QRectF(self.rect())
        # corner-full pill: radius == half the height.
        radii = CornerRadii.uniform(rect.height() / 2.0)
        path = rounded_path(rect, radii)
        painter.fillPath(path, bg)

        if self.is_large:
            painter.setFont(self._label_font())
            painter.setPen(theme.color(self._text_role))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._value)

    # -- attachment --------------------------------------------------------

    def attach(self, host: QWidget) -> None:
        """Overlay this badge on ``host``'s top-right corner.

        The badge is reparented to ``host`` and repositions itself whenever the
        host is resized, shown, or hidden. Mirrors the web overlay where the
        badge is anchored to the top-right of its containing element.
        """
        self.setParent(host)
        self._tracker = _HostTracker(self, host)
        host.installEventFilter(self._tracker)
        self._reposition_on_host()
        if host.isVisible() and self._is_label_visible:
            self.show()

    def _reposition_on_host(self) -> None:
        host = self.parentWidget()
        if host is None:
            return
        self.resize(self.sizeHint())
        # Anchor to the corner named by ``alignment`` (default top-right), then
        # apply ``offset``. Mirrors Flutter's alignment/offset placement.
        align = self._alignment
        if align & Qt.AlignmentFlag.AlignRight:
            x = host.width() - self.width()
        elif align & Qt.AlignmentFlag.AlignHCenter:
            x = (host.width() - self.width()) // 2
        else:  # AlignLeft / default
            x = 0
        if align & Qt.AlignmentFlag.AlignBottom:
            y = host.height() - self.height()
        elif align & Qt.AlignmentFlag.AlignVCenter:
            y = (host.height() - self.height()) // 2
        else:  # AlignTop / default
            y = 0
        # Clamp the anchor to the host, then apply the (possibly negative)
        # offset unclamped, matching Flutter's offset semantics.
        x = max(0, x) + self._offset.x()
        y = max(0, y) + self._offset.y()
        self.move(x, y)
        self.raise_()


class _HostTracker(QObject):
    """Repositions a badge when its host widget resizes or changes visibility."""

    def __init__(self, badge: MdBadge, host: QWidget) -> None:
        super().__init__(host)
        self._badge = badge

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        kind = event.type()
        if kind in (QEvent.Type.Resize, QEvent.Type.Show, QEvent.Type.Move):
            self._badge._reposition_on_host()
            if kind == QEvent.Type.Show and self._badge.is_label_visible:
                self._badge.show()
        elif kind == QEvent.Type.Hide:
            self._badge.hide()
        return False


def attach(badge: MdBadge, host: QWidget) -> None:
    """Overlay ``badge`` on ``host``'s top-right corner (see :meth:`MdBadge.attach`)."""
    badge.attach(host)


__all__ = ["MdBadge", "attach"]
