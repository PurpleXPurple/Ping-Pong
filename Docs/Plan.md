# How Desk Pong Was Made

*The plans, the iterations, the failures, and the reasoning behind every decision. A full development log.*

---

## Overview

Desk Pong is a single-file, transparent, always-on-top pong overlay for Windows. It was built in about twenty-five conversational turns across a single session. It went through roughly five complete rewrites before it worked. It has three gamemodes, four synthesised sound effects, a menu system, an animated start button, and no external assets of any kind.

This document is the story of how it got there.

It is not a tutorial. It is not a lesson. It is a log — of what was tried, what broke, what stuck, and why. It exists because the process was messy and interesting and mostly undocumented in the final source, and because somebody eventually needs to know why the paddles aren't hollow outlines anymore.

---

## The cast

Four parties, honestly named:

- **PurpleXPurple** — the human. Had the idea, made every design decision, played every build, reported every bug.
- **Nexus Prime** — the AI system prompt. A document defining how the AI should think and respond. Shaped tone, structure, discipline.
- **DeepSeek** — the language model. Generated every line of code, documentation, and this file.
- **The open source stack** — Python, Qt 6, PyQt6, PyInstaller, Pillow. The actual machinery.

None of them alone could have made this. See [[collaboration]] for the full credits.

---

## Part I — The original plan

### The idea

Desk Pong started as a request for a 3D pong game. Two files: `Ping.py` and `Pong.py`, plus a `Builds.py` for scene construction and a `Structures.py` for math. The plan was:

- PyQt6 for the window
- PyOpenGL for rendering
- A 3D arena with a camera, lighting, and depth
- Physics in 3D

This plan was wrong from the first paragraph, but it took several turns to find out.

### Why it was wrong

Three reasons, none of which were visible at the start:

1. **The user didn't have OpenGL.** Assumed, not verified. The first question a developer should ask — "what's installed?" — was skipped.
2. **The 3D framing was overkill.** Pong is a 2D game. Adding a third dimension adds a camera, a projection, depth sorting, and lighting, for zero gameplay benefit.
3. **PyQt6 + PyOpenGL is a fragile stack.** Version mismatches, plugin loading order, context creation failures — the kind of thing that eats hours of debugging for no reward.

The original code was written anyway. It was clean, well-structured, and completely unusable on the target machine.

### The response

> *"i don't have opengl, bro"*
> *"wtf"*

Correct response. The AI scrapped the OpenGL plan and pivoted to a software renderer — projecting triangles by hand and drawing them with `QPainter`.

That plan was also wrong, but less wrong.

---

## Part II — The software renderer era

### The approach

Instead of GPU rendering, the plan was:

- Store geometry as lists of vertices, triangles, and per-triangle colors
- Project every vertex to screen space using a `QMatrix4x4` view-projection matrix (still pure Python)
- Backface-cull triangles whose normals face away from the camera
- Shade each triangle with flat Lambert lighting
- Sort triangles by depth, then draw them with `QPainter` in painter's-algorithm order

This was written, and it worked. It rendered. It was a real 3D pong game with a real camera and real shading.

### Why it still felt wrong

Two problems:

1. **It was slow.** Sorting hundreds of triangles per frame in pure Python, then issuing hundreds of `drawPolygon` calls, is not what Python is good at. On a modern machine it hit 60 fps, but with constant CPU load.
2. **The user didn't want 3D.** They wanted pong.

The second problem is the one that mattered. The 3D framing was the AI's idea, not the user's. The user had asked for "a pong game" and the AI had interpreted that as "a 3D pong game" without confirming.

### The response

> *"the whole movement is inverted, the game is really ugly, i got an idea, no graphics, just 2 paddles floating in my desktop, transparent background, and a ball that goes left and right, no 3D this timee"*

That message is where Desk Pong actually started. Everything before it was scaffolding.

---

## Part III — The first real plan

### The new spec

