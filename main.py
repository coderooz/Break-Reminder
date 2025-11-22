import sys
import json
import threading
import os
import winreg

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QSpinBox,
    QCheckBox,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QSystemTrayIcon,
    QMenu,
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt

from daemon import daemon  # BreakDaemon instance


# --------------------------------------------------------------------
# Paths & settings helpers
# --------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICON_PATH = os.path.join(ASSETS_DIR, "icon.ico")


def ensure_settings_file() -> None:
    """Create settings.json with defaults if it doesn't exist or is invalid."""
    defaults = {
        "active_minutes": 45,
        "rest_minutes": 10,
        "autostart": False,
    }
    if not os.path.exists(SETTINGS_FILE):
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(defaults, f, indent=2)
        return

    # If file exists but is corrupted, reset to defaults
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "active_minutes" not in data or "rest_minutes" not in data:
            raise ValueError("Invalid settings structure")
    except Exception:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(defaults, f, indent=2)


def load_settings() -> dict:
    """Load settings with sane defaults and normalization."""
    defaults = {
        "active_minutes": 45,
        "rest_minutes": 10,
        "autostart": False,
    }
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return defaults

    defaults.update({k: v for k, v in data.items() if k in defaults})
    return defaults


def save_settings(active: int, rest: int, autostart: bool) -> None:
    data = {
        "active_minutes": int(active),
        "rest_minutes": int(rest),
        "autostart": bool(autostart),
    }
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def enable_autostart(enabled: bool) -> None:
    """Add/remove app from HKCU Run for current user."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "BreakReminder"

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
    except OSError:
        return

    if enabled:
        if getattr(sys, "frozen", False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(sys.argv[0])

        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
    else:
        try:
            winreg.DeleteValue(key, app_name)
        except OSError:
            pass


# --------------------------------------------------------------------
# Settings Window
# --------------------------------------------------------------------
class SettingsUI(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Break Reminder Settings")
        self.setFixedSize(320, 260)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        settings = load_settings()

        self.activeBox = QSpinBox(self)
        self.activeBox.setRange(1, 24 * 60)
        self.activeBox.setValue(settings["active_minutes"])

        self.restBox = QSpinBox(self)
        self.restBox.setRange(1, 24 * 60)
        self.restBox.setValue(settings["rest_minutes"])

        self.autoCheck = QCheckBox("Start automatically when Windows boots", self)
        self.autoCheck.setChecked(settings.get("autostart", False))

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QLabel("Active (minutes):"))
        layout.addWidget(self.activeBox)

        layout.addWidget(QLabel("Rest (minutes):"))
        layout.addWidget(self.restBox)

        layout.addSpacing(8)
        layout.addWidget(self.autoCheck)

        layout.addSpacing(16)
        btn = QPushButton("Save", self)
        btn.clicked.connect(self.save_changes)
        layout.addWidget(btn)

    def save_changes(self) -> None:
        active = self.activeBox.value()
        rest = self.restBox.value()
        autostart = self.autoCheck.isChecked()

        save_settings(active, rest, autostart)
        enable_autostart(autostart)

        QMessageBox.information(self, "Saved", "Settings saved successfully!")


# --------------------------------------------------------------------
# Tray Application wrapper
# --------------------------------------------------------------------
class TrayApp:
    def __init__(self, app: QApplication) -> None:
        self.app = app
        self.settings_window: SettingsUI | None = None

        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(
                None,
                "Error",
                "System tray is not available on this system.\n"
                "Break Reminder cannot run.",
            )
            sys.exit(1)

        if os.path.exists(ICON_PATH):
            icon = QIcon(ICON_PATH)
        else:
            icon = QIcon()

        self.tray = QSystemTrayIcon(icon, self.app)
        self.tray.setToolTip("Break Reminder")

        menu = QMenu()
        action_settings = QAction("Settings", self.tray)
        action_pause = QAction("Pause", self.tray)
        action_resume = QAction("Resume", self.tray)
        action_quit = QAction("Quit", self.tray)

        action_settings.triggered.connect(self.open_settings)
        action_pause.triggered.connect(lambda: setattr(daemon, "paused", True))
        action_resume.triggered.connect(lambda: setattr(daemon, "paused", False))
        action_quit.triggered.connect(self.exit)

        menu.addAction(action_settings)
        menu.addSeparator()
        menu.addAction(action_pause)
        menu.addAction(action_resume)
        menu.addSeparator()
        menu.addAction(action_quit)

        self.tray.setContextMenu(menu)

        # Double-click tray icon to open settings
        self.tray.activated.connect(self._on_tray_activated)

        self.tray.show()

        # Show a balloon on startup so you *see* that it's running
        self.tray.showMessage(
            "Break Reminder",
            "Running in the background. Right-click this icon for options.",
            QSystemTrayIcon.Information,
            3000,
        )

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.DoubleClick:
            self.open_settings()

    def open_settings(self) -> None:
        if self.settings_window is None:
            self.settings_window = SettingsUI()
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def exit(self) -> None:
        daemon.running = False
        self.tray.hide()
        self.app.quit()


# --------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------
if __name__ == "__main__":
    print("Starting Break Reminder...")
    print("Base directory:", BASE_DIR)
    print("Icon path:", ICON_PATH)

    try:
        ensure_settings_file()

        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)

        tray_app = TrayApp(app)

        # Start background daemon thread AFTER tray is created so
        # if daemon crashes, you still see the tray.
        t = threading.Thread(target=daemon.run, daemon=True)
        t.start()

        sys.exit(app.exec())

    except Exception as e:
        # Catch anything unexpected so it doesn't just "do nothing"
        import traceback

        print("Fatal error in main.py:", e)
        traceback.print_exc()
        input("Press Enter to exit...")
