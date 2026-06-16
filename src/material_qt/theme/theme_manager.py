"""Application-wide theme singleton carrying Material color roles out-of-band.

QPalette only models a handful of roles, far fewer than Material's ~50, so the
theme is carried via this singleton + the :attr:`ThemeManager.themeChanged`
signal. A sensible subset is also mapped onto the application ``QPalette`` so
native Qt widgets pick up the theme.
"""

from __future__ import annotations

from enum import Enum, auto

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QGuiApplication, QPalette

from ..tokens.color import ColorRole
from .color_scheme import ColorScheme


class ThemeMode(Enum):
    """How the active scheme is chosen."""

    LIGHT = auto()
    DARK = auto()
    SYSTEM = auto()


def _system_is_dark() -> bool:
    """Best-effort OS dark-mode detection via Qt style hints (Qt 6.5+)."""
    app = QGuiApplication.instance()
    if app is None:
        return False
    try:
        from PySide6.QtCore import Qt

        hints = app.styleHints()
        return hints.colorScheme() == Qt.ColorScheme.Dark
    except (AttributeError, TypeError):
        # Older Qt without colorScheme(): fall back to window lightness.
        palette = app.palette()
        return palette.color(QPalette.ColorRole.Window).lightness() < 128


class ThemeManager(QObject):
    """Singleton holding the active :class:`ColorScheme`.

    Use :meth:`instance` to access it. Emits :attr:`themeChanged` whenever the
    resolved scheme changes (mode change or system scheme change).
    """

    themeChanged = Signal()

    _instance: "ThemeManager | None" = None

    def __init__(self) -> None:
        super().__init__()
        self._mode = ThemeMode.SYSTEM
        self._scheme = ColorScheme.for_mode(dark=self._resolved_dark())
        self._connect_system_hints()

    # -- singleton ---------------------------------------------------------

    @classmethod
    def instance(cls) -> "ThemeManager":
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    # -- system hint wiring ------------------------------------------------

    def _connect_system_hints(self) -> None:
        app = QGuiApplication.instance()
        if app is None:
            return
        hints = app.styleHints()
        # colorSchemeChanged exists on Qt 6.5+; guard defensively.
        signal = getattr(hints, "colorSchemeChanged", None)
        if signal is not None:
            signal.connect(self._on_system_scheme_changed)

    def _on_system_scheme_changed(self, *args: object) -> None:
        if self._mode is ThemeMode.SYSTEM:
            self._refresh()

    # -- mode / scheme -----------------------------------------------------

    @property
    def mode(self) -> ThemeMode:
        return self._mode

    @property
    def scheme(self) -> ColorScheme:
        return self._scheme

    @property
    def is_dark(self) -> bool:
        return self._scheme.is_dark

    def _resolved_dark(self) -> bool:
        if self._mode is ThemeMode.DARK:
            return True
        if self._mode is ThemeMode.LIGHT:
            return False
        return _system_is_dark()

    def set_mode(self, mode: ThemeMode) -> None:
        """Set the theme mode; refreshes and signals if the scheme changes."""
        self._mode = mode
        self._refresh()

    def toggle_light_dark(self) -> None:
        """Convenience: flip between explicit LIGHT and DARK modes."""
        self.set_mode(ThemeMode.LIGHT if self.is_dark else ThemeMode.DARK)

    def _refresh(self) -> None:
        new_scheme = ColorScheme.for_mode(dark=self._resolved_dark())
        if new_scheme is self._scheme:
            return
        self._scheme = new_scheme
        app = QGuiApplication.instance()
        if app is not None:
            self.apply_app_palette(app)
        self.themeChanged.emit()

    # -- color access ------------------------------------------------------

    def color(self, role: ColorRole | str):
        """Return the QColor for ``role`` in the active scheme."""
        return self._scheme.color(role)

    # -- QPalette mapping --------------------------------------------------

    def apply_app_palette(self, app: QGuiApplication | None = None) -> None:
        """Map a sensible Material subset onto the application QPalette.

        surface -> Window, on-surface -> WindowText, primary -> Highlight,
        on-primary -> HighlightedText, surface-container-lowest -> Base.
        """
        app = app or QGuiApplication.instance()
        if app is None:
            return
        s = self._scheme
        palette = QPalette(app.palette())
        cr = QPalette.ColorRole
        palette.setColor(cr.Window, s.color(ColorRole.SURFACE))
        palette.setColor(cr.WindowText, s.color(ColorRole.ON_SURFACE))
        palette.setColor(cr.Base, s.color(ColorRole.SURFACE_CONTAINER_LOWEST))
        palette.setColor(cr.Text, s.color(ColorRole.ON_SURFACE))
        palette.setColor(cr.Highlight, s.color(ColorRole.PRIMARY))
        palette.setColor(cr.HighlightedText, s.color(ColorRole.ON_PRIMARY))
        palette.setColor(cr.ButtonText, s.color(ColorRole.ON_SURFACE))
        palette.setColor(cr.Button, s.color(ColorRole.SURFACE_CONTAINER))
        app.setPalette(palette)


__all__ = ["ThemeManager", "ThemeMode"]