The user had now clarified:

- **No 3D.** 2D only.
- **Transparent background.** The wallpaper shows through.
- **Floating on the desktop.** Not a windowed app.
- **Two paddles and a ball.** Nothing else.

That's a completely different project. The old code was abandoned (not refactored — abandoned).

### The first working build

A single-file Python script. Frameless window, `WA_TranslucentBackground`, `WindowStaysOnTopHint`. Two paddles drawn as rounded rectangles. A ball drawn as a circle. Fixed 120 Hz physics. An AI that predicted the ball's trajectory through wall bounces.

It worked. It ran. It was called `DeskPong.py`.

### What was wrong with it

Everything aesthetic. And one thing functional.

The functional bug: **pressing Esc didn't quit.**

The cause: the window used `Qt.WindowType.Tool`. On Windows, Tool windows are treated as secondary — they cannot receive keyboard focus. So `activateWindow()` and `setFocus()` were being silently ignored, and every key press went to whatever else had focus (VS Code, the browser, the desktop).

The fix took four attempts to get right. See [[Part VIII — The Esc problem]] for the full story.

### What else was wrong

- The paddles were `drawRoundedRect` calls with no border, no shadow, no contrast. On a bright wallpaper, the AI paddle (a hollow white outline) disappeared entirely.
- The layout was a fixed-width band. Not the full desktop.
- There were no sounds.
- There were no scores.
- There was no menu.
- There was no gamemode selection.

The user asked for all of that in one message. The AI delivered a rewrite.

---

## Part IV — The menu era

### The first menu

Adding a menu meant adding scenes. The game now had four states:

- `menu` — the panel with options and START
- `starting` — the fade-out transition
- `playing` — a match in progress
- `won` — the win banner

Each state had its own draw path and its own input handling. This was the first place where the code started feeling like a real application instead of a demo.

### The first animated button

The START button got a pulsing border and a sweep animation — a short white line gliding along the bottom edge, fading in and out. That was the first "juice" element in the project, and it set the tone for everything that followed.

### The first difficulties

Four AI skill levels: EASY, NORMAL, HARD, INSANE. Each one varied five parameters at once:

- `ai_speed` — how fast the paddle can move
- `ai_err0` and `ai_err1` — aim error at rally start vs. rally peak
- `ai_react` — reaction delay after direction change
- `ai_dead` — dead zone where the AI stops correcting

That five-parameter approach was deliberate. Tuning one variable at a time makes difficulty feel samey. Tuning five at once makes each level *feel* different in a way the player can't quite articulate.

### The first "cleaner" rewrite

The initial menu was chunky and colorful. The user's response:

> *"fucking hell, why does it look so ugly- make it cleaner, black and white, full start animation, full better graphics, 300x better layoutt bro"*

Three specific asks:

1. **Black and white.** No more cyan, no more pink, no more yellow. Monochrome.
2. **Better layout.** Tighter, more typographic, less chunky.
3. **Full start animation.** Not just a pulse. A real animation.

The rewrite delivered all three:

- The palette collapsed to `#ffffff` with varying alpha over `#0a0a0c`
- The panel became 480×528 design units, scaled per screen
- The START button got a continuous sweep, an inversion on hover, and a press-scale

That version shipped. It looked good.

---

## Part V — The gamemode expansion

### The Chaos spec

> *"first is the superpowers, switches the game's entire mechanics upside down and just gives you the ability to just invert the ball's rotation, make it run faster than it already is, force it to go back to you and suddenly you smash it with a little animation making it go up and down as the AI completely gets stunned for 4 seconds if the ball hits it before its you again, and the AI also gets 3 abilities similar but they are, duplicate ball, duplicate paddle itself and let him cheat a bit but they have collision from each other, throw the user/player close in the middle instead whenever it wants"*

That single message contains seven mechanics:

