"""Typography utilities: build QFonts from typescale specs and apply to widgets."""

from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget

from ..tokens.typography import REM_PX, TypescaleRole, TypescaleSpec, spec_for

# Material font weights (100..900) -> QFont.Weight integer scale (which is the
# same numeric scale in Qt 6, so we can pass the value directly).
_FALLBACK_FAMILIES = ["Roboto", "Noto Sans", "Segoe UI", "Helvetica Neue", "Arial"]


def font_for(spec: TypescaleSpec) -> QFont:
    """Build a :class:`QFont` from a typescale spec.

    Uses pixel sizing (``size_rem * 16``), numeric weight, and letter spacing
    derived from the tracking token (rem -> px, applied as absolute spacing).
    """
    font = QFont()
    font.setFamily(spec.family)
    font.setFamilies([spec.family, *_FALLBACK_FAMILIES])
    # Round to whole px to avoid sub-pixel font sizes that Qt may ignore.
    font.setPixelSize(max(1, round(spec.size_px)))
    font.setWeight(QFont.Weight(spec.weight))
    # Tracking is an absolute length in px; QFont uses AbsoluteSpacing in px.
    if spec.tracking_px:
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, spec.tracking_px)
    return font


def font_for_role(role: TypescaleRole | str) -> QFont:
    """Build a :class:`QFont` directly from a typescale role."""
    return font_for(spec_for(role))


def apply(widget: QWidget, role: TypescaleRole | str) -> None:
    """Apply the font for ``role`` to ``widget``."""
    widget.setFont(font_for_role(role))


__all__ = ["REM_PX", "apply", "font_for", "font_for_role"]
