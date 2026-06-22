"""Material 3 full-screen search view for QtWidgets.

Ports the *view* half of Flutter's ``SearchAnchor`` (``search_anchor.dart``):
the surface that opens when a :class:`MdSearchBar` is tapped. It is a
``surface-container-high`` overlay that, in full-screen mode, fills its parent
with a header (a back affordance, an editable query field, and a clear button)
above a divider and a scrollable list of suggestions that update live as the
query changes. Selecting a suggestion emits :attr:`suggestionSelected` and
closes the view.

Property mapping (Flutter ``SearchAnchor`` ``view*`` → here):

* ``viewHintText`` → ``view_hint_text`` ctor kwarg / :meth:`set_placeholder`
* ``viewLeading`` (back button) → built-in back affordance, ``leading_icon``
* ``viewTrailing`` (clear) → built-in clear button
* ``suggestionsBuilder`` → ``suggestions_provider`` (a ``query -> list[str]``
  callable; data, so a plain callable rather than a Signal) plus the manual
  :meth:`set_suggestions` path
* ``viewOnChanged`` → :attr:`textChanged`; ``viewOnSubmitted`` → :attr:`submitted`
* selecting a suggestion → :attr:`suggestionSelected` (Signal) then close
* ``isFullScreen`` → ``full_screen`` ctor kwarg

The view subclasses :class:`core.ModalOverlay`, inheriting the scrim/fade,
Escape-to-dismiss, parent-resize tracking, and drop-focus-before-hide handling;
:meth:`_center_panel` is overridden so the panel fills the parent (full-screen)
or anchors to the top (non-full-screen).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

from PySide6.QtCore import Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ...core.material_widget import MaterialWidgetMixin
from ...core.modal_overlay import ModalOverlay
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...tokens.shape import ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..divider.divider import MdDivider
from ..iconbutton.iconbutton import MdIconButton
from ..list.list import MdListItem
from ..scrollbar.scrollbar import use_material_scrollbars

_HEADER_HEIGHT = 72
_PAD = 12

SuggestionsProvider = Callable[[str], Iterable[str]]


class _ViewPanel(MaterialWidgetMixin, QWidget):
    """The search view's content surface."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_material(
            shape=ShapeScale.NONE,
            elevation=ElevationLevel.LEVEL3,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE_CONTAINER_HIGH,
        )

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