**Player abilities:**
1. Invert — flip the ball's horizontal direction
2. Overdrive — increase ball speed
3. Recall — force the ball to head back toward the player
4. Smash — lock the ball into a wave pattern; stun the AI for 4 seconds if it lands

**AI abilities:**
5. Duplicate Ball — clone the ball with a random angle
6. Duplicate Paddle — spawn a second AI paddle
7. Throw Player — teleport the player's paddle to mid-screen

Each ability has a cooldown. Each ability has a visual signal. The balls collide with each other.

That's a complete design spec. It's tighter than most professional game design documents.

### The Crap spec

> *"second is 'Crap' it gives each paddle a sword, you both have to keep hitting the ball to parry it against each other, yeah... no movement, just clicks"*

Three rules:

1. No movement
2. Swords instead of paddles
3. Parry via timed clicks

The AI added:
- A 140px parry window
- A 60px perfect-parry zone
- A telegraph ring that fills as the ball approaches
- A whiff lockout so mistimed clicks don't chain

### The sound system

> *"also add sounds to the game, it feels boring asf"*

The AI could have shipped `.wav` files. It didn't. Instead it synthesised 14 sounds at startup:

- Each sound is a list of `(frequency, duration, waveform, volume)` tuples
- A function converts those into raw PCM samples
- The samples are wrapped in a RIFF WAVE header
- The WAV is written to a temp folder
- `QSoundEffect` plays it

Zero asset files. Zero licensing concerns. Zero deployment friction. The whole audio engine is about 80 lines.

That decision — synthesize instead of ship — is the single most elegant engineering choice in the project.

---

## Part VI — The input problems

### The F-key problem

The user reported:

> *"it still doesn't quit at all, make it use esc instead and force it to actually detect it properly"*

The AI diagnosed the problem: the window used `Qt.WindowType.Tool`. Tool windows cannot become the foreground on Windows, so no key events ever reach them.

The fix attempt: install a Windows low-level keyboard hook (`WH_KEYBOARD_LL`) via `ctypes`. A system-wide listener that catches Esc and F regardless of which window has focus.

### The hook failure

The hook crashed. Repeatedly.

```
ctypes.ArgumentError: argument 4: OverflowError: int too long to convert
```

On 64-bit Windows, `LRESULT` and `LPARAM` are 64-bit signed integers. The hook callback was declared with `ctypes.c_long`, which is 32-bit on Windows. Every time Windows passed a pointer, `ctypes` couldn't fit it and raised an exception.

But here's the subtle part: the exception was *silently ignored*. `ctypes` catches callback exceptions and passes `None` back. `None` becomes `0`. Windows interprets `0` as "the hook handled this key, don't propagate it."

So every keypress was being swallowed. Not just Esc and F. All of them. The game was unresponsive in every mode. The user only noticed it in Chaos because that's where they needed keys most.

### The ABI fix that didn't matter

The AI attempted an ABI fix: use `ctypes.c_ssize_t` instead of `c_long`, declare explicit `argtypes` on `CallNextHookEx`, add `restype` to `SetWindowsHookExW`.

That fix was correct. The hook would have stopped crashing.

But the user reported the crash persisted. They were probably running the old file. And the AI had, by then, already decided to abandon the hook entirely.

### The deletion

The final version of DeskPong has no Windows keyboard hook. The whole ctypes block was deleted.

Instead, three Qt-native paths handle Esc and F:

1. `QShortcut` with `ApplicationShortcut` context — fires whenever the app has focus
2. `app.installEventFilter(pong)` — catches keys before any widget processes them
3. `keyPressEvent` on the widget itself — third redundant path

Plus a 1 Hz focus re-grab timer that keeps the window activated if it loses focus.

And `os._exit(0)` for the quit, which bypasses Qt's event loop entirely.

The lesson: **on Windows, don't fight the OS with ctypes when Qt already has first-class support for what you need.** The hook was solving a problem that didn't exist once the window was configured correctly.

