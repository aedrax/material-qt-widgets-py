"""Material 3 modal time picker for QtWidgets.

Ports the Material 3 modal time picker (cf. Flutter's ``showTimePicker``): a modal
overlay with an elevated ``surface-container-high`` panel containing a time
display (selectable hour / minute fields + an AM/PM toggle) and a clock dial.
Clicking or dragging on the dial sets the active field. ``accepted(QTime)`` fires
on OK, ``rejected`` on Cancel/dismiss.

It supports both Material time-picker entry modes (cf. Flutter's
``TimePickerEntryMode``): a **dial** and a **text input** (type the hour/minute),
switched with the keyboard/clock icon button. ``initial_entry_mode`` picks the
starting mode.

The clock dial uses a north-up, clockwise layout: 12 o'clock at the top, 3 to the
right. The screen-vector -> value math (``atan2(dx, -dy)``) is exposed as pure
functions :func:`angle_to_hour` / :func:`angle_to_minute` so the cardinal mapping
is unit-tested (top=12, right=3, bottom=6, left=9).

Deferred (scaffold): the 24-hour dual-ring dial (inner ring) — this is the
12-hour + AM/PM picker only.
"""

from __future__ import annotations

import math

from PySide6.QtCore import QRectF, Qt, QTime, Signal
from PySide6.QtGui import QIntValidator, QPainter, QPen
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QStackedWidget,
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
from ..button import MdTextButton
from ..iconbutton import MdIconButton

_PANEL_W = 328
_DIAL = 256
_OUTER_R = 100  # radius of the (outer) number ring
_INNER_R = 60  # radius of the inner ring (24-hour dial)
_KNOB_R = 20


def angle_to_hour(dx: float, dy: float) -> int:
    """Map a screen vector from the dial center to a clock hour (1..12).

    North is 12 (``dy`` negative is up); angle increases clockwise.
    """
    deg = math.degrees(math.atan2(dx, -dy)) % 360
    h = round(deg / 30) % 12
    return 12 if h == 0 else h


def angle_to_minute(dx: float, dy: float) -> int:
    """Map a screen vector from the dial center to a minute (0..59)."""
    deg = math.degrees(math.atan2(dx, -dy)) % 360
    return round(deg / 6) % 60


def angle_to_hour24(dx: float, dy: float, *, inner: bool) -> int:
    """Map a screen vector to a 24-hour clock hour, picking the ring.

    The dial has two rings of 12 positions: the inner ring is ``12, 1..11`` (top
    is 12) and the outer ring is ``00, 13..23`` (top is 00). ``inner`` selects
    which ring the point fell on (by its distance from the center).
    """
    deg = math.degrees(math.atan2(dx, -dy)) % 360
    p = round(deg / 30) % 12
    if inner:
        return 12 if p == 0 else p
    return 0 if p == 0 else p + 12


def _hour24_layout(h: int) -> tuple[int, bool]:
    """Position (0..11 from top, clockwise) and ``inner`` ring for 24h hour ``h``."""
    if h == 0:
        return 0, False
    if h == 12:
        return 0, True
    if 1 <= h <= 11:
        return h, True
    return h - 12, False  # 13..23 on the outer ring


def _pos(value: int, step_deg: float, cx: float, cy: float, r: float):
    ang = math.radians(value * step_deg)
    return cx + r * math.sin(ang), cy - r * math.cos(ang)


