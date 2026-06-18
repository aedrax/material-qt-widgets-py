"""Typography font resolution: bundled Roboto must be available."""

from __future__ import annotations

from PySide6.QtGui import QFontDatabase, QFontInfo

from material_qt.core.typography_util import font_for_role


def test_roboto_registered_and_resolved(qtbot):
    # Building any typescale font triggers lazy registration of bundled Roboto.
    font = font_for_role("body-large")
    assert "Roboto" in QFontDatabase.families()
    assert QFontInfo(font).family() == "Roboto"
    assert font.pixelSize() == 16
    assert font.weight() == 400


def test_label_large_is_medium_weight(qtbot):
    font = font_for_role("label-large")
    assert font.weight() == 500
