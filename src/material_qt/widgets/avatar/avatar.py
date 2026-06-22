"""Material circular avatar for QtWidgets.

Ports Flutter's ``CircleAvatar`` — a round container that shows either an image
(``QPixmap`` or an image path) or short fallback content (initials/text). The
background and foreground (text) colors resolve from theme roles so they track
theme switches; the size is expressed as a ``radius`` (half the diameter),
matching Flutter (default 20px ⇒ a 40px circle).

Flutter's ``minRadius``/``maxRadius`` (animated constraint pair) and the image
error callbacks are not ported — a single ``radius`` covers the sizing need and
Qt surfaces image-load failure synchronously via :meth:`QPixmap.isNull`.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter, QPainterPath, QPixmap
from PySide6.QtWidgets import QWidget

from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager

_DEFAULT_RADIUS = 20


class MdCircleAvatar(QWidget):
    """A circular avatar showing an image or fallback text/initials.

    Args:
        parent: Optional parent widget.
        text: Fallback text (e.g. initials) shown when no image is set.
        image: A ``QPixmap`` or path to an image file. When set (and loadable),
            it is drawn clipped to the circle and takes precedence over ``text``.
        radius: Half the diameter, in pixels (default 20 ⇒ a 40px circle).
        background_role: Theme color role for the circle fill.
        foreground_role: Theme color role for the fallback text.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        text: str = "",
        image: QPixmap | str | None = None,
        radius: int = _DEFAULT_RADIUS,
        background_role: ColorRole = ColorRole.PRIMARY_CONTAINER,
        foreground_role: ColorRole = ColorRole.ON_PRIMARY_CONTAINER,
    ) -> None:
        super().__init__(parent)
        self._text = text
        self._radius = max(0, int(radius))
        self._background_role = background_role
        self._foreground_role = foreground_role
        self._pixmap: QPixmap | None = None

        self.setFont(font_for_role(TypescaleRole.TITLE_MEDIUM))
        self._apply_size()
        if image is not None:
            self.set_image(image)

        ThemeManager.instance().themeChanged.connect(self.update)

    # -- sizing ------------------------------------------------------------

    def _apply_size(self) -> None:
        diameter = self._radius * 2
        self.setFixedSize(diameter, diameter)

    @property
    def radius(self) -> int:
        return self._radius

    @radius.setter
    def radius(self, value: int) -> None:
        value = max(0, int(value))
        if value != self._radius:
            self._radius = value
            self._apply_size()
            self.update()

    def set_radius(self, value: int) -> None:
        self.radius = value

    # -- content -----------------------------------------------------------

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        if value != self._text:
            self._text = value
            self.update()

    def set_text(self, value: str) -> None:
        self.text = value

    def set_image(self, image: QPixmap | str | None) -> None:
        """Set the avatar image from a ``QPixmap`` or a file path.

        Passing ``None`` (or an unloadable path) clears the image, falling back
        to the text content.
        """
        if image is None:
            self._pixmap = None
        elif isinstance(image, QPixmap):
            self._pixmap = image if not image.isNull() else None
        else:
            pm = QPixmap(str(image))
            self._pixmap = pm if not pm.isNull() else None
        self.update()

    @property
    def pixmap(self) -> QPixmap | None:
        return self._pixmap

    # -- colors ------------------------------------------------------------

    @property
    def background_role(self) -> ColorRole:
        return self._background_role

    @background_role.setter
    def background_role(self, role: ColorRole) -> None:
        if role != self._background_role:
            self._background_role = role
            self.update()

    @property
    def foreground_role(self) -> ColorRole:
        return self._foreground_role

    @foreground_role.setter
    def foreground_role(self, role: ColorRole) -> None:
        if role != self._foreground_role:
            self._foreground_role = role
            self.update()

    # -- painting ----------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        rect = QRectF(self.rect())
        if rect.isEmpty():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        theme = ThemeManager.instance()

        # Background fill.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(theme.color(self._background_role))
        painter.drawEllipse(rect)

        if self._pixmap is not None:
            # Clip to the circle and draw the image scaled to cover.
            painter.save()
            side = int(min(rect.width(), rect.height()))
            scaled = self._pixmap.scaled(
                side,
                side,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            # Center the (possibly larger) scaled pixmap inside the circle.
            x = rect.center().x() - scaled.width() / 2
            y = rect.center().y() - scaled.height() / 2
            clip = QPainterPath()
            clip.addEllipse(rect)
            painter.setClipPath(clip)
            painter.drawPixmap(int(x), int(y), scaled)
            painter.restore()
            return

        if self._text:
            painter.setPen(theme.color(self._foreground_role))
            painter.drawText(
                rect, Qt.AlignmentFlag.AlignCenter, self._text
            )


__all__ = ["MdCircleAvatar"]
