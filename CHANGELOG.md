# Changelog

All notable changes to DeskPong are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Score persistence between sessions
- Sound volume control in the menu
- Rebindable controls
- Multi-monitor support (choose target screen)
- Reduced executable size (drop unused Qt modules)

---

## [0.1.0] — 2026-10-03

First working release. Full-screen transparent pong overlay for Windows with three gamemodes, menu, and synthesized sound.

### Added

#### Core
- Full-screen transparent overlay that draws only the paddles, ball, center line, and score digits — the desktop behind stays visible
- Always-on-top window with hidden taskbar entry so it floats above other applications
- Auto-fit to the primary screen's geometry on launch
- Auto-installer: if PyQt6 is missing, the script installs it via `pip` and restarts itself. Runs end-to-end on a machine with Python but no PyQt6.
- Hard quit via `os._exit(0)` — the process dies immediately, no lingering timers, tray icons, or deferred event-loop work

#### Gamemodes
- **CLASSIC** — vertical pong against an AI opponent, first to 11 wins
- **CHAOS** — four player abilities (Invert, Overdrive, Recall, Smash) with individual cooldowns displayed as bottom-screen pills; three AI abilities that auto-fire (Duplicate Ball, Duplicate Paddle, Throw Player)
- **CRAP** — no movement; sword-based parry duel with a 140px timing window, 60px perfect-parry zone, and an animated telegraph ring that fills as the ball approaches

#### Controls
- `↑` / `↓` and `W` / `S` for paddle movement (both bindings live simultaneously)
- `Esc` and `F` quit from any scene, via three redundant paths: `QShortcut` with `ApplicationShortcut` context, an application-wide `eventFilter`, and widget-level `keyPressEvent`
- `Backspace` returns to the menu from any match
- Numpad `1`–`4` or `Z` / `X` / `C` / `V` trigger Chaos abilities; the ability bar itself is also clickable
- Left-click or `Space` triggers the parry in Crap mode
- Auto-focus re-grab every second and on every mouse press, so key input keeps working even after clicking another window

#### Menu
- Animated START button with a continuous white sweep along the bottom edge and a pulsing border
- Three cyclable settings rows: Gamemode, AI Skill (EASY / NORMAL / HARD / INSANE), Ball Speed (SLOW / NORMAL / FAST)
- Dynamic controls panel that changes per gamemode
- Entrance animation (14px slide + fade) over 0.36 s
- All buttons have hover, press, and click-flash states

#### AI
- Predictive ball tracking with `predict_y` — folds ball trajectory through top/bottom walls to compute the correct intercept y
- Reaction delay per difficulty (0.28 s EASY → 0.03 s INSANE)
- Aim error per rally: shrinks as the rally lengthens, higher on easier difficulties
- Per-difficulty dead zone so the AI doesn't jitter on tiny corrections
- Speed ramp per difficulty

#### Physics
- Fixed 120 Hz substep with accumulator loop, capped at 6 substeps per frame
- Ball speedup on every paddle hit, capped at a per-mode maximum
- Angle deflection based on hit offset from paddle center
- Paddle velocity transfer on hit (10% contribution)
- Ball spin via `QQuaternion` (rotation is real, not faked)

#### Chaos-specific mechanics
- Smash: locks the ball into a sine-wave vertical wobble at 1.55× horizontal speed; if it lands on an AI paddle, that paddle is stunned for 4 seconds
- Duplicate balls collide with each other and swap velocities
- Duplicate AI paddles physically separate if they overlap
- Throw Player: teleports the player paddle to mid-screen with a random ±0.22 screen-height offset

#### Crap-specific mechanics
- Perfect parry (within 60 px of the sweet spot) gives 1.18× speedup and a white screen flash
- Normal parry gives 1.06× speedup
- Whiff lockout: clicking outside the parry window blocks further clicks for 0.22 s

#### Graphics
- Monochrome palette — black, white, and alpha only
- Player paddle: solid white body with a black inner rim
- AI paddle: solid black body with a 2 px white outer rim
- Stunned AI paddle: pulsing white outline with "!!!" marks above
- Ball: black halo, white core, inner shadow crescent on the upper-left for depth
- Trail: 24-sample deque rendered with quadratic alpha falloff
- Center line: white dashes at 26 alpha, drawn once into a cached `QPixmap`
- Score digits rendered as cached pixmaps per value, blitted every frame

