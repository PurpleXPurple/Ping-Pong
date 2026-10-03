# Desk Pong — The Complete Guide

**A guide for everyone who uses, plays, or builds this game.**

Version 0.1.0 · Written for Windows · Built with PyQt6

---

# Table of Contents

**PART I — MEET DESK PONG** *(everyone reads this)*
- Chapter 1: What is Desk Pong
- Chapter 2: What you need
- Chapter 3: Glossary of terms

**PART II — THE PLAYER'S GUIDE** *(for adults who just want to play)*
- Chapter 4: Installing and launching
- Chapter 5: Understanding the menu
- Chapter 6: Classic mode
- Chapter 7: Chaos mode
- Chapter 8: Crap mode
- Chapter 9: Difficulty and skill
- Chapter 10: Troubleshooting

**PART III — THE DEVELOPER'S GUIDE** *(for people modifying the code)*
- Chapter 11: Architecture at a glance
- Chapter 12: Reading the code
- Chapter 13: The game loop
- Chapter 14: Physics and collision
- Chapter 15: The AI opponent
- Chapter 16: Rendering
- Chapter 17: Audio synthesis
- Chapter 18: The menu system
- Chapter 19: Tuning the game
- Chapter 20: Extending Desk Pong
- Chapter 21: Building and shipping

**PART IV — THE KID'S COMPANION** *(for young players)*
- Chapter 22: What is Desk Pong
- Chapter 23: How to play
- Chapter 24: The three games
- Chapter 25: Tips and tricks
- Chapter 26: Being the boss of your own game

**PART V — APPENDICES**
- Appendix A: Complete key reference
- Appendix B: Frequently asked questions
- Appendix C: File reference
- Appendix D: Configuration reference
- Appendix E: Changelog summary
- Appendix F: License and credits

---

# PART I — MEET DESK PONG

## Chapter 1: What is Desk Pong

Desk Pong is a game that lives **on top of your desktop**. Not in a window. Not behind other windows. On top, permanently, floating above everything else.

When you launch it, your screen doesn't go black or fill with a game. Instead, three things appear out of nowhere:

- A **white paddle** on the left
- A **black paddle** on the right
- A **yellow-and-white ball** in the middle

The rest of your screen — your wallpaper, your icons, your open applications — stays visible behind them. The game is drawn onto a transparent layer that sits above everything.

You can play it. You can ignore it and let it run. You can quit it with a single keypress. It has no background music, no notifications, no login screen, no ads, no telemetry, and it never asks for anything from the internet.

It's a game that respects being a game.

### The very short version

- **Two paddles. One ball. Three gamemodes.**
- **Full-screen. Transparent. Always on top.**
- **Esc quits. Arrow keys move. Everything else you'll figure out.**
- **No Python needed if you use the `.exe`.**
- **Free. Open source. MIT licensed.**

---

## Chapter 2: What you need

### If you're playing the packaged build

Nothing. You need:

- A Windows computer
- Windows 8, 10, or 11
- A working keyboard
- About 50 megabytes of free disk space

That's it. No Python. No PyQt6. No runtime to install. No administrator password.

### If you're running from source

- Python 3.9 or newer installed
- Internet access on first run (for the auto-installer)
- PyQt6 — but the game installs it for you
- About 200 megabytes of free disk space

### If you're building from source

- Everything above, plus
- PyInstaller
- A Windows machine (you cannot build a Windows `.exe` from Linux or macOS)

### Hardware

Anything from the last decade. The game is a few dozen shapes drawn in 2D. It runs fine on integrated graphics, old laptops, virtual machines, and probably a smart fridge if you could install Python on it.

Minimum realistic specs: 1280×720 screen, any dual-core CPU, 2 GB RAM.

---

## Chapter 3: Glossary of terms

These words appear throughout this guide. Skim this once, and reference it as needed.

| Term | Meaning |
|---|---|
| **Paddle** | The flat rectangle you move up and down. Player's is white; AI's is black. |
| **Ball** | The circle that bounces between paddles. Yellow-and-white with a subtle shadow. |
| **Rally** | A single continuous back-and-forth exchange. Resets when someone scores. |
| **Point** | Awarded when the ball passes a paddle and exits the play area. |
| **Match** | A full game. First to 11 points wins. |
| **AI** | The computer-controlled opponent on the right side. |
| **Chaos** | A gamemode with abilities, duplications, and physics tricks. |
| **Crap** | A gamemode with no movement, only parries. |
| **Classic** | The default gamemode. Normal pong. |
| **Cooldown** | The time you must wait before using an ability again. |
| **Stun** | A state where the AI can't move. Lasts 4 seconds. |
| **Parry** | Deflecting the ball in Crap mode with a timed click. |
| **Perfect parry** | A parry that lands within the innermost timing zone. Gives bonus ball speed. |
| **Overlay** | A window that draws on top of everything else without a background. |
| **Transparent** | You can see through the parts of the game that aren't paddles or ball. |
| **Overlay window** | The window that contains the game. |
| **HUD** | Heads-Up Display. The on-screen score and ability pills. |
| **Hitbox** | The invisible shape that determines whether a collision counts. |
| **Physics tick** | A single step of the simulation. Happens 120 times per second. |
| **Frame** | One complete redraw of the screen. Happens about 60 times per second. |
| **Skill level** | A preset that changes how good the AI is. |
| **Ball speed setting** | A preset that changes how fast the ball moves. |
| **Pill** | The rectangular buttons at the bottom of the screen in Chaos mode. |
| **Trail** | The fading line of dots behind the ball. |
| **Center line** | The dashed vertical line down the middle of the screen. |
| **Source code** | The text file that tells the computer how to run the game. |
| **Executable** | The `.exe` file that runs the game. |
| **PyInstaller** | The tool that turns Python source code into a `.exe`. |
| **PyQt6** | The library that lets Python draw windows, handle input, and play sound. |

---

# PART II — THE PLAYER'S GUIDE

## Chapter 4: Installing and launching

### If you downloaded the `.exe`

1. Find `DeskPong.exe` wherever you saved it — likely your Downloads folder.
2. Double-click it.
3. If Windows shows a blue box that says **"Windows protected your PC"**, click **More info**, then **Run anyway**.
4. The game starts immediately.

That blue box appears because the game isn't digitally signed by a paid certificate authority. Windows is being cautious. You're not in any danger.

**Where to save it:** anywhere you can remember. A folder on your desktop, a games folder, a USB stick — the game has no installer and no dependencies on the folder it lives in.

**Where it stores data:** nowhere important. The only file the game creates is a temporary audio folder inside `%TEMP%`, and it deletes that folder when you quit.

### If you're running the Python source

1. Open a terminal (PowerShell or Command Prompt).
2. Navigate to the folder with `DeskPong.py`.
3. Type `python DeskPong.py` and press Enter.
4. The first run prints `[DeskPong] PyQt6 not found. Installing...` and disappears for about 30 seconds while it installs a library.
5. It restarts itself automatically.
6. The game appears.

**Subsequent launches:** same command, but no wait. The library is already installed.

**To stop it before quitting the game:** press `Esc`. This kills the process instantly. If the game somehow ignores Esc, right-click the tray icon and choose **Quit**.

---

## Chapter 5: Understanding the menu

When the game launches, you see a black panel in the middle of your screen. This is the menu.

```
                DESK PONG
             A MINIMAL PONG

        ┌─────────────────────┐
        │        START        │  ← pulsing white sweep along the bottom
        └─────────────────────┘
─────────────────────────────────
      GAMEMODE          CLASSIC  ›
─────────────────────────────────
      AI SKILL           EASY    ›
─────────────────────────────────
      BALL SPEED        NORMAL   ›
─────────────────────────────────
      CONTROLS
      [↑][↓]  Move your paddle
      [W][S]  Move (alt)
      [ESC]   Quit
      [BKSP]  Back to menu
```

### The START button

This is the big one. Click it and the game begins. It has a continuous animation along its bottom edge — a white line sweeps left to right, fades, and repeats. When you hover over it, the whole button inverts to white with black text.

### The three option rows

Click anywhere on a row to cycle it to the next value.

- **GAMEMODE** — Classic, Chaos, or Crap
- **AI SKILL** — Easy, Normal, Hard, or Insane
- **BALL SPEED** — Slow, Normal, or Fast

