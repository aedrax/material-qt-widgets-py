"""Material 3 modal date picker for QtWidgets.

Ports the Material 3 modal date picker (cf. Flutter's ``showDatePicker`` /
``CalendarDatePicker``): a modal overlay with an elevated
``surface-container-high`` panel containing a header (supporting label + the
selected date as a headline), a month navigation row, a weekday row, and a 6x7
day grid, with Cancel / OK actions. The selected day is a ``primary`` filled
circle (``on-primary`` text); today is a ``primary`` outline; days outside the
month are blank. ``accepted(QDate)`` fires on OK, ``rejected`` on Cancel/dismiss.

Deferred (scaffold): the docked and text-input variants, and locale-driven
first-day-of-week — the grid is hardcoded Sunday-first.
"""

from __future__ import annotations

from PySide6.QtCore import QDate, QEvent, QObject, QRectF, Qt, QVariantAnimation, Signal
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
from ...core.motion import MOTION_ENABLED, duration_ms, easing_curve
from ...core.typography_util import font_for_role
from ...tokens.color import ColorRole
from ...tokens.elevation import ElevationLevel
from ...tokens.motion import Duration, Easing
from ...tokens.shape import CornerRadii, ShapeScale
from ...tokens.typography import TypescaleRole
from ...theme.theme_manager import ThemeManager
from ..button import MdTextButton
from ..iconbutton import MdIconButton

_SCRIM_OPACITY = 0.32
_PANEL_W = 328
_CELL = 40
_PAD = 12
_WEEKDAYS = ["S", "M", "T", "W", "T", "F", "S"]


def first_column(year: int, month: int) -> int:
    """Grid column (0=Sun .. 6=Sat) the 1st of ``year``/``month`` falls in.

    Qt's ``QDate.dayOfWeek()`` is 1=Mon..7=Sun; ``% 7`` maps it to a
    Sunday-first column (Sun 7->0 .. Sat 6->6).
    """
    return QDate(year, month, 1).dayOfWeek() % 7


class _DayCell(MaterialWidgetMixin, QWidget):
    """A single selectable day in the calendar grid."""

    clicked = Signal(QDate)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._date: QDate | None = None
        self._selected = False
        self._today = False
        self._init_material(
            shape=CornerRadii.uniform(_CELL / 2.0),
            ripple=True,
            focus_ring=False,
            ripple_role=ColorRole.ON_SURFACE,
        )
        self.setFixedSize(_CELL, _CELL)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_day(self, date: QDate | None, *, selected: bool, today: bool) -> None:
        self._date = date
        self._selected = selected
        self._today = today
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if date else Qt.CursorShape.ArrowCursor
        )
        self.update()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if self._date is not None:
            self.clicked.emit(self._date)
        super().mousePressEvent(event)

    def paintEvent(self, event) -> None:  # noqa: N802
        if self._date is None:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        theme = ThemeManager.instance()
        rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)

        if self._selected:
            painter.setBrush(theme.color(ColorRole.PRIMARY))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(rect)
            text_color = theme.color(ColorRole.ON_PRIMARY)
        elif self._today:
            pen = painter.pen()
            pen.setColor(theme.color(ColorRole.PRIMARY))
            pen.setWidthF(1.0)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(rect)
            text_color = theme.color(ColorRole.PRIMARY)
        else:
            text_color = theme.color(ColorRole.ON_SURFACE)

        painter.setFont(font_for_role(TypescaleRole.BODY_MEDIUM))
        painter.setPen(text_color)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                         str(self._date.day()))


class _DatePanel(MaterialWidgetMixin, QWidget):
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


