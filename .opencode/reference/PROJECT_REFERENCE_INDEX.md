# Project Reference Index

**Reference Metadata**

| Field | Value |
|-------|-------|
| Name | PROJECT_REFERENCE_INDEX |
| Version | 1.0 |
| Status | active |
| Last Verified | 2026-09-08 |
| Verification Type | FULL |

---

## 1. Project Identity

| Field | Value |
|-------|-------|
| Name | Break Reminder |
| Type | Desktop Application (Windows) |
| Language | Python |
| Framework | PySide6 (Qt for Python) |
| Author | Ranit Saha (Coderooz) |
| License | MIT |
| Repository | https://github.com/coderooz/Break-Reminder |
| Initial Release | 2025-11-22 |

---

## 2. Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.x |
| GUI Framework | PySide6 (Qt 6) |
| Notifications | winotify (Windows toast notifications) |
| Idle Detection | WinAPI via ctypes (GetLastInputInfo) |
| Settings | JSON (local file) |
| Build | PyInstaller |
| Platform | Windows 10/11 |

---

## 3. Root Structure

```
break-reminder/
├── .git/
├── .github/                    # GitHub templates and CI
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── workflows/
│       └── ci.yml
├── .opencode/
│   └── reference/
│       └── PROJECT_REFERENCE_INDEX.md   # This file
├── .workspace/                 # Development artifacts (not committed)
├── assets/                     # Application assets
│   ├── icon.ico               # Application icon
│   └── break.wav              # Break notification sound
├── docs/                       # Project documentation
│   └── Architecture/
├── .gitignore
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── DEVELOPERS.md
├── LICENSE                     # MIT License
├── README.md
├── SECURITY.md
├── daemon.py                   # Background break timer daemon
├── main.py                     # Application entry point and GUI
├── main.spec                   # PyInstaller build configuration
├── requirements.txt            # Python dependencies
└── settings.json               # User settings (runtime)
```

---

## 4. Directory Reference

### `assets/`

Type: Application assets

Purpose: Contains icon and sound files used by the application at runtime.

Contains:
- `icon.ico` — Application icon (system tray and window)
- `break.wav` — Custom notification sound for break reminders

### `docs/`

Type: Project documentation

Purpose: Architecture and design documentation for developers.

### `.github/`

Type: GitHub configuration

Purpose: Issue templates and CI workflow definitions.

### `.opencode/reference/`

Type: OpenCode project reference

Purpose: Project Reference Index for navigation and structural reference.

### `.workspace/`

Type: Development workspace (git-ignored)

Purpose: Temporary development artifacts, reports, and session data.

---

## 5. File Reference

### `main.py`

Type: Application entry point

Purpose: Main entry point for the Break Reminder application. Contains the GUI layer.

Responsibilities:
- Application initialization and lifecycle management
- System tray icon and context menu (Settings, Pause, Resume, Quit)
- Settings window UI (PySide6 QWidget)
- Settings persistence (load/save to `settings.json`)
- Windows autostart registry management (HKCU Run key)
- Background daemon thread management

Dependencies:
- `daemon.py` — BreakDaemon singleton
- PySide6 — GUI framework
- winreg — Windows registry access for autostart

Layer: Application / GUI

### `daemon.py`

Type: Background daemon module

Purpose: Core break-timing logic and idle detection.

Responsibilities:
- Active/rest period timing loop
- Windows idle time detection via WinAPI (GetLastInputInfo)
- Settings loading from `settings.json`
- Windows toast notification dispatch
- Pause/resume state management

Dependencies:
- winotify — Windows toast notifications
- ctypes — WinAPI access for idle detection
- `settings.json` — Runtime configuration

Layer: Background / Timer

### `settings.json`

Type: Runtime configuration

Purpose: User-configurable settings persisted as JSON.

Default values:
```json
{
  "active_minutes": 45,
  "rest_minutes": 10,
  "autostart": false
}
```

### `main.spec`

Type: PyInstaller build configuration

Purpose: Defines how PyInstaller packages the application into a standalone executable.

Key configuration:
- Entry point: `main.py`
- Bundled data: `settings.json`, `assets/icon.ico`, `assets/break.wav`
- Output: Single-file executable (`console=False`)

### `requirements.txt`