---

## Part VII — The paddle rendering saga

### V1 — Hollow outline

The AI's first paddle design for the monochrome rewrite:

- Player: solid white rounded rectangle
- AI: **hollow white outline**

The reasoning was aesthetic: make the two paddles visually distinct, not just positionally. Player = filled, AI = outlined.

### The problem

The user reported the paddles were "weird." The AI later discovered why.

A hollow white outline on a bright wallpaper is invisible. On a light-background desktop, the AI paddle disappeared entirely. The player would see the ball flying toward empty space and lose the point without understanding why.

### V2 — Inverted ink

The fix:

- Player: **solid white body + black inner rim**
- AI: **solid black body + white outer rim**
- Both have a black drop-halo behind them

The two paddles are now *positively* different, not just fill-vs-outline. The player's paddle is a white shape with a dark edge. The AI's paddle is a dark shape with a light edge.

Both read clearly on any background. Neither disappears.

### V3 — The stun state

When the AI is stunned (from a Smash hit), the paddle switches to a third visual: pulsing white outline with "!!!" marks above it. This is the one place where a hollow outline is intentional — it signals "this paddle is disabled."

The stun visual is exactly the design that failed as the default. The AI learned nothing and everything at the same time.

---

## Part VIII — The Esc problem, revisited

### The original quit

```python
def _quit(self):
    self._timer.stop()
    QApplication.quit()
```

`QApplication.quit()` is a *request* to the event loop. It tells Qt "please exit the main loop when you get a chance." That chance never came.

Two reasons:

1. The tray icon was still alive. Qt's event loop stays running as long as any Qt object is active.
2. `app.setQuitOnLastWindowClosed(False)` was set at startup, so even closing the window didn't trigger a quit.

The result: the game window would freeze (timers stopped), but the process would stay alive indefinitely. From the user's perspective, the game "paused."

> *"the game just paused, no exiting. wtf? seriously fix this. like actually kill the game and stop everything and delete it the second that esc hits"*

### The fix

```python
def _quit(self):
    if self._quitting:
        return
    self._quitting = True
    try:
        SFX.shutdown()
    except Exception:
        pass
    os._exit(0)
```

`os._exit(0)` is a raw `ExitProcess` syscall. It bypasses:

- Qt's event loop
- The tray icon's hold on the process
- `atexit` handlers
- `__del__` methods
- Thread joins
- Deferred deletes

The process is dead in one instruction. Nothing survives it.

The tradeoff: `SFX.shutdown()` has to be called *before* the exit, because the temp folder cleanup won't happen otherwise. That's why the explicit cleanup is in there.

### The deeper lesson

On Windows, "quit the application" is not a request to be sent to an event loop. It's a syscall. Treat it like one.

---

## Part IX — The icon pipeline detour

### The plan

The user wanted a `.ico` file for the PyInstaller build. The plan:

1. Write `logo.svg` — a vector version of the paddles-and-ball design
2. Convert SVG → PNG using CairoSVG
3. Convert PNG → ICO using Pillow

### The failure

CairoSVG on Windows requires native Cairo DLLs (`libcairo-2.dll`). These do not ship with `pip install cairosvg`. They're a separate system-level dependency that must be installed manually via GTK, MSYS2, or similar.

The user hit the exact error:

```
OSError: no library called "cairo-2" was found
```

### The fix

Instead of fighting CairoSVG, the AI wrote `make_icon.py` — a script that draws the same icon design directly with Pillow.

Pillow has no native dependencies beyond libpng and libjpeg, both of which ship with the wheel. The script:

1. Creates a 2048×2048 canvas (4× supersampling)
2. Draws rounded rectangles, circles, and lines
3. Downscales to 512×512 with LANCZOS
4. Regenerates at 16/24/32/48/64/128/256 sizes
5. Saves as a multi-size ICO

The result is identical to the SVG. The path is shorter. The dependencies are fewer.

