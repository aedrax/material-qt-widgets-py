"""Shared dropdown controller for field-anchored option popups.

Drives a single reused :class:`MdMenu` anchored under a field — the common
machinery behind the autocomplete, the filterable select, and the search bar's
suggestions. It owns:

* one persistent popup whose rows are rebuilt in place (so it resizes to the
  current matches without leaking windows);
* anchoring below the field at the field's width;
* optional top-match auto-highlight (so Enter commits without arrowing);
* for a non-grabbing popup, forwarding Up/Down/Enter/Escape from the typing
  input so the field keeps the keyboard while the popup is shown.

It is deliberately value-agnostic: :meth:`show` takes display **labels** and
:attr:`selected` re-emits the chosen label, leaving the host to map label →
value (each host already owns that mapping). Dismissal on an outside press is
handled by :class:`MdMenu` itself.
"""

from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtWidgets import QWidget

from .menu import MdMenu, MdMenuItem


class DropdownController(QObject):
    """Manages a field-anchored options popup. See the module docstring."""

    selected = Signal(str)  # the chosen row's text/label

    def __init__(
        self,
        anchor: QWidget,
        *,
        key_source: QWidget | None = None,
        max_height: int = 0,
        grabs_focus: bool = False,
        auto_highlight: bool = False,
    ) -> None:
        super().__init__(anchor)
        self._anchor = anchor
        self._max_height = int(max_height)
        self._grabs_focus = bool(grabs_focus)
        self._auto_highlight = bool(auto_highlight)
        self._menu: MdMenu | None = None
        # Drive the (non-grabbing) popup's navigation from the typing input,
        # which keeps the keyboard. Grabbing popups own their own key handling,
        # so they pass no key_source.
        if key_source is not None:
            key_source.installEventFilter(self)

    @property
    def menu(self) -> MdMenu | None:
        return self._menu

    def is_open(self) -> bool:
        return self._menu is not None and not self._menu.isHidden()

    def _ensure(self) -> MdMenu:
        if self._menu is None:
            self._menu = MdMenu(
                self._anchor, max_height=self._max_height,
                grabs_focus=self._grabs_focus,
            )
            self._menu.selected.connect(self.selected)  # re-emit the chosen label
        return self._menu

    def show(self, labels: Iterable[str]) -> None:
        """Rebuild the rows from ``labels`` and (re)open anchored under the field.

        Closes instead when ``labels`` is empty.
        """
        labels = list(labels)
        if not labels:
            self.close()
            return
        menu = self._ensure()
        menu.clear()
        for label in labels:
            menu.add_item(MdMenuItem(label))
        menu.setFixedWidth(self._anchor.width())
        menu.open_at(self._anchor)
        if self._auto_highlight:
            menu.highlight_first()

    def close(self) -> None:
        if self._menu is not None:
            self._menu.close()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if event.type() == QEvent.Type.KeyPress and self.is_open():
            key = event.key()
            if key == Qt.Key.Key_Down:
                self._menu.highlight_next()
                return True
            if key == Qt.Key.Key_Up:
                self._menu.highlight_prev()
                return True
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                return self._menu.activate_highlighted()
            if key == Qt.Key.Key_Escape:
                self.close()
                return True
        return False


__all__ = ["DropdownController"]
