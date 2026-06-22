"""Material 3 stepper for QtWidgets.

Ports Flutter's ``Stepper``: an ordered list of :class:`MdStep` s, each with a
numbered (or icon) circle reflecting its :class:`StepState`, a ``title`` and
optional ``subtitle``, and a content widget revealed for the current step. A
``vertical`` stepper stacks steps with the active step's content in-between;
a ``horizontal`` stepper lays the circles in a row with the active content
below.

Qt-idiomatic surface (callbacks -> Signals):

* ``stepTapped(int)`` — Flutter ``onStepTapped``;
* ``continued`` — Flutter ``onStepContinue`` (emitted by the Continue button);
* ``canceled`` — Flutter ``onStepCancel`` (emitted by the Cancel button);
* ``currentStep`` property + ``set_current_step(int)`` — Flutter ``currentStep``;
* ``StepperType`` (``VERTICAL`` / ``HORIZONTAL``) — Flutter ``StepperType``.
"""

from __future__ import annotations

from enum import Enum

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ...core.material_widget import MaterialWidgetMixin
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.shape import ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..button.button import MdTextButton
from ..icon.icon import MdIcon

_CIRCLE = 24
_CONNECTOR = 1
_ROW_PAD = 24


class StepperType(Enum):
    """The stepper's main axis (cf. Flutter ``StepperType``)."""

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


class StepState(Enum):
    """The state of a step's circle (cf. Flutter ``StepState``)."""

    INDEXED = "indexed"   # show the step number
    EDITING = "editing"   # show a pencil icon
    COMPLETE = "complete"  # show a tick icon
    DISABLED = "disabled"  # show the step number, not tappable
    ERROR = "error"       # show an error glyph


class MdStep:
    """A single step in an :class:`MdStepper`.

    Mirrors Flutter's ``Step``: a ``title`` (str), optional ``subtitle`` (str),
    a ``content`` widget revealed when the step is current, a :class:`StepState`
    (``state``) and an ``active`` flag (Flutter ``isActive``).
    """

    def __init__(
        self,
        title: str,
        content: QWidget | None = None,
        *,
        subtitle: str = "",
        state: StepState = StepState.INDEXED,
        active: bool = False,
    ) -> None:
        self.title = title
        self.subtitle = subtitle
        self.content = content if content is not None else QWidget()
        self.state = state
        self.active = active


class _StepCircle(QWidget):
    """The numbered / icon circle drawn for a step."""

    def __init__(self, index: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._index = index
        self._state = StepState.INDEXED
        self._active = False
        self.setFixedSize(_CIRCLE, _CIRCLE)
        self._icon = MdIcon("", color_role=ColorRole.ON_PRIMARY)
        self._icon.set_size(18)
        self._icon.setParent(self)
        self._icon.hide()
        ThemeManager.instance().themeChanged.connect(self.update)

    def _filled(self) -> bool:
        # PRIMARY-filled when the step is active or already complete (M3 fills
        # completed steps with PRIMARY too); ERROR has its own fill.
        return self._active or self._state is StepState.COMPLETE

    def set_state(self, state: StepState, active: bool) -> None:
        self._state = state
        self._active = active
        # Glyph on-color must match the circle fill it sits on (PRIMARY fill ->
        # ON_PRIMARY; the inactive/disabled grey fill -> SURFACE, like the number).
        self._icon.set_color_role(
            ColorRole.ON_PRIMARY if self._filled() else ColorRole.SURFACE
        )
        if state is StepState.EDITING:
            self._icon.set_name("edit")
            self._icon.show()
        elif state is StepState.COMPLETE:
            self._icon.set_name("check")
            self._icon.show()
        else:
            self._icon.hide()
        self._icon.move(
            (self.width() - self._icon.width()) // 2,
            (self.height() - self._icon.height()) // 2,
        )
        self.update()

    def _circle_color(self) -> QColor:
        tm = ThemeManager.instance()
        if self._state is StepState.ERROR:
            return tm.color(ColorRole.ERROR)
        if self._filled():
            return tm.color(ColorRole.PRIMARY)
        c = QColor(tm.color(ColorRole.ON_SURFACE))
        c.setAlphaF(0.38)
        return c

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._circle_color())
        painter.drawEllipse(self.rect())
        if self._state in (StepState.EDITING, StepState.COMPLETE):
            return  # the MdIcon child paints the glyph
        tm = ThemeManager.instance()
        if self._state is StepState.ERROR:
            painter.setPen(tm.color(ColorRole.ON_ERROR))
            text = "!"
        else:
            painter.setPen(tm.color(ColorRole.ON_PRIMARY) if self._filled()
                           else tm.color(ColorRole.SURFACE))
            text = str(self._index + 1)
        painter.setFont(font_for_role(TypescaleRole.LABEL_LARGE))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)