The value displayed on the right (`CLASSIC`, `EASY`, `NORMAL` in the example) is the current setting.

### The controls panel

Below the options, a list of keys you can press. **This list changes depending on the gamemode you picked.** In Classic mode, you see paddle movement controls. In Chaos mode, you see ability keys. In Crap mode, you see parry controls.

### What happens when you click START

- The menu fades out over about half a second.
- The menu's panel slides upward slightly as it disappears.
- The ball appears in the middle of the screen.
- It launches toward one of the paddles at a random angle.
- The game is live.

---

## Chapter 6: Classic mode

Classic mode is the purest form of the game. Two paddles, one ball, nothing else.

### How a rally works

The ball starts in the middle. It travels toward one side at a shallow angle. Whichever paddle it's heading toward tries to intercept it. If the paddle succeeds, the ball bounces back toward the other side, speeding up slightly. This continues until someone misses.

### How to move your paddle

Press `↑` to move up. Press `↓` to move down. Your paddle accelerates when you hold a key and slows down when you release it. This feels natural — the paddle has momentum, it doesn't stop instantly.

If you prefer, `W` and `S` do the exact same thing. Both sets of keys are always active.

### How points are scored

If the ball goes past **your** paddle (off the left edge of the screen), the AI gets a point.
If the ball goes past the **AI's** paddle (off the right edge), you get a point.

The score appears in the top-left (yours) and top-right (theirs) as white digits outlined in black.

### How the ball speeds up

Every time the ball hits a paddle, it gets faster. There's a cap on how fast it can go, but by the time a rally reaches 10 hits it's noticeably fast.

### How the AI plays

The AI paddle doesn't just follow the ball. It looks ahead — it calculates where the ball will be by the time it reaches the AI's side, factoring in any wall bounces. This is called **trajectory prediction**.

But the AI isn't perfect. It has three built-in flaws:

1. **It reacts slowly.** For a fraction of a second after the ball changes direction, the AI doesn't know what to do. This is the "reaction time."
2. **It aims slightly wrong.** It adds a small error to its target position. The error shrinks the longer the rally goes.
3. **It moves at a limited speed.** It can't teleport. If the ball is far away, the AI might not get there in time.

### How to win

First to 11 points. That's the whole rule.

Then a banner appears: `YOU WIN` or `AI WINS`. It stays for about two and a half seconds, then the game returns to the menu automatically.

### Beginner strategy

- **Stay near the center.** Don't overcommit to the top or bottom.
- **Watch the ball, not your paddle.** Your paddle follows your eyes.
- **Don't move after the ball passes you.** It's not going to come back.
- **Use the ball's angle.** If it's coming in at a steep angle, you'll need to move more than you think.
- **The AI has a weakness: it can't handle sharp angles.** If you can angle your paddle to hit the ball with a strong vertical trajectory, the AI struggles.

---

## Chapter 7: Chaos mode

Chaos mode is what happens when you take Classic and inject it with steroids. It adds **abilities** — special moves with cooldowns that change how the game plays.

### The ability system

At the bottom of the screen, four pills appear:

```
   ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
   │1 INVERT│  │2 BOOST│  │3 PULL │  │4 SMASH│
   └───────┘  └───────┘  └───────┘  └───────┘
```

Each pill shows:
- The **number key** that triggers it (`1` through `4`)
- The **ability name**
- A **cooldown bar** at the bottom that fills up as the ability recharges

When the ability is **ready**, the pill looks bright. When it's on **cooldown**, the pill is dim and the bar shows how much longer you have to wait.

### Your four abilities

**1 — Invert**
Flips every active ball's horizontal direction. Balls that were heading toward the AI now head toward you, and vice versa.

- **Cooldown:** 1.8 seconds
- **Use when:** You want to trick the AI. It's committed to moving one way, and suddenly the ball is coming back.

**2 — Overdrive**
Multiplies every active ball's speed by 1.55× on both axes.

- **Cooldown:** 4.5 seconds
- **Use when:** The AI is barely keeping up. Boost the ball to make it miss.
- **Warning:** This also boosts balls heading toward you. Use with care.

**3 — Recall**
Forces every active ball to head back toward you, regardless of where it was going.

- **Cooldown:** 3.5 seconds
- **Use when:** You need a moment to reposition, or you want to bait the AI into committing to a side.

**4 — Smash**
Only works when a ball is heading toward the AI. Locks the ball into a wavy pattern at 1.55× horizontal speed. If it lands on an AI paddle, that paddle is stunned for 4 seconds.

- **Cooldown:** 7 seconds
- **Use when:** You want to disable the AI entirely for a while.
- **Note:** If the ball is heading toward you, this ability does nothing.

### How to trigger abilities

Three ways, all equivalent:

1. **Numpad 1–4** — press the number on the right-hand number pad
2. **Z X C V** — bottom row of the left side of the keyboard (for laptops without numpads)
3. **Mouse click** — click the pill itself

### The AI's abilities

The AI is not idle during all this. It has its own three abilities, which fire automatically when the ball starts heading toward it:

**Duplicate Ball**
Clones the ball with a random angle. Now there are two balls in play. They collide with each other — when two balls hit, they swap velocities.

- **AI cooldown:** 10 seconds
- **Visual signal:** the flash text `AI: DUPLICATE BALL` appears at the bottom of the screen

**Duplicate Paddle**
Spawns a second AI paddle at a random offset from the first. Both track the ball. If they overlap, they push each other apart.

- **AI cooldown:** 15 seconds
- **Visual signal:** `AI: DUPLICATE PADDLE`

**Throw Player**
Teleports your paddle to roughly the middle of the screen with a random vertical offset. Also plays a "whoosh" sound.

- **AI cooldown:** 14 seconds
- **Visual signal:** `AI: THREW YOU`

### How the balls interact

When two or more balls are in play, they're not ghosts. If two balls collide, they **swap velocities**. This is real billiard-ball physics — the two moving objects exchange their motion vectors.

This means a slow ball hitting a fast ball will suddenly become fast, and vice versa.

### Strategy for Chaos

- **Chain abilities.** Invert, then Overdrive, then Smash. Every ability used in sequence hits harder than one used alone.
- **Watch the cooldowns.** The pills tell you when you're ready. Use an ability the moment its cooldown bar hits the top.
- **Smash stuns.** A stunned AI paddle is a free point. Time it for a rally where the AI is playing well.
- **Don't panic when balls duplicate.** Both balls have to be dealt with, but they're not coordinated. Focus on the one that's going to hit you first.
- **The AI's abilities have visual signals.** Watch the flash text at the bottom of the screen to know what it's doing.

---

## Chapter 8: Crap mode

Crap mode is the strangest of the three. It has **no paddle movement**. You don't press arrow keys. Your paddle stays put. So does the AI's.

Instead, a sword is planted in each paddle. A ball bounces back and forth horizontally. When it reaches your sword, you have to click at exactly the right moment to **parry** it back.

### The physics of Crap

The ball travels straight left or right. No vertical motion. No gravity. No angle.

It enters your parry zone. When it gets close to your sword, a dashed line appears showing the exact position of your parry window.

### The parry window

The window is 140 pixels wide. Inside that, there's a smaller 60-pixel "perfect parry" sweet spot.

```
       Your paddle          Parry window
           │                     │
           │  ┌───────────────┐  │
           ▼  │               │  ▼
        ╔════╗                 ╔════╗
        ║    ║    ·  ·  ·  ·   ║    ║
        ║    ║                 ║    ║
        ╚════╝                 ╚════╝
                ▲
                Sweet spot
```

### The telegraph ring

The most important visual in Crap mode: a **white ring** around your paddle that shrinks as the ball approaches.

- **When the ball is far away**, the ring is large and faint.
- **When the ball is close**, the ring shrinks and gets brighter.
- **When the ring is tight and bright**, that's your cue to click.

### Perfect vs. normal parry

- **Normal parry** — click anywhere inside the window. Ball bounces back at 1.06× speed.
- **Perfect parry** — click within the innermost 60-pixel zone. Ball bounces back at 1.18× speed, and a white flash covers the screen.
- **Whiff** — click outside the window. Nothing happens. You're locked out of clicking for 0.22 seconds.

### The AI's parry