class _ClockDial(QWidget):
    """A clock-face dial; click or drag to set the active value."""

    valueChanged = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._mode = "hour"  # or "minute"
        self._hour = 12
        self._minute = 0
        self._hour24 = False
        self.setFixedSize(_DIAL, _DIAL)
        ThemeManager.instance().themeChanged.connect(self.update)

    def set_mode(self, mode: str) -> None:
        self._mode = mode
        self.update()

    def set_24h(self, on: bool) -> None:
        self._hour24 = on
        self.update()

    def set_values(self, hour: int, minute: int) -> None:
        self._hour, self._minute = hour, minute
        self.update()

    def _center(self):
        return self.width() / 2.0, self.height() / 2.0

    def _apply(self, pos) -> None:
        cx, cy = self._center()
        dx, dy = pos.x() - cx, pos.y() - cy
        if self._mode == "hour":
            if self._hour24:
                inner = math.hypot(dx, dy) <= (_INNER_R + _OUTER_R) / 2.0
                self._hour = angle_to_hour24(dx, dy, inner=inner)
            else:
                self._hour = angle_to_hour(dx, dy)
            self.valueChanged.emit(self._hour)
        else:
            self._minute = angle_to_minute(dx, dy)
            self.valueChanged.emit(self._minute)
        self.update()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        self._apply(event.position())

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        self._apply(event.position())

    def _paint_hand(self, painter: QPainter, cx: float, cy: float,
                    kx: float, ky: float) -> None:
        primary = ThemeManager.instance().color(ColorRole.PRIMARY)
        # Use a fresh solid pen: the caller paints the face with NoPen, and
        # inheriting that style here would silently drop the hand line.
        pen = QPen(primary)
        pen.setWidthF(2.0)
        painter.setPen(pen)
        painter.drawLine(int(cx), int(cy), int(kx), int(ky))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(primary)
        painter.drawEllipse(QRectF(cx - 4, cy - 4, 8, 8))
        painter.drawEllipse(QRectF(kx - _KNOB_R, ky - _KNOB_R, 2 * _KNOB_R, 2 * _KNOB_R))

    def _paint_number(self, painter: QPainter, text: str, x: float, y: float,
                      *, selected: bool) -> None:
        theme = ThemeManager.instance()
        painter.setPen(
            theme.color(ColorRole.ON_PRIMARY if selected else ColorRole.ON_SURFACE)
        )
        painter.drawText(QRectF(x - 20, y - 20, 40, 40),
                         Qt.AlignmentFlag.AlignCenter, text)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        theme = ThemeManager.instance()
        cx, cy = self._center()

        # Face.
        painter.setBrush(theme.color(ColorRole.SURFACE_CONTAINER_HIGHEST))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(0, 0, self.width(), self.height()))
        painter.setFont(font_for_role(TypescaleRole.BODY_LARGE))

        if self._mode == "hour" and self._hour24:
            pos, inner = _hour24_layout(self._hour)
            kx, ky = _pos(pos, 30.0, cx, cy, _INNER_R if inner else _OUTER_R)
            self._paint_hand(painter, cx, cy, kx, ky)
            for p in range(12):  # outer ring: 00, 13..23
                val = 0 if p == 0 else p + 12
                x, y = _pos(p, 30.0, cx, cy, _OUTER_R)
                self._paint_number(painter, f"{val:02d}", x, y, selected=val == self._hour)
            for p in range(12):  # inner ring: 12, 1..11
                val = 12 if p == 0 else p
                x, y = _pos(p, 30.0, cx, cy, _INNER_R)
                self._paint_number(painter, str(val), x, y, selected=val == self._hour)
            return

        if self._mode == "hour":
            value, labels = self._hour, [(h, h % 12) for h in range(1, 13)]
            fmt = str
        else:
            value, labels = self._minute, [(m, m // 5) for m in range(0, 60, 5)]
            fmt = lambda v: f"{v:02d}"  # noqa: E731

        kx, ky = _pos(value, 30.0 if self._mode == "hour" else 6.0, cx, cy, _OUTER_R)
        self._paint_hand(painter, cx, cy, kx, ky)
        for val, ring_index in labels:
            x, y = _pos(ring_index, 30.0, cx, cy, _OUTER_R)
            self._paint_number(painter, fmt(val), x, y, selected=val == value)


class _TimePanel(MaterialWidgetMixin, QWidget):
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


class _FieldLabel(QLabel):
    """A clickable hour/minute field in the time display."""

    clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(font_for_role(TypescaleRole.DISPLAY_MEDIUM))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(96, 80)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        self.clicked.emit()


class MdTimePicker(ModalOverlay):
    """A modal time picker overlay (12-hour dial + AM/PM)."""

    accepted = Signal(QTime)

    def __init__(
        self,
        parent: QWidget,
        *,
        initial_time: QTime | None = None,
        initial_entry_mode: str = "dial",
        hour24: bool = False,
        confirm_text: str = "OK",
        cancel_text: str = "Cancel",
        help_text: str | None = None,
    ) -> None:
        super().__init__(parent)
        t = initial_time or QTime.currentTime()
        self._hour24 = hour24
        # help_text overrides the per-mode label ("Select time" / "Enter time");
        # when given it is shown verbatim in both entry modes (cf. Flutter helpText).
        self._help_text = help_text
        self._is_pm = t.hour() >= 12
        # In 24h mode the dial value IS the hour (0-23); in 12h it's 1-12 + AM/PM.
        self._hour = t.hour() if hour24 else (t.hour() % 12 or 12)
        self._minute = t.minute()
        self._mode = "hour"  # which field the dial edits
        self._entry = "input" if initial_entry_mode == "input" else "dial"

        self._panel = _TimePanel(self)
        self._panel.setFixedWidth(_PANEL_W)
        pl = QVBoxLayout(self._panel)
        pl.setContentsMargins(24, 18, 24, 12)
        pl.setSpacing(16)

        self._support = QLabel()
        self._support.setFont(font_for_role(TypescaleRole.LABEL_MEDIUM))
        pl.addWidget(self._support)

        # Time display: a stacked HH:MM (dial labels vs editable fields) + AM/PM.
        disp = QHBoxLayout()
        disp.setSpacing(8)
        self._display = QStackedWidget()
        self._display.addWidget(self._build_dial_display())   # index 0: dial
        self._display.addWidget(self._build_input_display())  # index 1: input
        disp.addWidget(self._display)
        disp.addLayout(self._build_ampm())
        disp.addStretch(1)
        pl.addLayout(disp)
        if hour24:  # 24-hour clock has no AM/PM selector
            self._am.hide()
            self._pm.hide()

        # Dial (hidden in input mode).
        self._dial = _ClockDial()
        self._dial.set_24h(hour24)
        self._dial.valueChanged.connect(self._on_dial)
        dial_row = QHBoxLayout()
        dial_row.addStretch(1)
        dial_row.addWidget(self._dial)
        dial_row.addStretch(1)
        self._dial_row = QWidget()
        self._dial_row.setLayout(dial_row)
        pl.addWidget(self._dial_row)

        # Actions: entry-mode toggle (left) + Cancel / OK (right).
        actions = QHBoxLayout()
        self._toggle = MdIconButton("keyboard")
        self._toggle.clicked.connect(self._toggle_entry)
        actions.addWidget(self._toggle)
        actions.addStretch(1)
        cancel = MdTextButton(cancel_text)
        ok = MdTextButton(confirm_text)
        cancel.clicked.connect(self._on_cancel)
        ok.clicked.connect(self._on_ok)
        actions.addWidget(cancel)
        actions.addWidget(ok)
        pl.addLayout(actions)

        # Init the overlay first: it sets up _fade, which _apply_entry_mode ->
        # _center_panel relies on.
        self._init_overlay(parent)
        ThemeManager.instance().themeChanged.connect(self._restyle)
        self._restyle()
        self._refresh()
        self._apply_entry_mode()

    # -- display builders --------------------------------------------------

    def _build_dial_display(self) -> QWidget:
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)
        self._hour_field = _FieldLabel()
        self._minute_field = _FieldLabel()
        self._hour_field.clicked.connect(lambda: self._set_mode("hour"))
        self._minute_field.clicked.connect(lambda: self._set_mode("minute"))
        colon = QLabel(":")
        colon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        colon.setFont(font_for_role(TypescaleRole.DISPLAY_MEDIUM))
        row.addWidget(self._hour_field)
        row.addWidget(colon)
        row.addWidget(self._minute_field)
        return w

    def _make_edit(self, validator: QIntValidator) -> QLineEdit:
        e = QLineEdit()
        e.setValidator(validator)
        e.setMaxLength(2)
        e.setAlignment(Qt.AlignmentFlag.AlignCenter)
        e.setFont(font_for_role(TypescaleRole.DISPLAY_MEDIUM))
        e.setFixedSize(96, 80)
        return e

    def _build_input_display(self) -> QWidget:
        w = QWidget()
        outer = QVBoxLayout(w)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(4)
        hour_validator = QIntValidator(0, 23) if self._hour24 else QIntValidator(1, 12)
        self._hour_edit = self._make_edit(hour_validator)
        self._minute_edit = self._make_edit(QIntValidator(0, 59))
        self._hour_edit.textEdited.connect(self._on_edit_hour)
        self._minute_edit.textEdited.connect(self._on_edit_minute)
        colon = QLabel(":")
        colon.setFixedWidth(12)
        colon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        colon.setFont(font_for_role(TypescaleRole.DISPLAY_MEDIUM))
        fields = QHBoxLayout()
        fields.setSpacing(4)
        fields.addWidget(self._hour_edit)
        fields.addWidget(colon)
        fields.addWidget(self._minute_edit)
        labels = QHBoxLayout()
        labels.setSpacing(4)
        self._hour_caption = QLabel("Hour")
        self._minute_caption = QLabel("Minute")
        for cap in (self._hour_caption, self._minute_caption):
            cap.setFixedWidth(96)
            cap.setFont(font_for_role(TypescaleRole.BODY_SMALL))
        labels.addWidget(self._hour_caption)
        labels.addSpacing(12)
        labels.addWidget(self._minute_caption)
        labels.addStretch(1)
        outer.addLayout(fields)
        outer.addLayout(labels)
        return w

    def _build_ampm(self) -> QVBoxLayout:
        box = QVBoxLayout()
        box.setSpacing(0)
        self._am = QLabel("AM")
        self._pm = QLabel("PM")
        for lbl in (self._am, self._pm):
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFont(font_for_role(TypescaleRole.TITLE_MEDIUM))
            lbl.setFixedSize(48, 40)
            lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        self._am.mousePressEvent = lambda e: self._set_pm(False)  # type: ignore[method-assign]
        self._pm.mousePressEvent = lambda e: self._set_pm(True)  # type: ignore[method-assign]
        box.addWidget(self._am)
        box.addWidget(self._pm)
        return box

    # -- state -------------------------------------------------------------

    @property
    def selected_time(self) -> QTime:
        if self._hour24:
            return QTime(self._hour, self._minute)
        h24 = self._hour % 12 + (12 if self._is_pm else 0)
        return QTime(h24, self._minute)

    def _set_mode(self, mode: str) -> None:
        self._mode = mode
        self._dial.set_mode(mode)
        self._refresh()

    def _set_pm(self, pm: bool) -> None:
        self._is_pm = pm
        self._refresh()

    def _on_dial(self, value: int) -> None:
        if self._mode == "hour":
            self._hour = value
        else:
            self._minute = value
        self._refresh()

    def _on_edit_hour(self, text: str) -> None:
        if text:
            lo, hi = (0, 23) if self._hour24 else (1, 12)
            self._hour = max(lo, min(hi, int(text)))
            self._refresh()

    def _on_edit_minute(self, text: str) -> None:
        if text:
            self._minute = max(0, min(59, int(text)))
            self._refresh()

    def _toggle_entry(self) -> None:
        self._entry = "input" if self._entry == "dial" else "dial"
        self._apply_entry_mode()

    def _apply_entry_mode(self) -> None:
        is_input = self._entry == "input"
        self._display.setCurrentIndex(1 if is_input else 0)
        self._dial_row.setVisible(not is_input)
        # Icon shows the mode you can switch TO: keyboard (->input) / clock.
        self._toggle.set_icon("schedule" if is_input else "keyboard")
        if self._help_text is not None:
            self._support.setText(self._help_text)
        else:
            self._support.setText("Enter time" if is_input else "Select time")
        if is_input:
            self._hour_edit.setText(f"{self._hour:02d}")
            self._minute_edit.setText(f"{self._minute:02d}")
        self._refresh()
        self._center_panel()

    def _refresh(self) -> None:
        theme = ThemeManager.instance()
        self._hour_field.setText(f"{self._hour:02d}")
        self._minute_field.setText(f"{self._minute:02d}")
        # Keep input fields in sync, but don't clobber the one being typed in.
        if not self._hour_edit.hasFocus():
            self._hour_edit.setText(f"{self._hour:02d}")
        if not self._minute_edit.hasFocus():
            self._minute_edit.setText(f"{self._minute:02d}")
        self._dial.set_values(self._hour, self._minute)
        self._dial.set_mode(self._mode)

        def field_style(active: bool) -> str:
            bg = ColorRole.PRIMARY_CONTAINER if active else ColorRole.SURFACE_CONTAINER_HIGHEST
            fg = ColorRole.ON_PRIMARY_CONTAINER if active else ColorRole.ON_SURFACE
            return (f"background-color: {theme.color(bg).name()};"
                    f"color: {theme.color(fg).name()}; border-radius: 8px;")

        self._hour_field.setStyleSheet(field_style(self._mode == "hour"))
        self._minute_field.setStyleSheet(field_style(self._mode == "minute"))

        def ampm_style(active: bool) -> str:
            bg = ColorRole.TERTIARY_CONTAINER if active else ColorRole.SURFACE_CONTAINER_HIGH
            fg = ColorRole.ON_TERTIARY_CONTAINER if active else ColorRole.ON_SURFACE_VARIANT
            return (f"background-color: {theme.color(bg).name()};"
                    f"color: {theme.color(fg).name()};")

        self._am.setStyleSheet(ampm_style(not self._is_pm))
        self._pm.setStyleSheet(ampm_style(self._is_pm))

    def _restyle(self) -> None:
        theme = ThemeManager.instance()
        variant = theme.color(ColorRole.ON_SURFACE_VARIANT).name()
        self._support.setStyleSheet(f"color: {variant};")
        self._hour_caption.setStyleSheet(f"color: {variant};")
        self._minute_caption.setStyleSheet(f"color: {variant};")
        edit_css = (
            f"QLineEdit {{ color: {theme.color(ColorRole.ON_SURFACE).name()};"
            f" background: {theme.color(ColorRole.SURFACE_CONTAINER_HIGHEST).name()};"
            f" border: 1px solid {theme.color(ColorRole.OUTLINE).name()};"
            " border-radius: 8px; }"
            f" QLineEdit:focus {{ border: 2px solid {theme.color(ColorRole.PRIMARY).name()}; }}"
        )
        self._hour_edit.setStyleSheet(edit_css)
        self._minute_edit.setStyleSheet(edit_css)

    # -- open / close ------------------------------------------------------

    def _on_ok(self) -> None:
        self.accepted.emit(self.selected_time)
        self._close()

    def _on_cancel(self) -> None:
        self.dismiss()


__all__ = ["MdTimePicker", "angle_to_hour", "angle_to_hour24", "angle_to_minute"]
