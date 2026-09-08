# Developer Notes — Break Reminder

This document provides technical reference for developers working on the Break Reminder project.

---

## Quick Start

### Prerequisites

- Windows 10 or 11
- Python 3.8+ (recommended: 3.11+)
- pip (Python package manager)

### Setup

```bash
# Clone the repository
git clone https://github.com/coderooz/Break-Reminder.git
cd Break-Reminder

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Build Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build using the provided spec file
pyinstaller main.spec

# Output: dist/main.exe
```

---

## Project Architecture

### Two-Module Design

The application is split into two modules with clear separation of concerns:

| Module | Layer | Responsibility |
|--------|-------|----------------|
| `main.py` | GUI | System tray, settings window, application lifecycle |
| `daemon.py` | Background | Break timer, idle detection, notifications |

### Thread Model

```
Main Thread (PySide6 event loop)
├── System tray icon
├── Settings window
└── Daemon Thread (background)
    ├── Active period timer (1s tick)
    ├── Idle time detection (WinAPI)
    ├── Rest period timer
    └── Toast notifications
```

**Communication:** The daemon is accessed via a module-level singleton (`daemon.py:daemon`). State changes (`paused`, `running`) are set directly on the singleton from the GUI thread.

### Why Threaded?

- PySide6's event loop is blocking — the daemon must run in a background thread
- The daemon thread is marked `daemon=True` so it exits when the main thread exits
- Shared state (`paused`, `running`) uses simple boolean flags (GIL-protected)

---

## Key Components

### Settings Management

**File:** `main.py` (lines 34-82)

Settings are stored in `settings.json` next to the executable:

```json
{
  "active_minutes": 45,
  "rest_minutes": 10,
  "autostart": false
}
```

**Key functions:**
- `ensure_settings_file()` — Creates defaults if missing or corrupted
- `load_settings()` — Loads with fallback defaults
- `save_settings()` — Writes settings to disk

**Important:** Settings are read by the daemon on each timer cycle, so changes take effect within 1 second without restart.

### Autostart

**File:** `main.py` (lines 85-106)

Uses Windows Registry `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`:
- `enable_autostart(True)` — Writes executable path to registry
- `enable_autostart(False)` — Removes the registry entry
- Handles both frozen (PyInstaller) and development (Python script) modes

### Idle Detection

**File:** `daemon.py` (lines 38-58)

Uses WinAPI via ctypes:
- `GetLastInputInfo()` — Gets timestamp of last user input
- `GetTickCount()` — Gets current system uptime
- Returns idle time in seconds

**Behavior:** If user is idle for > 300 seconds (5 minutes), the active timer resets to 0. This prevents false break reminders when the user walks away.

### Notification System

**File:** `daemon.py` (lines 64-85)

Uses `winotify` library:
- Shows Windows toast notification with app icon
- Plays custom sound (`assets/break.wav`) if available
- Falls back to system default sound

---

## Development Workflow

### Code Conventions

- **Python style:** PEP 8
- **Type hints:** Use for function signatures
- **Naming:** `snake_case` for functions/variables, `PascalCase` for classes
- **Imports:** Group as stdlib → third-party → local
- **Comments:** Minimal; docstrings for public APIs

### Testing Checklist

Before submitting changes, verify:

- [ ] Application starts and shows system tray icon
- [ ] Right-click tray menu works (Settings, Pause, Resume, Quit)
- [ ] Settings window opens and displays current values
- [ ] Settings save/load cycle works correctly
- [ ] Active timer counts down and triggers notification
- [ ] Notification sound plays
- [ ] Pause/Resume functionality works
- [ ] Quit cleanly exits the application
- [ ] Autostart toggle modifies registry correctly
- [ ] Idle detection resets timer when user is away
- [ ] Application builds with PyInstaller successfully

### Common Issues

**Notification not showing:**
- Check if Windows Focus Assist / Do Not Disturb is enabled
- Verify `assets/icon.ico` exists
- Try running from command line to see stdout output

**Autostart not working:**
- Verify registry key exists: `reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v BreakReminder`
- Check if running from a network path (autostart requires local path)

**Daemon not responding:**
- The daemon thread exits when `daemon.running = False`
- If the tray app crashes, the daemon thread (being daemon=True) exits automatically

---

## File Modification Guide

### Adding a New Feature

1. **GUI feature** → Add to `main.py` in the `SettingsUI` or `TrayApp` class
2. **Background feature** → Add to `daemon.py` in the `BreakDaemon` class
3. **New settings** → Update `ensure_settings_file()` defaults and `load_settings()` defaults
4. **New asset** → Place in `assets/` and update `main.spec` datas if needed

### Changing Settings Schema

1. Update defaults in `ensure_settings_file()` (main.py)
2. Update defaults in `load_settings()` (main.py)
3. Update defaults in `load_settings()` (daemon.py) — duplicate for daemon independence
4. Add UI elements in `SettingsUI.__init__()` (main.py)
5. Update save logic in `SettingsUI.save_changes()` (main.py)
6. Update `main.spec` if bundling new files

### Modifying the Daemon Loop

The daemon loop in `BreakDaemon.run()` follows this pattern:

```
while running:
    load settings
    for active_seconds:
        if not paused:
            check idle time
            if idle > 5min: reset timer
            else: increment timer
        sleep 1s
    
    if not paused:
        send notification
        for rest_seconds:
            sleep 1s
```

**Caution:** The daemon sleeps in 1-second intervals. Long-running operations in the loop will delay break reminders.

---

## Build System

### PyInstaller Configuration (`main.spec`)

- **Entry:** `main.py`
- **Bundled data:** `settings.json`, `assets/icon.ico`, `assets/break.wav`
- **Output:** Single-file executable (console hidden)
- **UPX compression:** Enabled

### Build Commands

```bash
# Standard build
pyinstaller main.spec

# Clean build
Remove-Item -Recurse -Force build, dist
pyinstaller main.spec
```

### Output

- `dist/main.exe` — Standalone executable (~15-25 MB)
- Can be distributed without Python installed
- Requires Windows 10+ at runtime

---

## Dependency Details

### PySide6

- Qt 6 bindings for Python
- Provides: QApplication, QWidget, QSystemTrayIcon, QMenu, QIcon, etc.
- License: LGPL (compatible with MIT project)

### winotify

- Lightweight Windows toast notification wrapper
- Provides: Notification class, audio presets
- License: MIT

---

## Debugging Tips

### Run from Command Line

```bash
python main.py
```

stdout shows:
```
Starting Break Reminder...
Base directory: C:\path\to\project
Icon path: C:\path\to\project\assets\icon.ico
```

### Check Settings

```bash
type settings.json
```

### Check Registry (Autostart)

```bash
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v BreakReminder
```

### Process List

```bash
tasklist | findstr main
```

---

## Governance

This project follows OpenCode governance rules:

- **PRI:** `.opencode/reference/PROJECT_REFERENCE_INDEX.md` — Structural reference
- **MCP Memory:** Session context, decisions, and rationale
- **Reports:** `.workspace/reports/` (git-ignored)

For governance details, see the project's `AGENTS.md` or the global governance files at `~/.config/opencode/`.