class MdSearchView(ModalOverlay):
    """A Material 3 full-screen search view overlay.

    Open it with :meth:`open` (inherited) — typically wired to
    ``MdSearchBar.clicked``. It emits :attr:`suggestionSelected` when the user
    picks a suggestion (and then closes), :attr:`textChanged` / :attr:`submitted`
    mirroring the query field, and the inherited :attr:`rejected` / :attr:`closed`
    on dismissal.
    """

    textChanged = Signal(str)  # noqa: N815  (Qt-style signal name)
    submitted = Signal(str)
    suggestionSelected = Signal(str)  # noqa: N815

    def __init__(
        self,
        parent: QWidget,
        *,
        view_hint_text: str = "Search",
        leading_icon: str = "arrow_back",
        suggestions_provider: SuggestionsProvider | None = None,
        full_screen: bool = True,
    ) -> None:
        super().__init__(parent)
        self._full_screen = full_screen
        self._provider = suggestions_provider

        self._panel = _ViewPanel(self)
        panel_lay = QVBoxLayout(self._panel)
        panel_lay.setContentsMargins(0, 0, 0, 0)
        panel_lay.setSpacing(0)

        # -- header: back · query · clear ----------------------------------
        header = QWidget()
        header.setFixedHeight(_HEADER_HEIGHT)
        header_lay = QHBoxLayout(header)
        header_lay.setContentsMargins(_PAD, 0, _PAD, 0)
        header_lay.setSpacing(_PAD)

        self._back = MdIconButton(leading_icon)
        self._back.clicked.connect(self.dismiss)
        header_lay.addWidget(self._back, 0)

        self._edit = QLineEdit()
        self._edit.setPlaceholderText(view_hint_text)
        self._edit.setFont(font_for_role(TypescaleRole.BODY_LARGE))
        self._edit.setFrame(False)
        self._edit.textChanged.connect(self.textChanged.emit)
        self._edit.textChanged.connect(self._on_query_changed)
        self._edit.returnPressed.connect(
            lambda: self.submitted.emit(self._edit.text())
        )
        header_lay.addWidget(self._edit, 1)

        self._clear = MdIconButton("close")
        self._clear.clicked.connect(self._edit.clear)
        header_lay.addWidget(self._clear, 0)

        panel_lay.addWidget(header, 0)
        panel_lay.addWidget(MdDivider(), 0)

        # -- scrollable suggestion list ------------------------------------
        self._list_host = QWidget()
        self._list_lay = QVBoxLayout(self._list_host)
        self._list_lay.setContentsMargins(0, 0, 0, 0)
        self._list_lay.setSpacing(0)
        self._list_lay.addStretch(1)
        self._items: list[MdListItem] = []
        self._values: list[str] = []

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setWidget(self._list_host)
        self._scroll.setStyleSheet("background: transparent;")
        self._scroll.viewport().setStyleSheet("background: transparent;")
        use_material_scrollbars(self._scroll)  # match the gallery-wide scrollbar
        panel_lay.addWidget(self._scroll, 1)

        self._init_overlay(parent)
        self._restyle()
        ThemeManager.instance().themeChanged.connect(self._restyle)

    # -- query / suggestions ----------------------------------------------

    def text(self) -> str:
        return self._edit.text()

    def set_text(self, text: str) -> None:
        self._edit.setText(text)

    def set_placeholder(self, text: str) -> None:
        self._edit.setPlaceholderText(text)

    def set_suggestions_provider(self, provider: SuggestionsProvider | None) -> None:
        """Set the ``query -> suggestions`` callable and refresh the list."""
        self._provider = provider
        self._on_query_changed(self._edit.text())

    def set_suggestions(self, suggestions: Iterable[str]) -> None:
        """Replace the suggestion list with ``suggestions`` (the manual path)."""
        self._clear_items()
        for value in suggestions:
            value = str(value)
            item = MdListItem(value)
            item.clicked.connect(
                lambda v=value: self._on_suggestion_selected(v)
            )
            self._list_lay.insertWidget(self._list_lay.count() - 1, item)
            self._items.append(item)
            self._values.append(value)

    def suggestions(self) -> list[str]:
        return list(self._values)

    def _clear_items(self) -> None:
        for item in self._items:
            self._list_lay.removeWidget(item)
            item.setParent(None)
            item.deleteLater()
        self._items.clear()
        self._values.clear()

    def _on_query_changed(self, query: str) -> None:
        if self._provider is None:
            return
        self.set_suggestions(self._provider(query))

    def _on_suggestion_selected(self, value: str) -> None:
        self.suggestionSelected.emit(value)
        self._close()

    # -- overlay geometry --------------------------------------------------

    def open(self) -> None:  # noqa: A003
        super().open()
        self._edit.setFocus()

    def _center_panel(self) -> None:
        # Full-screen: fill the parent. Non-full-screen: a top-anchored surface
        # spanning the width, capped at ~2/3 height — a simplification of
        # Flutter's anchored-to-bar geometry (noted as a follow-up).
        if self._full_screen:
            self._panel.setGeometry(0, 0, self.width(), self.height())
        else:
            self._panel.setGeometry(0, 0, self.width(), int(self.height() * 2 / 3))

    def _restyle(self) -> None:
        theme = ThemeManager.instance()
        on_surface = theme.color(ColorRole.ON_SURFACE).name()
        hint = theme.color(ColorRole.ON_SURFACE_VARIANT).name()
        self._edit.setStyleSheet(
            "background: transparent; border: none;"
            f"color: {on_surface}; selection-background-color: {hint};"
        )


__all__ = ["MdSearchView", "SuggestionsProvider"]