class MdDatePicker(QWidget):
    """A modal date picker overlay."""

    accepted = Signal(QDate)
    rejected = Signal()
    closed = Signal()

    def __init__(self, parent: QWidget, *, initial_date: QDate | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._selected = initial_date or QDate.currentDate()
        self._view = QDate(self._selected.year(), self._selected.month(), 1)

        self._panel = _DatePanel(self)
        self._panel.setFixedWidth(_PANEL_W)
        pl = QVBoxLayout(self._panel)
        pl.setContentsMargins(_PAD, _PAD, _PAD, _PAD)
        pl.setSpacing(8)

        # Header: supporting label + selected date headline.
        self._support = QLabel("Select date")
        self._support.setFont(font_for_role(TypescaleRole.LABEL_MEDIUM))
        self._headline = QLabel()
        self._headline.setFont(font_for_role(TypescaleRole.HEADLINE_MEDIUM))
        pl.addWidget(self._support)
        pl.addWidget(self._headline)

        # Month navigation row.
        nav = QHBoxLayout()
        self._month_label = QLabel()
        self._month_label.setFont(font_for_role(TypescaleRole.TITLE_SMALL))
        prev_btn = MdIconButton("chevron_left")
        next_btn = MdIconButton("chevron_right")
        prev_btn.clicked.connect(lambda: self._shift_month(-1))
        next_btn.clicked.connect(lambda: self._shift_month(1))
        nav.addWidget(self._month_label)
        nav.addStretch(1)
        nav.addWidget(prev_btn)
        nav.addWidget(next_btn)
        pl.addLayout(nav)

        # Weekday header row.
        wk = QHBoxLayout()
        wk.setSpacing(0)
        for d in _WEEKDAYS:
            lbl = QLabel(d)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFixedWidth(_CELL)
            lbl.setFont(font_for_role(TypescaleRole.BODY_SMALL))
            wk.addWidget(lbl)
        wk.addStretch(1)
        pl.addLayout(wk)

        # Day grid (6 rows x 7 cols).
        self._grid = QGridLayout()
        self._grid.setSpacing(0)
        self._cells: list[_DayCell] = []
        for i in range(42):
            cell = _DayCell()
            cell.clicked.connect(self._on_day_clicked)
            self._cells.append(cell)
            self._grid.addWidget(cell, i // 7, i % 7)
        grid_holder = QWidget()
        grid_holder.setLayout(self._grid)
        grid_holder.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        pl.addWidget(grid_holder)

        # Actions.
        actions = QHBoxLayout()
        actions.addStretch(1)
        cancel = MdTextButton("Cancel")
        ok = MdTextButton("OK")
        cancel.clicked.connect(self._on_cancel)
        ok.clicked.connect(self._on_ok)
        actions.addWidget(cancel)
        actions.addWidget(ok)
        pl.addLayout(actions)

        self._fade = 0.0
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(duration_ms(Duration.MEDIUM2))
        self._anim.setEasingCurve(easing_curve(Easing.EMPHASIZED))
        self._anim.valueChanged.connect(self._set_fade)

        parent.installEventFilter(self)
        self._restyle()
        ThemeManager.instance().themeChanged.connect(self._restyle)
        ThemeManager.instance().themeChanged.connect(self.update)
        self._refresh()
        self.hide()

    # -- state -------------------------------------------------------------

    @property
    def selected_date(self) -> QDate:
        return self._selected

    def _shift_month(self, delta: int) -> None:
        self._view = self._view.addMonths(delta)
        self._refresh()

    def _on_day_clicked(self, date: QDate) -> None:
        self._selected = date
        self._refresh()

    def _refresh(self) -> None:
        self._headline.setText(self._selected.toString("ddd, MMM d"))
        self._month_label.setText(self._view.toString("MMMM yyyy"))
        offset = first_column(self._view.year(), self._view.month())
        days = self._view.daysInMonth()
        today = QDate.currentDate()
        for i, cell in enumerate(self._cells):
            day = i - offset + 1
            if 1 <= day <= days:
                date = QDate(self._view.year(), self._view.month(), day)
                cell.set_day(date, selected=date == self._selected,
                             today=date == today)
            else:
                cell.set_day(None, selected=False, today=False)

    def _restyle(self) -> None:
        theme = ThemeManager.instance()
        self._support.setStyleSheet(
            f"color: {theme.color(ColorRole.ON_SURFACE_VARIANT).name()};"
        )
        for lbl, role in (
            (self._headline, ColorRole.ON_SURFACE),
            (self._month_label, ColorRole.ON_SURFACE),
        ):
            lbl.setStyleSheet(f"color: {theme.color(role).name()};")

    # -- open / close ------------------------------------------------------

    def open(self) -> None:
        self.setGeometry(self.parentWidget().rect())
        self._center_panel()
        self.raise_()
        self.show()
        self.setFocus()
        if MOTION_ENABLED:
            self._anim.stop()
            self._anim.setStartValue(0.0)
            self._anim.setEndValue(1.0)
            self._anim.start()
        else:
            self._set_fade(1.0)

    def _on_ok(self) -> None:
        self.accepted.emit(self._selected)
        self._close()

    def _on_cancel(self) -> None:
        self.rejected.emit()
        self._close()

    def _close(self) -> None:
        self.hide()
        self.closed.emit()

    def _set_fade(self, value) -> None:
        self._fade = float(value)
        self._center_panel()
        self.update()

    # -- geometry / scrim --------------------------------------------------

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if obj is self.parentWidget() and event.type() == QEvent.Type.Resize:
            if self.isVisible():
                self.setGeometry(self.parentWidget().rect())
                self._center_panel()
        return False

    def _center_panel(self) -> None:
        self._panel.adjustSize()
        w = self._panel.width()
        h = self._panel.sizeHint().height()
        slide = int((1.0 - self._fade) * 12)
        self._panel.setGeometry(
            int((self.width() - w) / 2),
            int((self.height() - h) / 2) + slide, int(w), int(h),
        )

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._center_panel()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if not self._panel.geometry().contains(event.position().toPoint()):
            self.rejected.emit()
            self._close()

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.rejected.emit()
            self._close()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        scrim = QColor(ThemeManager.instance().color(ColorRole.SCRIM))
        scrim.setAlphaF(_SCRIM_OPACITY * self._fade)
        painter.fillRect(self.rect(), scrim)


__all__ = ["MdDatePicker", "first_column"]