The AI has a `parry_acc` value (parry accuracy) that's set by the AI Skill level. On Easy, it's 40%. On Insane, it's 95%. When it's the AI's turn, it rolls for a chance to parry and, if successful, picks a random moment inside the window to fire.

### How to play well

- **Watch the ring, not the ball.** The ball's position is less useful than the ring's size.
- **Click when the ring is tight, not when the ball is close.** By the time the ball is at your paddle, it's too late.
- **Perfect parries are worth chasing.** They're 18% faster and they feel great.
- **If you whiff, don't click again for a beat.** You're locked out and a second click is wasted.

### Controls

| Input | Action |
|---|---|
| Left-click anywhere | Parry |
| `Space` | Parry (alt) |
| `Enter` | Parry (alt) |

That's it. There is no movement. There are no abilities. There's only timing.

---

## Chapter 9: Difficulty and skill

The AI SKILL setting changes five things at once. This is intentional — tuning one thing would be confusing. Instead, Easy is genuinely easy and Insane is genuinely hard, across every dimension.

### The four levels

| Level | Reaction | Aim error | Speed | Parry accuracy |
|---|---|---|---|---|
| **EASY** | 0.28 s | ±18% | Slow | 40% |
| **NORMAL** | 0.18 s | ±11% | Medium | 60% |
| **HARD** | 0.10 s | ±5.5% | Fast | 80% |
| **INSANE** | 0.03 s | ±1.5% | Very fast | 95% |

### What each number means

**Reaction time** — After the ball changes direction, how long the AI takes before it starts moving toward the new position. On Easy, it's nearly a third of a second. On Insane, it's 30 milliseconds — faster than a human eye blink.

**Aim error** — The AI predicts where the ball will be, then adds a random error to that prediction. On Easy, the error is huge. On Insane, it's tiny. The error also shrinks as the rally grows longer, so long rallies are harder for the AI on Easy but barely change the AI on Insane.

**Speed** — How fast the AI paddle can move. On Easy, it's 50% of screen height per second. On Insane, 120%.

**Parry accuracy** — Only matters in Crap mode. How often the AI successfully parries on its turn.

### Ball Speed

Separate from AI Skill, this changes the ball's base speed, its maximum speed, and how aggressively it accelerates.

| Speed | Base | Max | Speedup per hit |
|---|---|---|---|
| **SLOW** | 9% of width/s | 24% | 1.5% |
| **NORMAL** | 12% | 33% | 2.2% |
| **FAST** | 16% | 44% | 2.8% |

### Recommended combinations

- **First time playing:** EASY + SLOW
- **Enjoying yourself:** NORMAL + NORMAL
- **Looking for a challenge:** HARD + NORMAL
- **Punishing yourself:** INSANE + FAST

---

## Chapter 10: Troubleshooting

### The game won't start

**Symptom:** Double-click the `.exe`, nothing happens.
**Fix:** Right-click the `.exe`, choose **Run as administrator** once. If it works, the issue is a permissions quirk on your machine.

**Symptom:** Windows shows "This app can't run on your PC."
**Cause:** You're on a 32-bit Windows install and the game was built for 64-bit, or vice versa.
**Fix:** Rebuild from source on a matching machine, or grab the correct architecture from the releases page.

### The game starts but I can't see it

**Symptom:** The tray icon appears but no game panel.
**Fix:** Move your mouse to the middle of the screen. The game panel might be hidden behind a full-screen window. Press `Alt+Tab` and pick Desk Pong.

**Symptom:** The game is invisible but keys still respond.
**Cause:** A compositor issue (rare). If you're on Windows with "Transparency effects" turned off, the game may render as fully opaque black.
**Fix:** Settings → Personalization → Colors → turn on Transparency effects.

### I can't quit

**Symptom:** `Esc` does nothing.
**Fix:** Click on the game window first (anywhere on the panel or in the game area), then press `Esc`. If it still doesn't quit, use the tray icon.

**Symptom:** Nothing works and the process is stuck.
**Fix:** Open Task Manager (`Ctrl+Shift+Esc`), find `DeskPong.exe` or `python.exe`, right-click, End Task.

### Sound doesn't work

**Symptom:** Visuals play but no sound.
**Cause:** Qt Multimedia isn't installed, or your audio device is having issues.
**Fix:** The game is designed to run silently if audio fails. There's no fix needed — the game plays identically without sound. If you specifically want sound, reinstall PyQt6 from source: `pip install --force-reinstall PyQt6`.

### Sound is too loud or too quiet

There is no volume control in-game. Use the Windows volume mixer:

1. Right-click the speaker icon in your system tray.
2. Choose **Open Volume Mixer**.
3. Find Desk Pong in the list.
4. Adjust its slider.

### The AI is too easy or too hard

Use the menu's **AI SKILL** setting. There are four levels, and INSANE + FAST is genuinely difficult.

If INSANE feels too easy, you're not alone. The AI is designed to be beatable at every level — it's a game, not an IQ test. But if you want a real challenge, try playing with SLOW ball speed and INSANE skill. The AI will rarely miss, and the rallies will be long.

### The game crashed

**Symptom:** Window disappears.
**Fix:** Relaunch. The game has no state to lose — every match starts fresh.

If crashes are frequent, check your PyQt6 version:

```bash
pip show PyQt6
```

You need version 6.4 or newer.

---

# PART III — THE DEVELOPER'S GUIDE

## Chapter 11: Architecture at a glance

Desk Pong is a single-file Python application. There are no modules, no packages, no imports from local directories. Everything lives in `DeskPong.py`.

### The three layers

```
┌────────────────────────────────────────────────┐
│                  PRESENTATION                   │
│  paintEvent → QPainter → QPixmap caches         │
│  Cached menu background, center line, digits    │
└────────────────────────────────────────────────┘
                       ▲
                       │ reads state
                       │
┌────────────────────────────────────────────────┐
│                    GAME LOGIC                   │
│  Modes: Classic, Chaos, Crap                    │
│  Per-mode step functions, input handlers        │
└────────────────────────────────────────────────┘
                       ▲
                       │ mutates state
                       │
┌────────────────────────────────────────────────┐
│                     PHYSICS                     │
│  Integration, collision, AI prediction          │
│  Runs at fixed 120 Hz via accumulator           │
└────────────────────────────────────────────────┘
```

### Why single file

Three reasons:

1. **Distribution.** Ship one file. The user downloads `DeskPong.py` or `DeskPong.exe`. Nothing else.
2. **Editing.** All the code is in one place. Search finds everything.
3. **PyInstaller simplicity.** One entry point, no relative imports to reason about.

The tradeoff is that `DeskPong.py` is around 1300 lines. That's big for a Python file. But it's organized into clear sections with comment headers, and every section is conceptually separable if you ever want to split it.

### The top-level structure of `DeskPong.py`

```
1. Bootstrap (auto-installer)
2. Imports
3. Config tables (DIFFICULTIES, BALL_SPEEDS, GAMEMODES)
4. Tunables (PADDLE_W, BALL_R_FRAC, etc.)
5. Palette (QColor constants)
6. Sound synthesis (WAV generation + SoundEngine)
7. Helpers (clamp, lerp, predict_y, etc.)
8. Entities (Ball, Paddle)
9. Button
10. DeskPong widget (the game)
11. main()
```

If you're reading top to bottom, you'll go from "what libraries does this use" through "how does it look" to "how does it play" to "how does it start." That's the right order.

---

## Chapter 12: Reading the code

### Section 1: Bootstrap

```python
def _bootstrap():
    try:
        import PyQt6.QtWidgets  # noqa: F401
        return
    except ImportError:
        pass
    # ... install PyQt6 via pip, then os.execv to restart
```

This runs **before any PyQt6 import**. If PyQt6 is missing, it installs it and re-launches the current script with the same arguments. The `os.execv` call replaces the running process — no parent process left behind.

Why it exists: someone running from source shouldn't have to know about `pip`. The game installs its own dependencies.

### Section 2: Config tables

These are the *game design* values. They're separate from the *engineering* tunables below them because they represent choices the player makes, not physical constants.

```python
DIFFICULTIES = [
    ("EASY",   dict(ai_speed=0.50, ai_err0=0.180, ...)),
    ("NORMAL", dict(ai_speed=0.70, ai_err0=0.110, ...)),
    ("HARD",   dict(ai_speed=0.90, ai_err0=0.055, ...)),
    ("INSANE", dict(ai_speed=1.20, ai_err0=0.015, ...)),
]
```