**Lesson:** when a library fails due to missing native code, replace the library, don't install the native code. Native code is a deployment problem. Pure Python is not.

---

## Part X — The PyInstaller arc

### The user's question

> *"i wanna use pyinstaller to create a .exe file for the game but first i need to confirm — Will it work across every device even if it doesn't have Python in the first place? just the exe file?"*

The answer: **yes**. PyInstaller bundles the Python interpreter itself, plus every library the code imports, plus the C runtime DLLs. The `.exe` is self-contained.

Three caveats, none of which stopped the build:

1. **Not a cross-compiler.** Must be built on Windows.
2. **Windows 7 is unsupported.** Python 3.9+ and modern PyQt6 don't run on it anyway.
3. **Antivirus false positives.** Unsigned PyInstaller binaries frequently get flagged. `--onedir` and `--noupx` reduce the risk.

### The first failed command

> *"pyinstaller: error: ambiguous option: --upx=False could match --upx-exclude, --upx-dir"*

The AI had told the user to run `--upx=False`. That's not a real flag. The real flag is `--noupx`.

Three tokens of difference. A whole failed build.

**Lesson:** when giving command-line instructions, verify every flag against `--help` before sending. Especially for tools with long option names that auto-complete.

---

## Part XI — The final plan

After all the iterations, the final architecture of `DeskPong.py` is:

### Sections in order

1. **Bootstrap** — auto-install PyQt6 if missing, restart the process
2. **Imports** — nothing unusual
3. **Config tables** — `DIFFICULTIES`, `BALL_SPEEDS`, `GAMEMODES`
4. **Tunables** — physical constants and palette
5. **Sound synthesis** — the WAV generator and `SoundEngine`
6. **Helpers** — `clamp`, `lerp`, `predict_y`, `make_tray_icon`
7. **Entities** — `Ball`, `Paddle`
8. **Button** — one class, reused for the menu
9. **DeskPong widget** — everything else
10. **main()** — twenty lines

### Sections in the widget

1. `__init__` — state, buttons, timers
2. Focus handling — `showEvent`, `_grab_focus_now`, `_ensure_focus`
3. Screen fit and resize
4. Fonts and layout
5. Scene management — `_set_scene`, `_on_start`, `_begin_game`
6. Main loop — `_tick`, `_step_*`
7. Physics — `_integrate_ball`, `_bounce_walls`, `_bounce_off_paddle`
8. AI — `_step_ai_paddle`, `_ai_reaction_tick`
9. Chaos abilities — `_try_invert`, `_try_overdrive`, etc.
10. Crap parry — `_crap_player_click`, `_do_parry`
11. Input handlers
12. Painting — `paintEvent` and every `_paint_*` and `_draw_*`
13. Cached pixmap builders — `_build_center_line`, `_build_score_pixmap`

### The whole thing is about 1,300 lines

It's large for a single file, but every section is conceptually separable. If someone wanted to split it into modules, the boundaries are already drawn by the comment headers.

---

## Part XII — What actually made it work

Reading back through the whole arc, four decisions mattered more than the rest:

### 1. Abandoning the 3D framing

The user's message *"no 3D this time"* was the single most important line in the entire project. Everything before it was scaffolding. Everything after it was the actual game.

### 2. Synthesizing the sounds instead of shipping them

Zero assets. Zero deployment issues. The synthesized sound engine is smaller than a single WAV file would have been.

### 3. Killing the Windows keyboard hook

The hook was solving a problem that didn't exist once the window was configured correctly. Once the tool-window flag was removed, Qt's own key handling worked fine. The ctypes code was 80 lines of fragility that had to be deleted.

### 4. Using `os._exit(0)` for quit

`QApplication.quit()` is polite. `os._exit(0)` is not. On Windows, polite doesn't work when you have a tray icon and a disabled last-window-closes policy. Raw syscalls do.

---

