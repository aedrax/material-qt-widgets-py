"""Application-wide theme singleton carrying Material color roles out-of-band.

QPalette only models a handful of roles, far fewer than Material's ~50, so the
theme is carried via this singleton + the :attr:`ThemeManager.themeChanged`
signal. A sensible subset is also mapped onto the application ``QPalette`` so
native Qt widgets pick up the theme.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Mapping

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QGuiApplication, QPalette

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
        # Runtime color-role overrides applied on top of the resolved scheme,
        # kept per mode so a brand color can differ between light and dark.
        self._overrides_light: dict[ColorRole, QColor] = {}
        self._overrides_dark: dict[ColorRole, QColor] = {}
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
        self._notify()

    def _notify(self) -> None:
        """Rebuild the app palette and emit ``themeChanged``.

        Used by both scheme changes and override changes — the latter mutate
        resolved values without changing the (cached) scheme object, so they
        cannot rely on :meth:`_refresh`'s identity guard.
        """
        app = QGuiApplication.instance()
        if app is not None:
            self.apply_app_palette(app)
        self.themeChanged.emit()

    # -- color access ------------------------------------------------------

    def color(self, role: ColorRole | str):
        """Return the QColor for ``role``, honoring any runtime override."""
        role = ColorRole(role)
        overrides = self._overrides_dark if self._scheme.is_dark else self._overrides_light
        if role in overrides:
            return QColor(overrides[role])
        return self._scheme.color(role)

    # -- runtime overrides -------------------------------------------------

    def set_overrides(
        self,
        overrides: Mapping[ColorRole | str, QColor | str],
        *,
        mode: ThemeMode | None = None,
    ) -> None:
        """Override color-role values at runtime (e.g. brand the ``primary`` role).

        Values accept a :class:`QColor` or any string :class:`QColor` understands
        (e.g. ``"#006A6A"``). ``mode=None`` applies to both light and dark;
        ``LIGHT``/``DARK`` applies to that scheme only. Repaints all widgets.
        """
        normalized = {ColorRole(k): QColor(v) for k, v in overrides.items()}
        for target in self._override_targets(mode):
            target.update(normalized)
        self._notify()

    def clear_overrides(self, *, mode: ThemeMode | None = None) -> None:
        """Remove overrides for the given mode (or both when ``mode`` is None)."""
        for target in self._override_targets(mode):
            target.clear()
        self._notify()

    def overrides(self, *, dark: bool | None = None) -> dict[ColorRole, QColor]:
        """A copy of the active (or specified) mode's overrides, for inspection."""
        is_dark = self._scheme.is_dark if dark is None else dark
        src = self._overrides_dark if is_dark else self._overrides_light
        return {role: QColor(color) for role, color in src.items()}

    def _override_targets(
        self, mode: ThemeMode | None
    ) -> list[dict[ColorRole, QColor]]:
        if mode is ThemeMode.DARK:
            return [self._overrides_dark]
        if mode is ThemeMode.LIGHT:
            return [self._overrides_light]
        return [self._overrides_light, self._overrides_dark]

    # -- QPalette mapping --------------------------------------------------

    def apply_app_palette(self, app: QGuiApplication | None = None) -> None:
        """Map a sensible Material subset onto the application QPalette.

        surface -> Window, on-surface -> WindowText, primary -> Highlight,
        on-primary -> HighlightedText, surface-container-lowest -> Base.
        """
        app = app or QGuiApplication.instance()
        if app is None:
            return
        c = self.color  # honors runtime overrides
        palette = QPalette(app.palette())
        cr = QPalette.ColorRole
        palette.setColor(cr.Window, c(ColorRole.SURFACE))
        palette.setColor(cr.WindowText, c(ColorRole.ON_SURFACE))
        palette.setColor(cr.Base, c(ColorRole.SURFACE_CONTAINER_LOWEST))
        palette.setColor(cr.Text, c(ColorRole.ON_SURFACE))
        palette.setColor(cr.Highlight, c(ColorRole.PRIMARY))
        palette.setColor(cr.HighlightedText, c(ColorRole.ON_PRIMARY))
        palette.setColor(cr.ButtonText, c(ColorRole.ON_SURFACE))
        palette.setColor(cr.Button, c(ColorRole.SURFACE_CONTAINER))
        app.setPalette(palette)


__all__ = ["ThemeManager", "ThemeMode"]
