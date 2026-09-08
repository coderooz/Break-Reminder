# Break Reminder — Architecture Overview

## Overview

Break Reminder is a lightweight Windows desktop utility that monitors active computer usage and reminds users to take regular breaks. It runs as a system tray application with a background daemon that tracks time and sends toast notifications.

## System Architecture

```
┌─────────────────────────────────────────────┐
│                  OS Layer                    │
│  ┌────────────┐  ┌───────────────────────┐  │
│  │  WinAPI     │  │  Windows Registry     │  │
│  │  (idle      │  │  (autostart)          │  │
│  │   detect)   │  │                       │  │
│  └──────┬─────┘  └───────────┬───────────┘  │
│         │                    │               │
│  ┌──────┴────────────────────┴───────────┐  │
│  │         Application Layer              │  │
│  │                                        │  │
│  │  ┌──────────┐      ┌───────────────┐  │  │
│  │  │ main.py  │──────│  daemon.py    │  │  │
│  │  │ (GUI)    │      │  (Background) │  │  │
│  │  └──────────┘      └───────────────┘  │  │
│  │        │                    │          │  │
│  │  ┌─────┴─────┐      ┌─────┴────────┐ │  │
│  │  │  PySide6  │      │   winotify   │ │  │
│  │  │  (Qt 6)   │      │  (toasts)    │ │  │
│  │  └───────────┘      └──────────────┘ │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │              Data Layer                 │  │
│  │  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │ settings.json│  │  assets/       │  │  │
│  │  │ (config)     │  │  (icon, sound) │  │  │
│  │  └──────────────┘  └────────────────┘  │  │
│  └────────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

## Module Responsibilities

### main.py — GUI Layer

| Component | Responsibility |
|-----------|---------------|
| `SettingsUI` | Settings window (active/rest minutes, autostart toggle) |
| `TrayApp` | System tray icon, context menu, application lifecycle |
| `enable_autostart()` | Windows Registry autostart management |
| `load_settings()` / `save_settings()` | Settings persistence |

### daemon.py — Background Layer

| Component | Responsibility |
|-----------|---------------|
| `BreakDaemon` | Main timer loop (active period → rest period) |
| `get_idle_time_seconds()` | WinAPI idle time detection |
| `notify()` | Windows toast notification dispatch |
| `load_settings()` | Settings loading (independent copy) |

## Data Flow

```
User interacts with tray menu
        │
        ▼
TrayApp reads/writes settings.json
        │
        ▼
BreakDaemon reads settings.json each cycle
        │
        ▼
Timer tracks active time (1s intervals)
        │
        ├── If idle > 5min: reset timer
        │
        ├── If active time expired: send notification
        │
        └── If rest period: wait, then restart cycle
```

## Threading Model

- **Main thread:** PySide6 event loop (tray, settings window)
- **Daemon thread:** Background timer (breaks, notifications, idle detection)
- **Communication:** Direct attribute access on shared `BreakDaemon` singleton

The daemon thread is marked `daemon=True` (Python thread), ensuring it terminates when the main thread exits.

## Configuration System

Settings are stored in `settings.json` and read by both modules independently:

| Key | Type | Default | Range |
|-----|------|---------|-------|
| `active_minutes` | int | 45 | 1-1440 |
| `rest_minutes` | int | 10 | 1-1440 |
| `autostart` | bool | false | — |

Settings changes take effect within 1 second (next daemon cycle reads the file).

## Platform Dependencies

| Dependency | Usage | Alternative |
|------------|-------|-------------|
| WinAPI (ctypes) | Idle time detection | None (Windows-only) |
| Windows Registry | Autostart | Manual startup folder |
| winotify | Toast notifications | None (Windows-only) |
| PySide6 | GUI | tkinter (not used) |

## Security Model

- No network communication
- No data leaves the local machine
- Registry access limited to HKCU (current user)
- No elevated privileges required