## Part XIII — Timeline

```
Turn 1     Original 3D plan proposed. PyQt6 + PyOpenGL. Four files.
Turn 2     Full 3D code written. Multi-file architecture.
Turn 3     User: "i don't have opengl, bro"
Turn 4     Software renderer built. Painter's algorithm. 3D still.
Turn 5     User: "the whole movement is inverted, the game is really ugly"
Turn 6     User: "no 3D this timee"
Turn 7     First 2D transparent overlay. Single file. Works, but basic.
Turn 8     User: fullscreen, F-quit, scores, better AI
Turn 9     Menu added. Difficulty levels. Ball speeds.
Turn 10    User: "why does it look so ugly"
Turn 11    Monochrome rewrite. Animated START. Keycap badges.
Turn 12    Chaos mode + Crap mode + sound synthesized.
Turn 13    User: "the game just paused, no exiting"
Turn 14    Windows keyboard hook attempted. Crashed immediately.
Turn 15    ABI fix attempted. User reports crash persists.
Turn 16    Hook deleted. Qt-native shortcuts installed. os._exit(0).
Turn 17    Paddle rendering bug fixed (hollow → inverted ink).
Turn 18    PyInstaller question answered.
Turn 19    First successful .exe build.
Turn 20    Icon pipeline (CairoSVG → Pillow).
Turn 21    README, CHANGELOG, GUIDE written.
Turn 22    collaboration.md written.
Turn 23    GitHub release prepared.
Turn 24    This document.
```

Five complete rewrites. Two attempted fixes that had to be abandoned. One OS-level abstraction that had to be torn out. One Python library (CairoSVG) that had to be replaced with a hand-rolled solution (Pillow).

That's the actual cost of shipping a small game.

---

## Part XIV — What was never done

For completeness, the things that were discussed but not built:

- **Pause menu.** Discussed. Not implemented. Pressing Esc quits entirely, which is different.
- **Volume control.** Sound is fixed at 0.85. No slider.
- **Rebindable controls.** The key map is hardcoded.
- **Score persistence.** Every match starts at 0–0.
- **Multi-monitor support.** Only the primary screen is used.
- **Online multiplayer.** Never discussed in detail.
- **Replay recording.** Never discussed.
- **macOS or Linux support.** The window flags and focus behavior are Windows-specific.

Any of these could be added. The architecture supports them. They were left out because the user didn't ask, and adding unrequested features to a working build is how projects die.

---

## Connections

- [[README]] — the user-facing overview
- [[CHANGELOG]] — the version history
- [[GUIDE]] — the deep technical reference
- [[collaboration]] — the credits
- [[DeskPong.py]] — the actual source
- [[make_icon.py]] — the icon generator
- [[PyInstaller]] — the packaging tool
- [[Qt Window Flags]] — why `Tool` broke keyboard focus
- [[os._exit vs sys.exit]] — why the process has to die by syscall
- [[CairoSVG on Windows]] — the native dependency trap

---

## Open questions

- Was the 3D framing ever the right call? It might have worked if OpenGL had been installed. But the user would have gotten a 3D pong game instead of the transparent overlay they wanted. So probably not.
- Should the Windows keyboard hook have been attempted at all? The problem it solved (Esc when window isn't focused) is real. But the solution was worse than the problem. Maybe a simpler approach existed.
- Would splitting `DeskPong.py` into multiple files have helped? Probably not for this project. But at 1,300 lines it's approaching the point where single-file becomes a liability.
- Is the synthesized audio system worth keeping if someone wants to add a music track? WAVs are fine for short effects. Music tracks would need a different approach.
- If Desk Pong 2 were made from scratch today, what would change? Probably: `--onedir` from the start, no ctypes anywhere, maybe a small `config.py` for user-tunable values.

---

*End of document.*

*Every failure is documented. Every fix is documented. Every decision has a reason. This is what the source code doesn't tell you.*