Type: Dependency manifest

Purpose: Lists Python package dependencies for pip installation.

Contents:
```
PySide6
winotify
```

### `.gitignore`

Type: Git configuration

Purpose: Excludes build artifacts, virtual environments, IDE files, MCP runtime files, and workspace from version control.

---

## 6. Application Architecture

### Architecture Pattern

Single-user desktop utility with threaded daemon architecture:

```
┌─────────────────────────────────────┐
│           main.py (GUI)             │
│                                     │
│  ┌─────────────┐  ┌──────────────┐ │
│  │  TrayApp     │  │  SettingsUI  │ │
│  │  (System     │  │  (Config     │ │
│  │   Tray)      │  │   Window)    │ │
│  └──────┬──────┘  └──────────────┘ │
│         │                           │
│    ┌────┴────┐                      │
│    │ Thread  │                      │
│    └────┬────┘                      │
│         │                           │
└─────────┼───────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│         daemon.py (Background)      │
│                                     │
│  ┌──────────────────────────────┐   │
│  │       BreakDaemon            │   │
│  │  - Active period timer       │   │
│  │  - Idle time detection       │   │
│  │  - Rest period timer         │   │
│  │  - Toast notifications       │   │
│  └──────────────────────────────┘   │
│                                     │
│  State: running, paused             │
│  Communication: Shared singleton    │
└─────────────────────────────────────┘
```

### Communication Flow

1. `main.py` creates `TrayApp` (system tray) and starts `BreakDaemon.run()` in a daemon thread
2. User interacts via tray menu (Settings / Pause / Resume / Quit)
3. Settings changes are written to `settings.json` and read by daemon on next cycle
4. Daemon detects idle time via WinAPI; resets timer if user idle > 5 minutes
5. When active period expires, daemon sends Windows toast notification
6. Quit signal sets `daemon.running = False`, thread exits

---

## 7. Entry Points

| Entry Point | File | Purpose |
|-------------|------|---------|
| Application | `main.py` | Primary entry point (run directly or via PyInstaller executable) |
| Daemon | `daemon.py` | Background timer (started as thread by main.py) |
| Build | `main.spec` | PyInstaller build configuration |

---

## 8. Configuration

### `settings.json`

File: `settings.json`

Purpose: User-configurable application settings.

Fields:
- `active_minutes` (int, 1-1440): Minutes of active work before break reminder
- `rest_minutes` (int, 1-1440): Minutes for rest period
- `autostart` (bool): Whether to start on Windows login

Default: `{ "active_minutes": 45, "rest_minutes": 10, "autostart": false }`

### Windows Registry

Key: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`

Value: `BreakReminder` (REG_SZ) — Path to executable

Purpose: Windows autostart on user login.

---

## 9. Scripts & Commands

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run from source
python main.py
```

### Build

```bash
# Build standalone executable
pyinstaller main.spec

# Output: dist/main.exe
```

---

## 10. Dependencies

### Runtime Dependencies

| Package | Purpose | Notes |
|---------|---------|-------|
| PySide6 | Qt 6 GUI framework | System tray, settings window |
| winotify | Windows toast notifications | Lightweight wrapper |

### System Dependencies

| Dependency | Purpose |
|------------|---------|
| Windows 10/11 | Platform requirement |
| Python 3.x | Runtime (if running from source) |
| WinAPI (ctypes) | Idle time detection |
| Windows Registry | Autostart feature |

---

## 11. Assets

| File | Type | Purpose |
|------|------|---------|
| `assets/icon.ico` | ICO image | Application icon (system tray, window) |
| `assets/break.wav` | WAV audio | Custom notification sound |

---

## 12. Known Constraints

- **Windows-only**: Uses WinAPI for idle detection and Windows Registry for autostart
- **No cross-platform support**: Cannot run on macOS or Linux
- **No hotkey support**: No global keyboard shortcuts
- **No statistics**: No break history or usage tracking
- **Single-user**: No multi-user or network features

---

## 13. Reference Maintenance Log

### 2026-09-08

Change: Initial PRI creation

Classification: ADDED

Updated:
- Complete project structure documented
- All source files documented
- Architecture diagram created
- Configuration reference added
- Dependencies listed

Verification: FULL
