"""Focus helpers shared by modal overlays.

Hiding a widget that holds focus makes Qt reassign focus to the next widget in
the tab chain with ``TabFocusReason`` — which Material treats as keyboard focus
and shows a lingering focus ring on whatever sibling happens to be next (e.g.
an app-bar icon button). Dropping the focus *before* hiding leaves nothing to
reassign, so no spurious ring appears.
"""

from __future__ import annotations

from PySide6.QtWidgets import QApplication, QWidget


def drop_focus_within(container: QWidget) -> None:
    """Clear focus if it currently sits on ``container`` or a descendant.

    A no-op when focus is elsewhere, so it is safe to call unconditionally
    before hiding any container.
    """
    fw = QApplication.focusWidget()
    if fw is not None and (fw is container or container.isAncestorOf(fw)):
        fw.clearFocus()


__all__ = ["drop_focus_within"]
