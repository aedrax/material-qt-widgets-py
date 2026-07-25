"""Immutable role -> QColor color schemes, built per mode and cached."""

from __future__ import annotations

from functools import lru_cache
from types import MappingProxyType
from collections.abc import Mapping

from PySide6.QtGui import QColor

from ..tokens.color import ColorRole, resolve_hex


class ColorScheme:
    """An immutable mapping of every :class:`ColorRole` to a :class:`QColor`.

    Instances are value objects keyed only by their ``dark`` flag; use
    :meth:`light` / :meth:`dark` to obtain the cached singletons.
    """

    __slots__ = ("_dark", "_colors")

    def __init__(self, *, dark: bool) -> None:
        self._dark = dark
        colors: dict[ColorRole, QColor] = {}
        for role in ColorRole:
            colors[role] = QColor(resolve_hex(role, dark=dark))
        self._colors: Mapping[ColorRole, QColor] = MappingProxyType(colors)

    @property
    def is_dark(self) -> bool:
        return self._dark

    def color(self, role: ColorRole | str) -> QColor:
        """Return a copy of the QColor for ``role`` (callers may mutate freely)."""
        return QColor(self._colors[ColorRole(role)])

    def __getitem__(self, role: ColorRole | str) -> QColor:
        return self.color(role)

    def __contains__(self, role: object) -> bool:
        try:
            return ColorRole(role) in self._colors  # type: ignore[arg-type]
        except ValueError:
            return False

    def __repr__(self) -> str:
        return f"ColorScheme(dark={self._dark})"

    @staticmethod
    def light() -> ColorScheme:
        return _cached_scheme(False)

    @staticmethod
    def dark() -> ColorScheme:
        return _cached_scheme(True)

    @staticmethod
    def for_mode(*, dark: bool) -> ColorScheme:
        return _cached_scheme(dark)


@lru_cache(maxsize=2)
def _cached_scheme(dark: bool) -> ColorScheme:
    return ColorScheme(dark=dark)


__all__ = ["ColorScheme"]