class _StepHeader(MaterialWidgetMixin, QWidget):
    """A tappable circle + (title, subtitle) header for one step."""

    clicked = Signal()

    def __init__(self, index: int, step: MdStep, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._step = step
        self._init_material(
            shape=ShapeScale.SMALL, ripple=True, focus_ring=False,
            surface_role=ColorRole.SURFACE,
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.setSpacing(12)
        self.circle = _StepCircle(index)
        lay.addWidget(self.circle, 0, Qt.AlignmentFlag.AlignTop)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)
        self._title = QLabel(step.title)
        self._title.setFont(font_for_role(TypescaleRole.BODY_LARGE))
        text_col.addWidget(self._title)
        self._subtitle = QLabel(step.subtitle)
        self._subtitle.setFont(font_for_role(TypescaleRole.BODY_SMALL))
        self._subtitle.setVisible(bool(step.subtitle))
        text_col.addWidget(self._subtitle)
        lay.addLayout(text_col, 1)

        self.refresh()
        ThemeManager.instance().themeChanged.connect(self.refresh)

    def refresh(self) -> None:
        self.circle.set_state(self._step.state, self._step.active)
        tm = ThemeManager.instance()
        disabled = self._step.state is StepState.DISABLED
        title_role = ColorRole.ON_SURFACE_VARIANT if disabled else ColorRole.ON_SURFACE
        self._title.setStyleSheet(f"color: {tm.color(title_role).name()};")
        self._subtitle.setStyleSheet(
            f"color: {tm.color(ColorRole.ON_SURFACE_VARIANT).name()};"
        )
        tappable = self._step.state is not StepState.DISABLED
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if tappable
            else Qt.CursorShape.ArrowCursor
        )

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if self._step.state is not StepState.DISABLED:
            self.clicked.emit()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        self.paint_material_surface(painter)


