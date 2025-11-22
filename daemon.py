import time
import json
import ctypes
import os

from winotify import Notification, audio

# --------------------------------------------------------------------
# Paths & settings
# --------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICON_PATH = os.path.join(ASSETS_DIR, "icon.ico")
SOUND_PATH = os.path.join(ASSETS_DIR, "break.wav")


def load_settings() -> dict:
    """Load settings from JSON with safe defaults."""
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


# --------------------------------------------------------------------
# Idle-time detection using WinAPI
# --------------------------------------------------------------------
def get_idle_time_seconds() -> float:
    """Return idle time in seconds (no keyboard/mouse input)."""

    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_uint),
            ("dwTime", ctypes.c_uint),
        ]

    last_input = LASTINPUTINFO()
    last_input.cbSize = ctypes.sizeof(LASTINPUTINFO)

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    if not user32.GetLastInputInfo(ctypes.byref(last_input)):
        # in case of API failure, treat as no idle time
        return 0.0

    millis = kernel32.GetTickCount() - last_input.dwTime
    return millis / 1000.0


# --------------------------------------------------------------------
# Notification helper
# --------------------------------------------------------------------
def notify(message: str) -> None:
    """Show a Windows toast notification with optional icon and audio."""
    kwargs = {
        "app_id": "Break Reminder",
        "title": "Break Reminder",
        "msg": message,
    }

    if os.path.exists(ICON_PATH):
        kwargs["icon"] = ICON_PATH

    toast = Notification(**kwargs)

    # Prefer custom sound if available
    if os.path.exists(SOUND_PATH):
        # custom audio file~
        toast.set_audio(SOUND_PATH, loop=False)
    else:
        # fallback to a system sound
        toast.set_audio(audio.Default, loop=False)

    toast.show()


# --------------------------------------------------------------------
# Background daemon
# --------------------------------------------------------------------
class BreakDaemon:
    def __init__(self) -> None:
        self.paused: bool = False
        self.running: bool = True

    def run(self) -> None:
        """Main loop: track active time, remind to rest."""
        while self.running:
            settings = load_settings()
            active_s = int(settings["active_minutes"]) * 60
            rest_s = int(settings["rest_minutes"]) * 60

            t = 0
            # Active period
            while t < active_s and self.running:
                if not self.paused:
                    idle = get_idle_time_seconds()
                    # If user has been idle for more than 5 minutes, restart cycle
                    if idle > 300:
                        t = 0
                    else:
                        t += 1
                time.sleep(1)

            if not self.running:
                break

            # Rest period
            if not self.paused and self.running:
                notify(f"Time to rest for {settings['rest_minutes']} minutes 🧘")
                remaining = rest_s
                while remaining > 0 and self.running and not self.paused:
                    time.sleep(1)
                    remaining -= 1


# Singleton instance imported by main.py
daemon = BreakDaemon()
