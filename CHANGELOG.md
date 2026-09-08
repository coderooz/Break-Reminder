# Changelog

All notable changes to the Break Reminder project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Project governance structure (PRI, AGENTS.md, DEVELOPERS.md)
- MIT License
- CONTRIBUTING.md with contribution guidelines
- SECURITY.md with security policy
- CODE_OF_CONDUCT.md
- GitHub issue templates and CI workflow
- Architecture documentation in docs/
- Comprehensive README with installation, usage, and development instructions

### Changed
- Improved .gitignore to exclude MCP runtime files and workspace artifacts

## [1.0.0] - 2025-11-22

### Added
- Initial release of Break Reminder
- System tray application with PySide6 GUI
- Background daemon for break timing with idle detection
- Configurable active/rest minutes via settings UI
- Windows toast notifications with custom sound support
- Windows autostart via registry (HKCU Run key)
- Pause/Resume functionality from system tray
- Settings persistence via JSON file
- PyInstaller build configuration (main.spec)
- Custom application icon and break notification sound

### Known Limitations
- Windows-only (uses WinAPI for idle detection and registry for autostart)
- No system-wide hotkey support
- No break history/statistics tracking
- No configurable notification sounds per-break
