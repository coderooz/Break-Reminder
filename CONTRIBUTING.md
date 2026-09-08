# Contributing to Break Reminder

Thank you for your interest in contributing to Break Reminder! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Open a new issue with the **Bug Report** template
3. Include:
   - Windows version
   - Python version
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable

### Suggesting Features

1. Open a new issue with the **Feature Request** template
2. Describe the use case and expected behavior
3. Consider if the feature fits the project's scope (lightweight desktop utility)

### Submitting Changes

1. Fork the repository
2. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes following the code standards below
4. Test your changes on Windows
5. Commit with a clear message following [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   feat: add break history tracking
   fix: resolve notification sound not playing
   docs: update installation instructions
   ```
6. Push to your fork and open a Pull Request

## Code Standards

### Python Style

- Follow PEP 8 conventions
- Use type hints for function signatures
- Use `snake_case` for functions/variables, `PascalCase` for classes
- Keep functions focused and reasonably short
- Add docstrings for public functions and classes

### Architecture

- **`main.py`** — GUI layer (PySide6 tray app, settings window)
- **`daemon.py`** — Background logic (timer, idle detection, notifications)
- Keep GUI and daemon logic separated
- Daemon runs in a separate thread, communicates via shared state

### Dependencies

- Only add dependencies with clear justification
- Prefer well-maintained, lightweight libraries
- Update `requirements.txt` when adding/changing dependencies

### Testing

- Test on Windows 10/11 before submitting
- Verify system tray functionality
- Test settings save/load cycle
- Test autostart toggle
- Test pause/resume functionality

## Development Setup

See [DEVELOPERS.md](DEVELOPERS.md) for detailed development environment setup instructions.

## Pull Request Guidelines

- Keep PRs focused on a single change
- Include a clear description of what changed and why
- Reference any related issues
- Ensure the application builds and runs correctly
- Update documentation if your change affects user-facing behavior

## Code of Conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Questions?

Open an issue with the **Question** label or reach out via the project's GitHub Discussions.