Each entry is a tuple: `(display_name, parameter_dict)`. The menu cycles through them by index.

`ai_speed` is a fraction of screen height per second. `ai_err0` and `ai_err1` are the aim error at rally 0 and rally 8+. `ai_react` is the reaction delay in seconds. `ai_dead` is the dead zone in pixels.

### Section 3: Tunables

Physical constants:

```python
PADDLE_W         = 18           # paddle width in pixels
PADDLE_H_FRAC    = 0.155        # paddle height as fraction of screen height
BALL_R_FRAC      = 0.0085       # ball radius as fraction of screen height
PLAYER_ACCEL     = 5800.0       # player paddle acceleration, px/s²
```

The `_FRAC` suffix means "this scales with screen size." That's why the game looks correct on any monitor — nothing is hardcoded to a specific pixel size.

### Section 4: Palette

Every color is a `QColor` defined once. These get reused throughout the painting code.

```python
C_PANEL_BG   = QColor(  8,   8,  10, 238)
C_TEXT_HI    = QColor(255, 255, 255, 235)
C_HAIRLINE   = QColor(255, 255, 255,  28)
```

The fourth number is alpha (0–255). `238` is 93% opaque. `28` is 11% opaque.

### Section 5: Sound synthesis

The most interesting non-obvious part. Rather than shipping WAV files, the game generates them at startup:

```python
SOUNDS = {
    "click":    [(880, 0.035, "square", 0.18)],
    "paddle":   [(440, 0.065, "sine",   0.28)],
    ...
}
```

Each sound is a list of **tones**. Each tone is `(frequency_hz, duration_s, waveform, volume)`. Multiple tones play sequentially — a rising arpeggio for win, a descending chord for score.

`_synth_wav` converts these specs into raw PCM samples, packs them into a RIFF WAVE header, and writes them to a temp directory. `QSoundEffect` loads them from there.

The whole thing takes about 200 ms at startup and adds zero bytes to the shipped code.

### Section 6: Helpers

Small pure functions used everywhere:

- `clamp(v, lo, hi)` — cap a value into a range
- `lerp(a, b, t)` — linear interpolation
- `ease_out(t)` — cubic ease-out for animations
- `predict_y(...)` — trajectory folding (described in Chapter 15)

### Section 7: Entities

Two `__slots__` classes. `__slots__` prevents Python from allocating a `__dict__` for each instance, which makes them smaller and faster.

`Ball` has position, velocity, radius, alive flag, clone flag, smash state, and a trail deque.

`Paddle` has position, velocity, stun timer, and a flash timer.

### Section 8: Button

A small state machine. Tracks hover, press, and click-flash states as floats that decay over time. The paint code reads these floats to compute interpolated visuals.

### Section 9: The `DeskPong` widget

Everything else. This is the game. Roughly 900 lines.

### Section 10: `main()`

Twenty lines. Creates the `QApplication`, initializes sound, creates the widget, installs an event filter, shows the tray icon, runs the event loop.

---

## Chapter 13: The game loop

The game runs on a `QTimer` firing every 16 milliseconds (roughly 60 Hz). That's the **frame rate**.

But the physics doesn't run at 60 Hz. It runs at **120 Hz** — twice as often. This is intentional.

### Why decouple frame rate from physics rate

If physics ran at frame rate, then a slow frame (say a 33 ms hitch) would cause a big jump in ball position. Fast balls would tunnel through paddles. Collisions would feel wrong.

By running physics at a fixed rate independent of frame rate, motion is consistent even when frames drop.

### The accumulator pattern

```python
def _tick(self):
    now = time.perf_counter()
    dt = now - self._last_t
    self._last_t = now
    dt = clamp(dt, 0.0005, MAX_DT)  # cap at 50 ms

    self._scene_t += dt
    # ... update buttons, handle scene transitions ...

    self.accumulator += dt
    while self.accumulator >= FIXED_DT and steps < MAX_SUBSTEPS:
        self._step(FIXED_DT)
        self.accumulator -= FIXED_DT
        steps += 1
```

`FIXED_DT` is `1/120` — one physics tick.

The accumulator holds time that hasn't been "spent" on physics yet. Each frame, we add the real elapsed time to it, then drain it in fixed-size chunks.

### Frame rate independence

Result: whether your machine runs at 30 fps, 60 fps, or 144 fps, the ball moves the same distance per real-world second. The visuals just update more or less often.

### The substep cap

`MAX_SUBSTEPS = 6`. If a frame takes too long, we stop running substeps after 6 and let the accumulator grow. Next frame, we'll try again. This prevents a slow frame from causing a cascade of 100 physics steps that make the game stutter.

If the accumulator grows too big (say, the game was minimized for 10 seconds), we cap the incoming `dt` at 50 ms. The ball will "jump" but won't spiral out of control.

---

## Chapter 14: Physics and collision

### Ball integration

Every physics tick:

```python
ball.trail.appendleft((ball.x, ball.y))  # record position for trail
ball.x += ball.vx * dt
ball.y += ball.vy * dt
```

That's it. Simple Euler integration. No drag, no gravity, no restitution.

### Wall collision

```python
if ball.y - ball.r < 0.0:
    ball.y = ball.r
    ball.vy = abs(ball.vy)
elif ball.y + ball.r > self._h:
    ball.y = self._h - ball.r
    ball.vy = -abs(ball.vy)
```

Two important things:

1. **Position clamping.** After the bounce, the ball is forced out of the wall. Without this, a fast ball can get stuck bouncing inside the wall.
2. **Using `abs()` instead of negation.** `ball.vy = abs(ball.vy)` guarantees the ball is now heading downward (positive y). `ball.vy = -ball.vy` would only work if the ball was heading upward to begin with.

### Paddle collision

```python
def _overlaps(self, ball, pad):
    return (ball.x + ball.r >= pad.x
            and ball.x - ball.r <= pad.x + pad.w
            and ball.y + ball.r >= pad.y
            and ball.y - ball.r <= pad.y + pad.h)
```

Standard AABB overlap. Treats the ball as a square for collision purposes. The visual is a circle, but the hitbox is a square. That's a common simplification — nobody notices at these speeds.

### The bounce

```python
def _bounce_off_paddle(self, ball, pad, dir_x, paddle_vy):
    # 1. Push ball out of paddle along X
    if dir_x > 0:
        ball.x = pad.x + pad.w + ball.r + 0.5
    else:
        ball.x = pad.x - ball.r - 0.5

    # 2. Increase speed
    self._rally += 1
    base = max(math.hypot(ball.vx, ball.vy), self._w * self._cfg["base"])
    self._speed = min(base * self._cfg["speedup"], self._w * self._cfg["mx"])

    # 3. Compute new angle from hit offset
    center = pad.y + pad.h * 0.5
    offset = clamp((ball.y - center) / (pad.h * 0.5), -1.0, 1.0)
    angle = offset * BALL_MAX_ANGLE

    # 4. Set velocity
    ball.vx = math.cos(angle) * self._speed * dir_x
    ball.vy = math.sin(angle) * self._speed + paddle_vy * 0.10

    # 5. Renormalize to preserve total speed
    sp = math.hypot(ball.vx, ball.vy)
    if sp > 1e-4:
        k = self._speed / sp
        ball.vx *= k
        ball.vy *= k
```

Let's break that down.

**Step 1** — the ball is moved out of the paddle. If we don't do this, next tick the ball is still overlapping and we bounce again, trapping the ball inside.

