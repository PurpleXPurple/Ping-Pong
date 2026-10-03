# Desk Pong

A full-screen transparent Pong overlay for Windows. Two paddles and a ball rally across your desktop while everything behind stays visible. Three gamemodes, animated menu, synthesized sound, no assets, no network, no telemetry.

Built with PyQt6. Runs as a single Python file or as a standalone `.exe` with no Python installation required.

---

## Features

- **Transparent full-screen overlay** — your wallpaper stays visible
- **Always on top** — floats above every other window, hidden from the taskbar
- **Three gamemodes** — Classic, Chaos, Crap
- **Animated menu** — pulsing START button, hover/press/click states on every control
- **Synthesized sound** — 14 sounds generated at runtime, no audio files ship
- **Zero dependencies** beyond PyQt6
- **Auto-installer** — installs PyQt6 on first run if missing
- **Instant quit** — Esc kills the process in one syscall

---

## Requirements

### To play the packaged build
- Windows 8, 10, or 11
- No Python, no PyQt6, no runtime installs

### To run from source
- Python 3.9 or newer
- PyQt6 (auto-installed on first launch if missing)

---

## Installation

### Option A — Download the release

Grab `DeskPong.exe` from the [latest release](../../releases/latest). Double-click. Done.

First launch may trigger a Windows SmartScreen prompt ("Windows protected your PC") because the binary isn't code-signed. Click **More info → Run anyway**. This only happens once.

### Option B — Run from source

```bash
git clone https://github.com/your-username/DeskPong.git
cd DeskPong
python DeskPong.py
```
