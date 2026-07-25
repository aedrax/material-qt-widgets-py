"""ColorScheme resolution, light/dark, and ThemeManager signalling."""

from __future__ import annotations

from PySide6.QtGui import QColor

from material_qt.theme.color_scheme import ColorScheme
from material_qt.theme.theme_manager import ThemeManager, ThemeMode
from material_qt.tokens.color import ColorRole


def test_color_scheme_resolves_roles(qapp):
    light = ColorScheme.light()
    dark = ColorScheme.dark()
    assert light.color(ColorRole.PRIMARY) == QColor("#6750a4")
    assert dark.color(ColorRole.PRIMARY) == QColor("#d0bcff")
    assert not light.is_dark
    assert dark.is_dark


def test_color_scheme_cached(qapp):
    assert ColorScheme.light() is ColorScheme.light()
    assert ColorScheme.dark() is ColorScheme.dark()
    assert ColorScheme.for_mode(dark=True) is ColorScheme.dark()


def test_color_scheme_returns_copies(qapp):
    light = ColorScheme.light()
    c1 = light.color(ColorRole.PRIMARY)
    c1.setAlphaF(0.5)
    c2 = light.color(ColorRole.PRIMARY)
    assert c2.alphaF() == 1.0  # mutation did not leak into the scheme


def test_theme_manager_mode_switch_signals(qapp):
    tm = ThemeManager.instance()
    tm.set_mode(ThemeMode.LIGHT)
    received = []
    tm.themeChanged.connect(lambda: received.append(tm.is_dark))

    tm.set_mode(ThemeMode.DARK)
    assert tm.is_dark is True
    assert received == [True]

    tm.set_mode(ThemeMode.LIGHT)
    assert tm.is_dark is False
    assert received == [True, False]


def test_theme_manager_no_signal_when_unchanged(qapp):
    tm = ThemeManager.instance()
    tm.set_mode(ThemeMode.LIGHT)
    received = []
    tm.themeChanged.connect(lambda: received.append(1))
    tm.set_mode(ThemeMode.LIGHT)  # same mode -> same scheme
    assert received == []


def test_theme_manager_color(qapp):
    tm = ThemeManager.instance()
    tm.set_mode(ThemeMode.DARK)
    assert tm.color(ColorRole.PRIMARY) == QColor("#d0bcff")


def test_apply_app_palette(qapp):
    from PySide6.QtGui import QPalette

    tm = ThemeManager.instance()
    tm.set_mode(ThemeMode.LIGHT)
    tm.apply_app_palette(qapp)
    palette = qapp.palette()
    assert palette.color(QPalette.ColorRole.Highlight) == QColor("#6750a4")
    assert palette.color(QPalette.ColorRole.Base) == QColor("#ffffff")


def test_set_and_clear_color_override(qapp):
    tm = ThemeManager.instance()
    tm.set_mode(ThemeMode.LIGHT)
    tm.clear_overrides()
    signals = []
    tm.themeChanged.connect(lambda: signals.append(1))
    tm.set_overrides({ColorRole.PRIMARY: "#ff0000"})
    assert tm.color(ColorRole.PRIMARY) == QColor("#ff0000")
    assert signals  # themeChanged fired
    tm.clear_overrides()
    assert tm.color(ColorRole.PRIMARY) == QColor("#6750a4")  # back to token value


def test_override_accepts_qcolor_and_str(qapp):
    tm = ThemeManager.instance()
    tm.set_mode(ThemeMode.LIGHT)
    tm.set_overrides({ColorRole.PRIMARY: QColor(0, 128, 128)})
    assert tm.color(ColorRole.PRIMARY) == QColor(0, 128, 128)
    tm.clear_overrides()


def test_per_mode_override(qapp):
    tm = ThemeManager.instance()
    tm.clear_overrides()
    # Override only in dark.
    tm.set_overrides({ColorRole.PRIMARY: "#00ff00"}, mode=ThemeMode.DARK)
    tm.set_mode(ThemeMode.LIGHT)
    assert tm.color(ColorRole.PRIMARY) == QColor("#6750a4")  # light unaffected
    tm.set_mode(ThemeMode.DARK)
    assert tm.color(ColorRole.PRIMARY) == QColor("#00ff00")  # dark overridden
    tm.clear_overrides()
    tm.set_mode(ThemeMode.LIGHT)


def test_override_propagates_to_palette(qapp):
    from PySide6.QtGui import QPalette

    tm = ThemeManager.instance()
    tm.set_mode(ThemeMode.LIGHT)
    tm.set_overrides({ColorRole.PRIMARY: "#ff0000"})
    tm.apply_app_palette(qapp)
    assert qapp.palette().color(QPalette.ColorRole.Highlight) == QColor("#ff0000")
    tm.clear_overrides()
    tm.apply_app_palette(qapp)


class _FakeSignal:
    def __init__(self) -> None:
        self.connections = []

    def connect(self, slot) -> None:
        self.connections.append(slot)


class _FakeHints:
    def __init__(self, signal: _FakeSignal) -> None:
        self.colorSchemeChanged = signal  # mimics Qt naming


class _FakeApp:
    def __init__(self, hints: _FakeHints) -> None:
        self._hints = hints

    def styleHints(self) -> _FakeHints:  # noqa: N802
        return self._hints


def test_system_hints_wiring_retried_after_app_exists(qapp, monkeypatch):
    # Regression: a ThemeManager created before QApplication silently skipped
    # colorSchemeChanged wiring and never retried, so SYSTEM mode never
    # tracked the OS. Public entry points must retry (idempotently).
    from material_qt.theme import theme_manager as mod

    class _NoAppFactory:
        @staticmethod
        def instance():
            return None

    signal = _FakeSignal()
    fake_app = _FakeApp(_FakeHints(signal))

    class _FakeAppFactory:
        @staticmethod
        def instance():
            return fake_app

    saved = ThemeManager._instance
    try:
        ThemeManager._instance = None
        # No app yet: construction cannot wire the hint signal.
        monkeypatch.setattr(mod, "QGuiApplication", _NoAppFactory)
        tm = ThemeManager.instance()
        assert tm._system_hints_connected is False

        # An app appears: first use must wire the signal, exactly once.
        monkeypatch.setattr(mod, "QGuiApplication", _FakeAppFactory)
        tm.color(ColorRole.PRIMARY)
        assert tm._system_hints_connected is True
        assert signal.connections == [tm._on_system_scheme_changed]

        # Idempotent: further uses do not connect again.
        tm.color(ColorRole.SECONDARY)
        tm._connect_system_hints()
        assert len(signal.connections) == 1
    finally:
        ThemeManager._instance = saved


def test_system_hints_wired_at_construction_with_app(qapp):
    saved = ThemeManager._instance
    try:
        ThemeManager._instance = None
        tm = ThemeManager.instance()  # real qapp exists
        assert tm._system_hints_connected is True
    finally:
        ThemeManager._instance = saved


def test_override_repaints_component(qapp):
    from material_qt.widgets.button import MdFilledButton

    tm = ThemeManager.instance()
    tm.set_mode(ThemeMode.LIGHT)
    tm.clear_overrides()
    btn = MdFilledButton("X")
    btn.resize(120, 40)
    before = btn.grab().toImage().pixelColor(60, 20)
    tm.set_overrides({ColorRole.PRIMARY: "#ff0000"})
    after = btn.grab().toImage().pixelColor(60, 20)
    assert before != after  # filled container (primary) changed
    tm.clear_overrides()
