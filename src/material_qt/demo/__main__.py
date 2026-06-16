"""``python -m material_qt.demo`` -> a minimal foundation showcase window.

Shows a themed elevated surface, a ripple + focus-ring interactive surface, a
typescale label, and a light/dark toggle. The window is resizable so the
responsive size-class label updates live.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from material_qt.core.material_widget import MaterialWidget
from material_qt.core.responsive import ResponsiveHelper, WindowSizeClass
from material_qt.core.typography_util import apply as apply_typography
from material_qt.tokens.color import ColorRole
from material_qt.tokens.elevation import ElevationLevel
from material_qt.tokens.shape import ShapeScale
from material_qt.tokens.typography import TypescaleRole
from material_qt.theme.theme_manager import ThemeManager, ThemeMode


class TypeLabel(QLabel):
    """A QLabel that themes its text color and applies a typescale role."""

    def __init__(
        self,
        text: str,
        role: TypescaleRole,
        color_role: ColorRole = ColorRole.ON_SURFACE,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(text, parent)
        self._color_role = color_role
        apply_typography(self, role)
        ThemeManager.instance().themeChanged.connect(self._retheme)
        self._retheme()

    def _retheme(self) -> None:
        color = ThemeManager.instance().color(self._color_role)
        self.setStyleSheet(f"color: {color.name()};")


class DemoWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("material-qt — foundation demo")
        self.resize(720, 520)

        theme = ThemeManager.instance()
        theme.set_mode(ThemeMode.LIGHT)

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(24)

        root.addWidget(
            TypeLabel("Material Qt foundation", TypescaleRole.HEADLINE_MEDIUM)
        )
        root.addWidget(
            TypeLabel(
                "Tokens, theme, motion, ripple, focus ring and elevation.",
                TypescaleRole.BODY_LARGE,
                ColorRole.ON_SURFACE_VARIANT,
            )
        )

        # Elevated themed surface.
        surface = MaterialWidget(
            shape=ShapeScale.LARGE,
            elevation=ElevationLevel.LEVEL3,
            ripple=False,
            focus_ring=False,
            surface_role=ColorRole.SURFACE_CONTAINER_HIGH,
        )
        surface.setMinimumHeight(96)
        surface_layout = QVBoxLayout(surface)
        surface_layout.setContentsMargins(20, 20, 20, 20)
        surface_layout.addWidget(
            TypeLabel(
                "Elevated surface (level 3)",
                TypescaleRole.TITLE_MEDIUM,
                ColorRole.ON_SURFACE,
            )
        )
        root.addWidget(surface)

        # Interactive ripple + focus-ring surface.
        interactive = MaterialWidget(
            shape=ShapeScale.FULL,
            elevation=ElevationLevel.LEVEL1,
            ripple=True,
            focus_ring=True,
            ripple_role=ColorRole.PRIMARY,
            surface_role=ColorRole.PRIMARY_CONTAINER,
        )
        interactive.setMinimumSize(220, 56)
        interactive.setMaximumWidth(260)
        il = QHBoxLayout(interactive)
        il.setContentsMargins(16, 8, 16, 8)
        il.addWidget(
            TypeLabel(
                "Hover / click / Tab here",
                TypescaleRole.LABEL_LARGE,
                ColorRole.ON_PRIMARY_CONTAINER,
            ),
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        root.addWidget(interactive, alignment=Qt.AlignmentFlag.AlignLeft)

        # Controls row.
        controls = QHBoxLayout()
        self._toggle = QPushButton("Toggle light / dark")
        self._toggle.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._toggle.clicked.connect(self._toggle_theme)
        controls.addWidget(self._toggle)

        self._size_label = TypeLabel(
            "", TypescaleRole.LABEL_MEDIUM, ColorRole.ON_SURFACE_VARIANT
        )
        controls.addStretch(1)
        controls.addWidget(self._size_label)
        root.addLayout(controls)
        root.addStretch(1)

        # Responsive size-class readout.
        self._responsive = ResponsiveHelper(self)
        self._responsive.sizeClassChanged.connect(self._update_size_label)
        self._update_size_label(self._responsive.size_class)

        # Apply the initial palette so the window background is themed.
        theme.apply_app_palette()
        theme.themeChanged.connect(self._repaint_all)
        self._repaint_all()

    def _toggle_theme(self) -> None:
        ThemeManager.instance().toggle_light_dark()

    def _update_size_label(self, size_class: WindowSizeClass) -> None:
        self._size_label.setText(f"Size class: {size_class.name}  ({self.width()}px)")

    def _repaint_all(self) -> None:
        bg = ThemeManager.instance().color(ColorRole.SURFACE)
        self.setStyleSheet(f"DemoWindow {{ background: {bg.name()}; }}")
        self.update()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._update_size_label(self._responsive.size_class)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.fillRect(self.rect(), ThemeManager.instance().color(ColorRole.SURFACE))


def main() -> int:
    app = QApplication(sys.argv)
    # Re-instantiate the theme manager now that an application exists so it can
    # connect to system style hints.
    ThemeManager.instance()._connect_system_hints()
    window = DemoWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