class _Connector(QWidget):
    """A thin line drawn between step circles."""

    def __init__(self, *, vertical: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._vertical = vertical
        if vertical:
            self.setFixedWidth(_CONNECTOR)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        else:
            self.setFixedHeight(_CONNECTOR)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        ThemeManager.instance().themeChanged.connect(self.update)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.fillRect(self.rect(), ThemeManager.instance().color(ColorRole.OUTLINE_VARIANT))


class MdStepper(QWidget):
    """A Material 3 stepper (cf. Flutter ``Stepper``).

    Construct with a list of :class:`MdStep` and a :class:`StepperType`. The
    current step's content is shown; tapping a step header emits
    ``stepTapped(int)``; the Continue / Cancel buttons emit ``continued`` /
    ``canceled``.
    """

    stepTapped = Signal(int)  # noqa: N815  (Qt-style signal name)
    continued = Signal()
    canceled = Signal()

    def __init__(
        self,
        steps: list[MdStep] | None = None,
        parent: QWidget | None = None,
        *,
        type: StepperType = StepperType.VERTICAL,  # noqa: A002 (matches Flutter)
        current_step: int = 0,
        show_controls: bool = True,
    ) -> None:
        super().__init__(parent)
        self._steps: list[MdStep] = list(steps) if steps else []
        self._type = type
        self._show_controls = show_controls
        self._current = 0
        self._headers: list[_StepHeader] = []
        self._connectors: list[_Connector] = []

        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(0, 0, 0, 0)
        self._outer.setSpacing(0)
        self._body = QWidget()
        self._outer.addWidget(self._body)

        self._build()
        # Clamp the requested initial step into range.
        if self._steps:
            self._current = max(0, min(current_step, len(self._steps) - 1))
            self._sync_active()
            self._show_current_content()

    # -- public API --------------------------------------------------------

    @property
    def steps(self) -> list[MdStep]:
        return self._steps

    @property
    def type(self) -> StepperType:  # noqa: A003 (matches Flutter)
        return self._type

    @property
    def currentStep(self) -> int:  # noqa: N802 (matches Flutter property name)
        return self._current

    def set_current_step(self, index: int) -> None:
        if not self._steps:
            return
        index = max(0, min(index, len(self._steps) - 1))
        if index == self._current:
            return
        self._current = index
        self._sync_active()
        self._show_current_content()

    def set_step_state(self, index: int, state: StepState) -> None:
        if 0 <= index < len(self._steps):
            self._steps[index].state = state
            self._headers[index].refresh()

    # -- build -------------------------------------------------------------

    def _build(self) -> None:
        self._content_holders: list[QWidget] = []
        if self._type is StepperType.HORIZONTAL:
            self._build_horizontal()
        else:
            self._build_vertical()

    def _make_header(self, i: int) -> _StepHeader:
        header = _StepHeader(i, self._steps[i])
        header.clicked.connect(lambda idx=i: self._on_header_clicked(idx))
        self._headers.append(header)
        return header

    def _make_content_holder(self, i: int) -> QWidget:
        holder = QWidget()
        lay = QVBoxLayout(holder)
        lay.setContentsMargins(0, 8, 0, 8)
        lay.addWidget(self._steps[i].content)
        if self._show_controls:
            lay.addWidget(self._make_controls())
        self._content_holders.append(holder)
        return holder

    def _make_controls(self) -> QWidget:
        bar = QWidget()
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(0, 8, 0, 0)
        lay.setSpacing(8)
        cont = MdTextButton("Continue")
        cont.clicked.connect(self.continued.emit)
        cancel = MdTextButton("Cancel")
        cancel.clicked.connect(self.canceled.emit)
        lay.addWidget(cont)
        lay.addWidget(cancel)
        lay.addStretch(1)
        return bar

    def _build_vertical(self) -> None:
        lay = QVBoxLayout(self._body)
        lay.setContentsMargins(_ROW_PAD, 0, _ROW_PAD, 0)
        lay.setSpacing(0)
        for i in range(len(self._steps)):
            # Row: circle column (circle + connector below) | header + content.
            row = QGridLayout()
            row.setContentsMargins(0, _ROW_PAD // 2, 0, 0)
            row.setHorizontalSpacing(0)
            row.setVerticalSpacing(0)
            header = self._make_header(i)
            row.addWidget(header, 0, 0)
            holder = self._make_content_holder(i)
            row.addWidget(holder, 1, 0)
            lay.addLayout(row)
        lay.addStretch(1)

    def _build_horizontal(self) -> None:
        lay = QVBoxLayout(self._body)
        lay.setContentsMargins(_ROW_PAD, _ROW_PAD // 2, _ROW_PAD, 0)
        lay.setSpacing(0)
        # Header row: circles + titles separated by connectors.
        head_row = QHBoxLayout()
        head_row.setContentsMargins(0, 0, 0, 0)
        head_row.setSpacing(8)
        for i in range(len(self._steps)):
            head_row.addWidget(self._make_header(i), 0)
            if i < len(self._steps) - 1:
                conn = _Connector(vertical=False)
                self._connectors.append(conn)
                head_row.addWidget(conn, 1)
        lay.addLayout(head_row)
        # A single content area below the row; swapped on step change.
        for i in range(len(self._steps)):
            holder = self._make_content_holder(i)
            lay.addWidget(holder)
        lay.addStretch(1)

    # -- state -------------------------------------------------------------

    def _on_header_clicked(self, index: int) -> None:
        self.stepTapped.emit(index)

    def _sync_active(self) -> None:
        for i, header in enumerate(self._headers):
            self._steps[i].active = i == self._current
            header.refresh()

    def _show_current_content(self) -> None:
        for i, holder in enumerate(self._content_holders):
            holder.setVisible(i == self._current)

    # -- sizing ------------------------------------------------------------

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(420, 320)


__all__ = ["MdStep", "MdStepper", "StepState", "StepperType"]
