# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within Break Reminder, please send an email to [contact@coderooz.in](mailto:contact@coderooz.in). All security vulnerabilities will be promptly addressed.

**Please do NOT report security vulnerabilities through public GitHub issues.**

### What to include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response timeline

- **Acknowledgment:** Within 48 hours
- **Initial assessment:** Within 1 week
- **Fix or mitigation:** Depends on severity

## Security Considerations

### Windows Registry Access

Break Reminder uses Windows Registry for the autostart feature (`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`). This is a standard, well-documented Windows pattern for user-level autostart. The application:

- Only modifies the current user's registry hive (HKCU), not HKLM
- Does not require administrator privileges
- Only writes the executable path to enable/disable autostart

### Data Handling

- Settings are stored locally in `settings.json` in the application directory
- No data is transmitted over the network
- No telemetry or analytics are collected
- No user-identifying information is gathered

### Third-Party Dependencies

- **PySide6** — Qt for Python (Qt Company maintained)
- **winotify** — Windows toast notifications (lightweight wrapper)

## Best Practices for Users

- Download only from the official GitHub repository
- Verify the application icon matches the official Break Reminder icon
- Keep the application updated
- Review settings periodically