**Step 2** — the ball speeds up. There's a floor (don't go slower than base) and a ceiling (don't exceed `mx`). The `speedup` multiplier is per-hit.

**Step 3** — how far from center was the hit? `offset` is normalized to -1.0 (top edge) through +1.0 (bottom edge). Multiply by `BALL_MAX_ANGLE` (1 radian = 57°) to get the deflection angle.

**Step 4** — velocity is the angle decomposed into x and y components. The paddle's own vertical velocity is added at 10% weight, so hitting the ball with a moving paddle imparts some of that motion.

**Step 5** — renormalization. Because we added `paddle_vy * 0.10` in step 4, the total speed might exceed the intended `self._speed`. This scales both components down proportionally to hit the target speed exactly.

### Ball-ball collision (Chaos only)

```python
if dx * dx + dy * dy <= rr * rr:
    a.vx, b.vx = b.vx, a.vx
    a.vy, b.vy = b.vy, a.vy
    # then push both apart to avoid sticking
```

Elastic collision between equal-mass circles. The velocity swap is the correct answer for two identical masses hitting head-on. For glancing hits, the geometry is more complex, but for a game this is close enough.

---

## Chapter 15: The AI opponent

The AI has three responsibilities:

1. **Predict where the ball will be** when it reaches the AI's x-coordinate
2. **Move toward that position** at a limited speed
3. **Add error** to feel human

### The prediction function

```python
def predict_y(x0, y0, vx, vy, target_x, top, bottom):
    if abs(vx) < 1e-6:
        return y0
    t = (target_x - x0) / vx
    if t < 0.0:
        return y0
    y = y0 + vy * t
    span = bottom - top
    period = 2.0 * span
    y = (y - top) % period
    if y < 0.0:
        y += period
    if y > span:
        y = period - y
    return top + y
```

This is the trickiest math in the codebase. It computes where the ball crosses `target_x`, folding off the top and bottom walls.

**Step by step:**

1. If the ball isn't moving horizontally, return its current y (edge case).
2. Compute time to reach `target_x`. If negative, ball is moving away.
3. Extrapolate the ball's y at that time.
4. Fold the result through [top, bottom] using modular arithmetic, which simulates repeated bounces.

The "fold" is a standard technique: reduce `y` into a periodic domain, then mirror if it's beyond the midpoint.

This is exact. The AI computes the true intercept point of a bouncing ball. That's why even EASY AI intercepts correctly — the error is added afterward, not from bad prediction.

### The reaction delay

```python
if ball.vx > 0.0:
    self._ai_react_t += dt
if ball.vx <= 0.0 or self._ai_react_t < self._cfg["ai_react"]:
    target = self._h * 0.5  # go to center
else:
    target = predict_y(...)  # chase the ball
```

The AI only starts reacting after a `ai_react` second delay when the ball changes direction. Before that, it moves toward the center of the screen.

This creates the effect of "the AI is unprepared." On Easy it's a huge delay. On Insane it's imperceptible.

### The aim error

```python
err = (self._cfg["ai_err0"]
       + (self._cfg["ai_err1"] - self._cfg["ai_err0"]) * t)
self._ai_err = random.uniform(-1.0, 1.0) * err * self._h
```

`t` is `min(rally / 8, 1.0)`. So as the rally grows, the error linearly decreases from `ai_err0` to `ai_err1`. Newly launched balls get the full error; long rallies get a tighter AI.

The error is in units of screen height fraction, converted to pixels by multiplying by `self._h`.

### Movement

```python
speed = self._h * self._cfg["ai_speed"]
center = pad.y + pad.h * 0.5
diff = target - center
if abs(diff) < self._cfg["ai_dead"]:
    return
step = clamp(diff, -speed * dt, speed * dt)
pad.y = clamp(pad.y + step, 0.0, self._h - pad.h)
```

The AI moves at a capped speed toward the target. If it's already close enough (within `ai_dead` pixels), it does nothing — this prevents jittery micro-corrections.

The final `clamp` keeps the paddle inside the screen.

---

## Chapter 16: Rendering

The game draws everything with `QPainter`. No OpenGL. No GPU shaders. Just 2D vector drawing.

### Why not OpenGL

For the number of shapes involved (10-20 per frame after caching), `QPainter` is fast enough. OpenGL would add complexity for no gain.

### The cache strategy

Three things are cached as `QPixmap`:

1. **Center line** — the dashed white line down the middle. Doesn't change between resizes.
2. **Score digits** — the numbers in the corner. Change only when a point is scored.
3. **Menu background** — the panel, title, subtitles, hairlines, controls list. Changes only when the gamemode is cycled or the window resizes.

The cache is a plain dict:

```python
self._cache = {}
```

Lookup pattern:

```python
cl = self._cache.get("center_line")
if cl is None:
    cl = self._build_center_line()
    self._cache["center_line"] = cl
```

### DPI awareness

```python
def _new_pixmap(self, w, h):
    dpr = self._dpr()  # devicePixelRatioF
    pm = QPixmap(int(w * dpr), int(h * dpr))
    pm.setDevicePixelRatio(dpr)
    pm.fill(Qt.GlobalColor.transparent)
    return pm
```

On a HiDPI display (200% scaling), `devicePixelRatioF()` returns 2.0. The pixmap is created at 2× resolution and Qt automatically downscales it during drawing, producing a crisp image.

Without this, the cached pixmaps would look blurry on 4K displays.

### The paint order

```
paintEvent:
  1. Fill background (transparent)
  2. Draw cached center line
  3. If CRAP:
       draw trails, swords, parry window, ball, perfect flash
     Else:
       draw trails, balls, paddles, chaos HUD
  4. Draw cached score digits
  5. Draw flash text if active
  6. Draw win banner if applicable
```

Z-order is draw order. Later draws appear on top.

### The paddle rendering

```python
def _draw_paddle(self, p, pad, is_player, alpha, stunned=False):
    # 1. Flash aura (expanding rings)
    # 2. Black drop shadow
    # 3. Body:
    #    - Player: white with black inner rim
    #    - AI: black with white outer rim
    #    - Stunned: pulsing hollow outline
```

The AI paddle's black-with-white-rim design is what makes it readable on any wallpaper. Originally it was drawn as a hollow white outline, which disappeared on white backgrounds.

### The ball rendering

```python
# 1. Black halo (separation from background)
# 2. Smash aura if active (concentric white rings)
# 3. White core
# 4. Inner shadow crescent (for depth)
```

The inner shadow is drawn with `QPainterPath.subtracted`:

```python
shadow = QPainterPath()
shadow.addEllipse(QPointF(x - r * 0.18, y - r * 0.18), r * 0.72, r * 0.72)
clip = QPainterPath()
clip.addEllipse(QPointF(x, y), r * 0.92, r * 0.92)
shadow = shadow.subtracted(clip)
```

This creates a crescent shape — the part of the offset circle that isn't inside the ball. Filled with semi-transparent black, it reads as a shadow on the upper-left of the ball.

---

## Chapter 17: Audio synthesis

### Why synthesize

Shipping `.wav` files would mean:

- Larger install size (a few hundred KB)
- More files to manage
- Licensing concerns if any file was sourced
- Deployment friction (PyInstaller `--add-data` flags)

Synthesizing at startup solves all four. The sound definitions take 15 lines of code and produce 14 distinct sounds.

### How it works

Each sound is a list of tones:

```python
"win": [(400, 0.090, "sine", 0.28),
        (550, 0.090, "sine", 0.28),
        (700, 0.090, "sine", 0.28),
        (900, 0.180, "sine", 0.28)],
```

Four tones, rising in pitch, played back to back. Total duration ~0.45 seconds.

The frequency is in Hz, duration in seconds, waveform in {`"sine"`, `"square"`}, volume in 0–1.

### The waveform generator

```python
def _synth_wav(tones, rate=22050):
    samples = []
    for (freq, dur, wave, vol) in tones:
        n = int(dur * rate)
        attack = max(1, int(0.004 * rate))
        release = max(1, int(min(0.06, dur * 0.5) * rate))
        for i in range(n):
            t = i / rate
            # envelope
            if i < attack:
                env = i / attack
            elif i > n - release:
                env = max(0.0, (n - i) / release)
            else:
                env = 1.0
            # waveform
            ph = 2.0 * math.pi * freq * t
            s = math.sin(ph) if wave == "sine" else (1 if math.sin(ph) >= 0 else -1)
            samples.append(int(s * env * vol * 32767.0))
    # prepend RIFF WAVE header
    ...
```

Key details:

- **Sample rate is 22050 Hz** — half of CD quality. Sounds small but perfectly adequate for short beeps.
- **Attack envelope:** 4 ms ramp from 0 to full volume. Prevents a "click" at the start.
- **Release envelope:** up to 60 ms ramp from full to 0. Prevents a "click" at the end.
- **16-bit signed samples** — standard for PCM WAV.

### Playback

```python
eff = QSoundEffect()
eff.setSource(QUrl.fromLocalFile(path))
eff.setVolume(0.85)
self._effects[name] = eff
```

`QSoundEffect` is a low-latency audio player. It's designed for short sounds triggered by UI events. Perfect for this use case.

Each sound is loaded once and reused. Calling `.play()` re-triggers from the start.

### Cleanup

```python
def shutdown(self):
    self._effects.clear()
    for f in os.listdir(self._dir):
        os.unlink(os.path.join(self._dir, f))
    os.rmdir(self._dir)
```

The temp directory is deleted on quit. `_quit()` calls this explicitly before `os._exit(0)` — because `os._exit` bypasses `atexit` handlers and doesn't run `__del__` methods.

---

## Chapter 18: The menu system

### Scene management

The game has four states:

| Scene | Meaning |
|---|---|
| `"menu"` | Menu is showing |
| `"starting"` | Player clicked START, menu is fading out |
| `"playing"` | A match is in progress |
| `"won"` | Win banner is showing, about to return to menu |

`self._scene` holds the current state. `self._scene_t` is the time since the scene was entered.

### The starting transition

```python
if sc == "starting":
    if self._scene_t >= 0.42:
        self._begin_game()
    self.update()
    return
```

The menu fades out over 0.42 seconds. During this time, the START button stays in its inverted state, and the whole menu panel fades to transparent. When the fade completes, the game begins.

### The won transition

```python
if sc == "won":
    self._banner_t -= dt
    if self._banner_t <= 0.0:
        self._banner_text = ""
        self._set_scene("menu")
        self._cache.clear()
    self.update()
    return
```

The banner displays for 2.6 seconds. Then the scene flips back to menu and the cache is cleared (because the score reset).

### The Button class

Every button has:

- `label` — text
- `rect` — position and size
- `hovered` — bool
- `pressed` — bool
- `hover_t` — float, 0 to 1, eased toward `hovered`
- `press_t` — float, 0 to 1, decays after a press
- `flash_t` — float, 0 to 1, decays after a click
- `pulse_t` — float, monotonically increasing, used for the START button's animation

The paint code reads these floats and interpolates visuals. `hover_t` drives the fill color, `press_t` drives the scale, `flash_t` drives the white flash overlay.

### The layout system

Menu layout is computed in `_compute_layout`:

```python
self._panel_w = 480.0 * s
y = 0.0
self._y_title = y + 40.0 * s;  y = self._y_title + 44.0 * s
self._y_sub = y - 4.0 * s;     y = self._y_sub + 26.0 * s
# ... etc
```

`s` is the scale factor — `screen_height / 1080`, clamped to a reasonable range. Every measurement is `base_value * s`, so the menu scales proportionally on any screen.

Anchor positions are computed relative to the top of the panel, then offset by the panel's y-position at the end.

---

## Chapter 19: Tuning the game

Everything that's adjustable is at the top of `DeskPong.py`. Change a value, save, relaunch.

### Making it easier

- **Lower AI skill:** set `DEFAULT_DIFF = 0` (EASY)
- **Bigger paddle:** increase `PADDLE_H_FRAC` from `0.155` to `0.20`
- **Bigger ball:** increase `BALL_R_FRAC` from `0.0085` to `0.012`
- **Slower ball:** set `DEFAULT_SPEED = 0` (SLOW)
- **Slower acceleration:** reduce `PLAYER_ACCEL` from `5800.0` to `4000.0`

### Making it harder

- **AI skill:** set `DEFAULT_DIFF = 3` (INSANE)
- **Smaller paddle:** reduce `PADDLE_H_FRAC` to `0.10`
- **Smaller ball:** reduce `BALL_R_FRAC` to `0.006`
- **Faster ball:** set `DEFAULT_SPEED = 2` (FAST)
- **Shorter match:** reduce `WIN_SCORE` from `11` to `5`

### Custom difficulties

```python
DIFFICULTIES = [
    ("EASY",   dict(ai_speed=0.50, ai_err0=0.180, ai_err1=0.040,
                    ai_react=0.28, ai_dead=9.0, parry_acc=0.40)),
    ("NORMAL", dict(ai_speed=0.70, ai_err0=0.110, ai_err1=0.025,
                    ai_react=0.18, ai_dead=7.0, parry_acc=0.60)),
    ("HARD",   dict(ai_speed=0.90, ai_err0=0.055, ai_err1=0.014,
                    ai_react=0.10, ai_dead=5.0, parry_acc=0.80)),
    ("INSANE", dict(ai_speed=1.20, ai_err0=0.015, ai_err1=0.003,
                    ai_react=0.03, ai_dead=3.0, parry_acc=0.95)),
]
```

Add a fifth entry, adjust values, and the menu will pick it up automatically. The menu cycles through `len(DIFFICULTIES)` entries, so this scales.

### Custom ball speeds

Same pattern:

```python
BALL_SPEEDS = [
    ("SLOW",   dict(base=0.090, mx=0.240, speedup=1.015)),
    ("NORMAL", dict(base=0.120, mx=0.330, speedup=1.022)),
    ("FAST",   dict(base=0.160, mx=0.440, speedup=1.028)),
]
```

`base` and `mx` are fractions of screen width per second. `speedup` is the multiplier applied on each paddle hit.

### Adding a new gamemode

Four steps:

1. Add the name to `GAMEMODES`:
   ```python
   GAMEMODES = ["CLASSIC", "CHAOS", "CRAP", "MY_MODE"]
   ```

2. Add a step function:
   ```python
   def _step_my_mode(self, dt):
       # your logic here
       pass
   ```

3. Add it to the mode dispatch in `_tick`:
   ```python
   if m == "CRAP":
       self._step_crap(dt)
   elif m == "CHAOS":
       self._step_chaos(dt)
   elif m == "MY_MODE":
       self._step_my_mode(dt)
   else:
       self._step_classic(dt)
   ```

4. Add controls text in `_paint_controls_static`:
   ```python
   elif m == "MY_MODE":
       rows = (...)
   ```

That's the whole extension surface. The menu, the input system, and the rendering pipeline will all pick up your new mode automatically.

---

## Chapter 20: Extending Desk Pong

Ideas, ranked by difficulty.

### Easy

**Change the colors.** Every color is defined once in the palette section. Modify `C_PANEL_BG`, `C_TEXT_HI`, etc. Save, relaunch.

**Change the sounds.** Edit the `SOUNDS` dict. Each tone is `(frequency, duration, waveform, volume)`. Add more tones for longer sounds.

**Add a new difficulty.** Add an entry to `DIFFICULTIES`. Instant new option in the menu.

**Change the win score.** `WIN_SCORE = 11`. Set to any number.

### Medium

**Add a pause feature.** Introduce a `"paused"` scene. In `_tick`, if scene is `"paused"`, skip physics. Bind `P` to toggle.

**Add a second human player.** Change AI paddle input from AI logic to keyboard input. Bind `K`/`I` or similar. Two-player local pong.

**Add score persistence.** Write the score to a JSON file in `%APPDATA%` on game end. Read it back on launch. Requires ~20 lines.

**Add a "rally counter" display.** Track the current rally length. Draw it in the corner. Makes long rallies feel satisfying.

### Hard

**Add online multiplayer.** Requires a networking layer (sockets, asyncio, or a library like `aiohttp`). Real scope.

**Add replay recording.** Record all ball positions with timestamps. Play them back as a replay after the match. Requires serialization and a playback system.

**Rebindable controls.** Read bindings from a JSON file. Replace hardcoded key checks with a lookup. Requires a settings UI.

**Multi-monitor support.** Currently uses primary screen only. Would need a menu option to select which screen.

### The one change I'd recommend

**Add a volume control.** Sound is currently fixed at 0.85. A menu slider would be nice. It's about 30 lines of code.

---

## Chapter 21: Building and shipping

### Building the executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name DeskPong --noconfirm --noupx --icon logo.ico DeskPong.py
```

Arguments explained:

- `--onefile` — single self-extracting `.exe`
- `--windowed` — no console window
- `--name DeskPong` — output is `DeskPong.exe`
- `--noconfirm` — overwrite `dist/` and `build/` without asking
- `--noupx` — skip UPX compression (avoids antivirus false positives)
- `--icon logo.ico` — use the icon from `logo.ico`

### The folder build (recommended)

```bash
pyinstaller --onedir --windowed --name DeskPong --noconfirm --icon logo.ico DeskPong.py
```

Output is `dist/DeskPong/` — an `DeskPong.exe` plus an `_internal/` folder with all the runtime DLLs. Zip the whole folder. Distribute the zip.

Advantages over onefile:
- Faster startup
- Less likely to trigger antivirus heuristics
- Easier to inspect when something goes wrong

### If PyInstaller fails

Most common error: `Could not find the Qt platform plugin "windows"`.

Fix: add `--collect-all PyQt6`:

```bash
pyinstaller --onefile --windowed --name DeskPong --noconfirm --noupx --icon logo.ico --collect-all PyQt6 DeskPong.py
```

This forces PyInstaller to include every file in the PyQt6 package, including plugins it might not have detected automatically. Build takes longer, output is bigger, but it works.

### Verifying the build

The only valid test: copy `DeskPong.exe` (or the `DeskPong/` folder) to a machine that has **never had Python installed**. Run it. If the game launches, the build is good.

For a local test, use Windows Sandbox (available on Windows 10 Pro and Windows 11 Pro). Open Sandbox, drag the folder in, run the executable.

### Signing (optional)

Unsigned executables trigger SmartScreen warnings on first launch. A code-signing certificate costs $200–400 per year from a certificate authority. For personal use or sharing with friends, it's not worth it. For wide distribution, it is.

If you decide to sign:

1. Buy an OV (Organization Validation) certificate from DigiCert, Sectigo, etc.
2. Sign with `signtool sign /f cert.pfx /p password /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 DeskPong.exe`

Signed executables start clean on any Windows machine.

### Publishing to GitHub

1. Create a git repository
2. Commit `DeskPong.py`, `README.md`, `CHANGELOG.md`, `logo.svg`, `logo.ico`, `make_icon.py`
3. Tag a release: `git tag v0.1.0`
4. Push the tag: `git push origin v0.1.0`
5. Go to the repo on GitHub, click Releases → Draft a new release
6. Attach `DeskPong.exe` in the drop zone
7. Write release notes (see the CHANGELOG)
8. Publish

The download URL is `https://github.com/<user>/<repo>/releases/latest/download/DeskPong.exe` — share it anywhere.

---

# PART IV — THE KID'S COMPANION

*This part is written for younger players. If you're an adult, you're welcome to read it too, but you already know most of this.*

---

## Chapter 22: What is Desk Pong

Hi! Welcome to Desk Pong.

Desk Pong is a game that floats on top of your computer screen. It looks like a real desk toy — two paddles and a ball — that you can play with right over your wallpaper. Your background stays behind it, so you can still see your dog picture or your Minecraft wallpaper while you play.

The paddles are the rectangles. The left one is white (that's you). The right one is black (that's the computer). The ball is the yellow circle in the middle.

When you play, the ball bounces back and forth. If you miss it and it goes past your white paddle, the computer gets a point. If the computer misses and the ball goes past the black paddle, you get a point.

First person to **11 points** wins!

---

## Chapter 23: How to play

### Starting the game

When the game opens, you'll see a black rectangle in the middle of your screen with the words `DESK PONG` at the top. That's called the **menu**.

There's a big blue-white button in the middle that says `START`. Click it. The menu fades away and the game begins.

### Moving your paddle

Press `↑` (up arrow) to move the white paddle up.

Press `↓` (down arrow) to move the white paddle down.

That's it! You don't need to press anything else.

If you don't have arrow keys on your keyboard, or you like different keys better, you can use `W` and `S`. `W` goes up. `S` goes down. They do the exact same thing.

### Hitting the ball

You don't press a button to hit the ball. You just move your paddle in front of it. If your paddle touches the ball, the ball bounces back automatically.

Aim the middle of your paddle at the middle of the ball. That's how you hit it straight. If you hit it with the top of your paddle, the ball goes at a weird angle. If you hit it with the bottom of your paddle, it goes the other weird way.

### Scoring

Every time you hit the ball back, you get closer to winning. Every time the computer misses, you get a point.

The score shows up in the corner. Yours is on the left. The computer's is on the right.

### Winning

When you get 11 points, a big word appears: `YOU WIN`.

When the computer gets 11 points, it says `AI WINS`.

Then the game goes back to the menu and you can play again.

### Quitting

Press `Esc` (the escape key, top-left of your keyboard). The game disappears. That's it.

### Going back to the menu

If you want to change the game or stop a match in the middle, press `Backspace` (the big key above Enter). You'll go back to the menu.

---

## Chapter 24: The three games

Desk Pong has three different games you can play. You pick which one before you start.

### Game 1: Classic

This is the normal one. Two paddles, one ball, first to 11 points.

**How to win:** Just be fast! Move your paddle where the ball is going. Don't let it get past you.

### Game 2: Chaos

This one is CRAZY. It has **superpowers**.

When you're playing Chaos, at the bottom of the screen you'll see four buttons that say `INVERT`, `BOOST`, `PULL`, and `SMASH`. Each one is a superpower!

- **INVERT** — Press `1` (or `Z`). The ball suddenly turns around! It was going away from you, now it's coming back. Sneaky!
- **BOOST** — Press `2` (or `X`). The ball goes super fast. ZOOM!
- **PULL** — Press `3` (or `C`). The ball comes back to you, no matter where it was going.
- **SMASH** — Press `4` (or `V`). The ball starts wiggling up and down and goes super fast at the computer. If it hits the computer's paddle, the computer freezes for 4 whole seconds!

Wait, 4 seconds is a long time. That's how long you can score without the computer trying to stop you!

**But watch out** — the computer has superpowers too! It might:

- Make a **second ball** appear
- Make a **second paddle** appear on its side
- **Teleport your paddle** to the middle of the screen (rude!)

You'll see a message at the bottom of the screen when the computer uses one.

Each superpower has a **cooldown** — after you use it, a little bar fills up. When the bar is full, you can use it again.

### Game 3: Crap

This one is the weirdest. **You can't move your paddle.** It stays in one spot.

Instead, there's a **sword** sticking out of your paddle. The ball bounces left and right.

When the ball comes close to you, a white ring around your paddle starts getting smaller and smaller. When the ring is really tight, **click your mouse** (or press `Space`).

If you clicked at the right time, the ball bounces back! That's called a **parry**.

If you clicked too early or too late, nothing happens and you can't click again for a tiny moment.

If you don't click at all, the ball goes past you and the computer gets a point.

**How to win:** Watch the ring! Click when it's small.

---

## Chapter 25: Tips and tricks

### Tip 1: Watch the ball, not your paddle

It sounds weird, but your eyes should be on the ball. Your hands will naturally move the paddle to the right place. If you stare at your paddle, you'll lose track of where the ball is.

### Tip 2: Don't panic

The ball is fast sometimes. That's okay! Take a breath. Move the paddle smoothly. Frantic movement makes you miss more, not less.

### Tip 3: Use the middle of the paddle

If the ball hits the middle of your paddle, it goes straight back. Easy to predict. If it hits the top or bottom, it goes at a weird angle and you might miss the next one.

### Tip 4: Change the settings

You can make the game easier! In the menu, before you click START, click on `AI SKILL` and `BALL SPEED`. Choose `EASY` and `SLOW` to start. When you get good, change them to `HARD` or `INSANE`.

### Tip 5: Try all three games

Classic is the calm one.
Chaos is the exciting one.
Crap is the tricky one.

Play all three and pick your favorite!

### Tip 6: Take breaks

The game never ends on its own. It'll keep running forever. If your eyes get tired, press `Esc` and take a break. The game will be there when you come back.

---

## Chapter 26: Being the boss of your own game

Did you know you can **change the game**?

The game is made of a special kind of file called **code**. It's a text file. Inside the file, there are numbers that control how the game works.

If you have a grown-up to help you, you can open the file and change the numbers. Here are some fun ones:

### Making the paddle bigger

Find the line that says:

```
PADDLE_H_FRAC = 0.155
```

Change `0.155` to `0.250`. Now the paddle is much bigger. It's easier to hit the ball.

### Making the ball tiny

Find the line that says:

```
BALL_R_FRAC = 0.0085
```

Change it to `0.0040`. Now the ball is tiny. It's much harder!

### Making the game shorter

Find the line that says:

```
WIN_SCORE = 11
```

Change it to `3`. Now you only have to get 3 points to win. Fast games!

### Making the game longer

Change `WIN_SCORE` to `50`. Now you have to be really really good to win!

### Making the colors different

Find lines like:

```
C_PANEL_BG = QColor(8, 8, 10, 238)
```

The three numbers in the middle (8, 8, 10) are red, green, and blue. The last number (238) is how see-through it is.

- `QColor(255, 0, 0, 255)` = bright red
- `QColor(0, 255, 0, 255)` = bright green
- `QColor(0, 0, 255, 255)` = bright blue
- `QColor(255, 255, 0, 255)` = yellow

Change the numbers. Save the file. Run the game again. See what happens!

### Asking for help

If you want to add something cool to the game — like a new superpower or a different kind of paddle — ask a grown-up or a coding-savvy friend. The game is small enough that changes are easy to make.

**Remember:** always save a copy of the original file before you change anything. That way, if something breaks, you can go back to the way it was.

---

# PART V — APPENDICES

## Appendix A: Complete key reference

### Always available

| Key | Action |
|---|---|
| `Esc` | Quit the game immediately |
| `F` | Quit (alias for Esc) |
| `Backspace` | Return to the menu (from game or win screen) |

### Classic and Chaos movement

| Key | Action |
|---|---|
| `↑` | Move paddle up |
| `↓` | Move paddle down |
| `W` | Move paddle up (alt) |
| `S` | Move paddle down (alt) |

### Chaos abilities

| Key | Ability |
|---|---|
| Numpad `1` or `Z` | Invert ball direction |
| Numpad `2` or `X` | Overdrive (ball speed × 1.55) |
| Numpad `3` or `C` | Recall (pull ball toward you) |
| Numpad `4` or `V` | Smash (stun AI on hit) |

### Crap parry

| Key | Action |
|---|---|
| Left-click | Parry |
| `Space` | Parry (alt) |
| `Enter` | Parry (alt) |

### Menu

| Input | Action |
|---|---|
| Left-click on START | Begin game |
| Left-click on any option row | Cycle setting |
| Left-click on ability pill (Chaos) | Trigger ability |

---

## Appendix B: Frequently asked questions

**Can I run this on macOS or Linux?**

Not currently. The code uses `os._exit(0)` (portable) but the window flags and focus behavior are Windows-specific. A macOS port would need different window configuration. Linux might work with minor changes but isn't tested.

**Can I run this on Windows 7?**

Probably not. Python 3.9+ and PyQt6 don't support Windows 7 anymore. Windows 8 is the practical minimum.

**Can I change the resolution of the game?**

The game automatically fits your primary screen. There's no in-game resolution setting.

**Can I move the game window?**

No. It's full-screen and always on top by design. It's an ambient desktop toy, not a windowed app.

**Can I make the game smaller or bigger on my screen?**

Not in-game. But you could modify the `_fit_to_screen` method to use a portion of the screen instead of the whole thing.

**Does the game save my high score?**

No. Every match starts at 0–0.

**Does the game use the internet?**

No. No network access whatsoever.

**Does the game collect any data?**

No. No telemetry, no analytics, no logging.

**Can I share this with my friends?**

Yes. It's MIT licensed. Do anything you want with it.

**Can I sell this?**

Yes, though the market for a transparent pong overlay is probably small.

**What if I find a bug?**

Open an issue on the GitHub repo. Include what you were doing, what you expected, and what happened.

**Will there be more gamemodes?**

Maybe. The code is designed for it. Adding a new mode is about 50 lines of code.

---

## Appendix C: File reference

| File | Purpose |
|---|---|
| `DeskPong.py` | The entire game. Source code. |
| `DeskPong.exe` | The packaged game (after building with PyInstaller). |
| `logo.svg` | Vector logo for docs and GitHub. |
| `logo.ico` | Multi-size Windows icon for the `.exe`. |
| `logo.png` | 512×512 raster preview (generated by `make_icon.py`). |
| `make_icon.py` | Regenerates `logo.ico` from scratch using Pillow. |
| `README.md` | Project overview. |
| `CHANGELOG.md` | Version history. |
| `GUIDE.md` | This file. |

---

## Appendix D: Configuration reference

All values are at the top of `DeskPong.py`.

### Difficulty table

Each entry has:

- `ai_speed` — fraction of screen height per second
- `ai_err0` — aim error at rally start (fraction of screen height)
- `ai_err1` — aim error after 8+ hits
- `ai_react` — reaction delay in seconds
- `ai_dead` — dead zone in pixels (AI ignores smaller corrections)
- `parry_acc` — accuracy in Crap mode (0 to 1)

### Ball speed table

Each entry has:

- `base` — starting speed (fraction of screen width per second)
- `mx` — maximum speed
- `speedup` — multiplier applied per paddle hit

### Physics constants

| Constant | Default | Meaning |
|---|---|---|
| `PADDLE_W` | 18 | Paddle width in pixels |
| `PADDLE_H_FRAC` | 0.155 | Paddle height / screen height |
| `PADDLE_MARGIN_X` | 46 | Pixels from screen edge to paddle |
| `PLAYER_ACCEL` | 5800 | Player paddle acceleration px/s² |
| `PLAYER_DAMP` | 11 | Player paddle damping |
| `PLAYER_MAX_FRAC` | 1.25 | Max player paddle speed / screen height / s |
| `BALL_R_FRAC` | 0.0085 | Ball radius / screen height |
| `BALL_MAX_ANGLE` | 1.00 | Max deflection off paddle (radians) |
| `TRAIL_LEN` | 24 | Number of trail samples |
| `WIN_SCORE` | 11 | First to this many points wins |
| `SERVE_DELAY_S` | 0.75 | Delay before serving after a point |
| `BANNER_S` | 2.6 | Win banner duration |
| `FPS_MS` | 16 | Target frame time in milliseconds |
| `MAX_DT` | 0.05 | Max elapsed time per frame |
| `FIXED_DT` | 1/120 | Physics step duration |
| `MAX_SUBSTEPS` | 6 | Max physics steps per frame |

### Chaos constants

| Constant | Default | Meaning |
|---|---|---|
| `CD_INVERT` | 1.8 | Invert cooldown (s) |
| `CD_OVER` | 4.5 | Overdrive cooldown |
| `CD_RECALL` | 3.5 | Recall cooldown |
| `CD_SMASH` | 7.0 | Smash cooldown |
| `SMASH_SPEED` | 1.55 | Smash horizontal speed multiplier |
| `SMASH_WOBBLE` | 620 | Smash wave amplitude (px/s) |
| `STUN_S` | 4.0 | AI stun duration |
| `MAX_BALLS` | 3 | Max simultaneous balls |
| `MAX_AI_PADDLES` | 2 | Max AI paddles |
| `AI_CD_DUPE_BALL` | 10.0 | AI duplicate ball cooldown |
| `AI_CD_DUPE_PAD` | 15.0 | AI duplicate paddle cooldown |
| `AI_CD_THROW` | 14.0 | AI throw player cooldown |

### Crap constants

| Constant | Default | Meaning |
|---|---|---|
| `CRAP_WIN_PX` | 140 | Parry window size (px) |
| `CRAP_PERFECT_PX` | 60 | Perfect parry window (px) |
| `CRAP_WHIFF_LOCK` | 0.22 | Click lockout after whiff (s) |

---

## Appendix E: Changelog summary

See `CHANGELOG.md` for the full history. Short version:

- **0.1.0** — Initial release. Three gamemodes, animated menu, synthesized sound, single-file executable.

---

## Appendix F: License and credits

### License

MIT. See the LICENSE file in the repository or the license header in `DeskPong.py`.

You are free to use, modify, distribute, sublicense, and sell this software. The only requirement is that the copyright notice and license text are preserved.

### Credits

- **Original Pong** — Atari, 1972. Designed by Allan Alcorn.
- **PyQt6** — Riverbank Computing. The GUI library that makes this possible.
- **Qt6** — The Qt Company. The C++ framework underneath PyQt6.
- **Python** — Guido van Rossum and the Python Software Foundation.
- **You** — for playing, for reading this guide, for caring about a pong game enough to read 4000 lines about it.

---

**End of guide.**

*If this document helped, star the repo. If it didn't, open an issue. Either way, keep playing.*
