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

The first run auto-installs PyQt6 via `pip` and restarts the interpreter. Subsequent runs launch directly.

If you'd rather install manually:

```bash
pip install PyQt6
python DeskPong.py
```

---

## Controls

| Key | Action |
|---|---|
| `↑` / `↓` | Move paddle |
| `W` / `S` | Move paddle (alt) |
| `Esc` | Quit the game instantly |
| `F` | Quit (alias) |
| `Backspace` | Return to the menu |
| Mouse | Click menu items |

### Chaos mode abilities

| Key | Ability | Effect |
|---|---|---|
| `1` or `Z` | Invert | Flip every active ball's horizontal direction |
| `2` or `X` | Overdrive | 1.55× ball speed on both axes |
| `3` or `C` | Recall | Force every ball to head back toward you |
| `4` or `V` | Smash | Only works when a ball is heading to the AI. Locks the ball into a wave pattern at 1.55× speed. If it lands on an AI paddle, that paddle is stunned for 4 seconds. |

Numpad keys work whether or not NumLock is on. The ability bar at the bottom of the screen is also clickable.

### Crap mode

No movement. A ball ping-pongs horizontally. A telegraph ring fills as the ball approaches your paddle. Click when it's full.

| Input | Action |
|---|---|
| Left-click | Parry |
| `Space` or `Enter` | Parry (alt) |

Perfect parries (within the innermost timing zone) give extra ball speed and a white screen flash. Clicking outside the window locks you out for a fraction of a second.

---

## Gamemodes

### Classic
Standard vertical pong. First to 11 wins. Ball speeds up on every hit. AI difficulty is scalable from EASY to INSANE.

### Chaos
Everything from Classic, plus:

**Player abilities** — four on cooldowns, shown as pills at the bottom of the screen. Each pill has a cooldown bar. Grayed out while charging, bright when ready.

**AI abilities** — fire automatically on the AI's turn:
- **Duplicate Ball** — clones the ball at a random angle. Clones collide with each other and swap velocities.
- **Duplicate Paddle** — spawns a second AI paddle. If the two overlap, they push apart.
- **Throw Player** — teleports your paddle to mid-screen with a random vertical offset.

All AI abilities have their own cooldowns so they don't spam.

### Crap
No paddle movement. A ball bounces left and right on a fixed horizontal axis. You and the AI take turns parrying.

- **Parry window** — 140 px from your paddle
- **Perfect parry zone** — 60 px from the sweet spot
- **Telegraph ring** — fills as the ball approaches; click when it's full
- **Whiff lockout** — 0.22 s of dead input after a mistimed click

Failure to parry = point for the other side.

---

## Menu

Three cyclable settings before you start:

| Row | Options |
|---|---|
| **Gamemode** | Classic / Chaos / Crap |
| **AI Skill** | Easy / Normal / Hard / Insane |
| **Ball Speed** | Slow / Normal / Fast |

AI Skill changes reaction time, aim accuracy, movement speed, and (in Crap) parry accuracy. Ball Speed changes base speed, max speed, and how aggressively the ball accelerates on each hit.

Controls panel updates per gamemode.

---

## Project Structure

```
DeskPong/
├── DeskPong.py      # The entire game. Single file.
├── logo.svg         # Vector logo
├── make_icon.py     # Generates logo.ico from scratch (Pillow, no Cairo)
├── logo.ico         # Multi-size icon for PyInstaller
├── CHANGELOG.md     # Version history
└── README.md
```

Everything runs from `DeskPong.py`. No imports from local modules.

---

## Building from source

### Standalone executable (single file)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name DeskPong --noconfirm --noupx --icon logo.ico DeskPong.py
```

Output: `dist/DeskPong.exe` (~45 MB). No Python required on the target machine.

### Folder build (recommended)

```bash
pyinstaller --onedir --windowed --name DeskPong --noconfirm --icon logo.ico DeskPong.py
```

Output: `dist/DeskPong/` folder. Zip and distribute. Starts faster than onefile, and antivirus software is less likely to flag it.

If either build fails at runtime with a Qt plugin error, add `--collect-all PyQt6` and rebuild.

### Regenerating the icon

```bash
pip install pillow
python make_icon.py
```

Writes `logo.ico` and a `logo.png` preview.

---

## Configuration

All tunables live at the top of `DeskPong.py`:

```python
# Difficulty table
DIFFICULTIES = [
    ("EASY",   dict(ai_speed=0.50, ai_err0=0.180, ...)),
    ("NORMAL", dict(ai_speed=0.70, ai_err0=0.110, ...)),
    ("HARD",   dict(ai_speed=0.90, ai_err0=0.055, ...)),
    ("INSANE", dict(ai_speed=1.20, ai_err0=0.015, ...)),
]

# Ball speed table
BALL_SPEEDS = [
    ("SLOW",   dict(base=0.090, mx=0.240, speedup=1.015)),
    ("NORMAL", dict(base=0.120, mx=0.330, speedup=1.022)),
    ("FAST",   dict(base=0.160, mx=0.440, speedup=1.028)),
]

# Physical constants
PADDLE_H_FRAC   = 0.155    # paddle height as fraction of screen height
BALL_R_FRAC     = 0.0085   # ball radius as fraction of screen height
PLAYER_ACCEL    = 5800.0   # pixels per second squared
WIN_SCORE       = 11       # first to this many points wins
```

Change any of these and the game adapts. Everything is expressed as a fraction of screen dimensions so it scales correctly on any monitor size.

---

## How it works

**Window:** `Qt.WindowType.Window` + `FramelessWindowHint` + `WindowStaysOnTopHint` + `WA_TranslucentBackground`. Sized to the primary screen's geometry on launch. No title bar, no borders, no taskbar entry.

**Rendering:** everything is drawn with `QPainter` per frame. The menu background, center line, and score digits are rendered once into `QPixmap` caches and blitted, so per-frame drawing is minimal.

**Physics:** fixed 120 Hz substeps with an accumulator. The game loop measures real elapsed time and runs as many fixed-dt steps as fit within a max budget, so ball motion is frame-rate independent.

**Paddle drawing:** the player paddle is white with a black inner rim; the AI paddle is black with a white outer rim. The inversion means both read clearly on light or dark wallpapers — neither is a hollow outline that disappears.

**Ball:** white disc with a black halo and an inner shadow crescent drawn with `QPainterPath.subtracted()` to give the flat circle a sense of depth.

**Audio:** all sounds are synthesized at startup into WAV data written to a temporary directory, then played via `QSoundEffect`. The directory is deleted on quit. If Qt Multimedia is unavailable, the game runs silently and every `SFX.play()` becomes a no-op.

**Quit:** `os._exit(0)`. Bypasses Qt's event loop, tray icon keep-alive, and deferred cleanup. The process is terminated by the OS in a single syscall.

---

## Known issues

- **SmartScreen warning on first launch of the packaged build.** Windows flags unsigned executables. Click "More info → Run anyway." Only affects the PyInstaller build; running from source is unaffected.
- **Qt FFmpeg banner on first launch.** Harmless informational message from Qt Multimedia. Cannot be suppressed without patching Qt's logging rules.
- **AI prediction staleness in Chaos.** When the player uses Recall or Invert on an incoming ball, the AI's trajectory prediction briefly assumes the old direction until the next natural direction flip.

---

## Credits

Inspired by the original Pong (Atari, 1972) and every vertical-pong clone since. Built from scratch in PyQt6 with no game engine, no sprite assets, and no third-party game libraries.
```
