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


def test_focus_ring_overlay_is_never_top_level(qtbot):
    """Regression: the focus-ring overlay must be parented (to the host), not a
    parentless top-level window — otherwise it flashes as a separate OS window
    (e.g. during a responsive reparent). host.parentWidget() is None at
    construction, so the overlay must NOT be parented to it then."""
    from material_qt.widgets.button import MdFilledButton

    b = MdFilledButton("X")  # constructed with no parent
    qtbot.addWidget(b)
    ov = b.focus_ring.overlay
    assert ov.parentWidget() is not None
    assert not ov.isWindow()