#### Sound
- 14 sounds synthesized at startup into temporary WAV files, played via `QSoundEffect`
- No audio files ship with the project; the temp directory is deleted on quit
- Graceful fallback: if Qt Multimedia isn't installed, `HAS_SOUND` becomes `False` and every `SFX.play()` is a no-op

#### Performance
- Cached pixmaps for the menu background, center line, and score digits
- Rebuild only on resize, gamemode change, or score change
- `devicePixelRatioF` respected on all pixmaps for HiDPI displays
- Smooth pixmap transform enabled for scaled blits

#### Packaging
- `logo.svg` — vector logo for the project
- `make_icon.py` — Pillow-based ICO generator (no Cairo dependency)
- `logo.ico` — multi-size icon (16 through 256) usable by PyInstaller's `--icon` flag

### Changed

- Initial window flags use `Qt.WindowType.Window` instead of `Tool`. `Tool` windows cannot receive keyboard focus on Windows, which prevented Esc/F from quitting the game.
- The Windows low-level keyboard hook (`WH_KEYBOARD_LL`) was removed. It caused an ABI mismatch on 64-bit Python (`LRESULT`/`LPARAM` are 64-bit, but the callback was declared with 32-bit `c_long`), which caused `ctypes` to raise `OverflowError` on every keypress and silently return 0 from the callback, swallowing all input. Replaced with Qt-native shortcuts.
- `_quit()` no longer calls `QApplication.quit()`. That path was swallowed by the tray icon plus `setQuitOnLastWindowClosed(False)`, leaving the process alive but frozen. `os._exit(0)` is a raw `ExitProcess` syscall and bypasses everything.

### Fixed

- `F` key no longer fails to quit when the window loses focus to another application
- Esc now quits from every scene, including mid-match, without requiring a second press
- Chaos gamemode no longer crashes the input handler on every keypress
- AI paddle no longer disappears on bright wallpapers (was drawn as a hollow white outline; now solid black with white rim)
- Ball no longer renders as a flat white disc without depth (inner shadow crescent added)
- Sword graphics in Crap mode now read clearly on light wallpapers (black outline stroke added behind the white blade)
- Score digits no longer cause a visible flicker on point scoring (pixmap cache invalidated and rebuilt before the next paint)

### Known Issues

- On some Windows 11 configurations, the first launch of the packaged `.exe` triggers a SmartScreen warning ("Windows protected your PC"). Clicking "More info → Run anyway" proceeds normally. Only affects the PyInstaller build, not the raw `.py`.
- Sound initialization prints a Qt FFmpeg informational banner on first launch (`qt.multimedia.ffmpeg: Using Qt multimedia with FFmpeg version 7.1.5`). Harmless.
- The `predict_y` AI assumes no mid-flight velocity change from external sources. In Chaos mode, when the player uses Recall or Invert on an incoming ball, the AI's prediction is briefly stale until the next direction flip.

### Security

- No network access. No file system writes outside `%TEMP%\deskpong_sfx_*` (created and deleted on every run).
- No admin elevation requested. No registry writes.
- The auto-installer invokes `sys.executable -m pip install PyQt6`, which is user-scoped by default.

---

## Format Reference

Types of changes:

- **Added** — new features
- **Changed** — changes to existing behavior
- **Deprecated** — features that will be removed in upcoming versions
- **Removed** — features removed in this version
- **Fixed** — bug fixes
- **Security** — vulnerabilities, mitigations, hardening

## Version Rules

- **MAJOR** (`1.0.0`) — incompatible changes to controls, file format, or gamemode rules
- **MINOR** (`0.2.0`) — new features that don't break existing behavior
- **PATCH** (`0.1.1`) — bug fixes only, no new features

Before `1.0.0`, anything can change.

---

[Unreleased]: https://github.com/PurpleXPurple/Ping-Pong/compare/tag/Build
[0.1.0]: https://github.com/PurpleXPurple/Ping-Pong/releases/tag/Build