"""Focus-ring overlay lifetime: the overlay is reparented to the host's
parent on first show, so it must be torn down with the host or it paints
against a dead C++ object (historically a segfault) and leaks per host."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget
from shiboken6 import isValid

from material_qt.core.focus_ring import _FocusOverlay
from material_qt.widgets.button import MdFilledButton


def _shown_host(qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    btn = MdFilledButton("X", parent)
    btn.setGeometry(10, 10, 80, 40)
    parent.show()
    return parent, btn


def test_overlay_deleted_with_host_while_ring_visible(qtbot):
    parent, btn = _shown_host(qtbot)
    btn.focus_ring.show_ring()
    overlay = btn.focus_ring.overlay
    assert overlay.parentWidget() is parent  # reparented on show
    assert not overlay.isHidden()

    btn.deleteLater()
    qtbot.wait(20)  # host destruction + overlay's own deferred delete

    assert not isValid(overlay) or overlay.isHidden()
    # Must not raise (previously: RuntimeError mid-paint -> segfault).
    parent.repaint()


def test_overlays_do_not_accumulate_on_parent(qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    parent.show()
    for _ in range(5):
        btn = MdFilledButton("X", parent)
        btn.setGeometry(10, 10, 80, 40)
        btn.show()
        btn.focus_ring.show_ring()
        btn.focus_ring.hide_ring()
        btn.deleteLater()
    qtbot.wait(20)
    leftovers = [c for c in parent.children() if isinstance(c, _FocusOverlay)]
    assert leftovers == []
