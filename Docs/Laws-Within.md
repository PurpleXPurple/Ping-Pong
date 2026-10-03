# Laws Within

**The internal constitution of Desk Pong.**

Every non-trivial decision in this project has an underlying rule it's trying to satisfy. Most of those rules are implicit — buried in the code, reflected in the palette, enforced by the way the game quits. This document makes them explicit.

Read this if you want to understand *why* the game is the way it is, or if you're about to modify it and want to know what you're not allowed to break.

These are laws, not preferences. Each one exists because violating it broke something real.

---

## Overview

Desk Pong is not a collection of features. It's a set of constraints that produced a specific feel. Change the constraints and you change the game. Some of those changes are fine. Others break the identity.

The laws fall into four categories:

1. **Screen laws** — the game does not own the screen
2. **Presence laws** — the game does not demand attention
3. **Engineering laws** — the code obeys specific structural rules
4. **Development laws** — how the project is allowed to grow

Read them in that order. Each category builds on the previous one.

---

## Part I — Laws of the screen

### Law 1 — The screen belongs to the user

The game is a guest. The desktop is not a canvas for the game to fill. It's a workspace that the game happens to occupy.

**Consequences:**

- The overlay must be transparent. Not "translucent." Transparent.
- Whatever is behind the game stays visible — wallpaper, icons, open windows.
- The game does not paint a background, a border, or a shadow that reads as "belonging to the game."
- The game does not appear in the taskbar.

**Violations:** any change that adds a background color, a window frame, or a taskbar entry.

**Why:** A full-screen opaque game is a game. A transparent overlay is a thing that happens to be on your desktop. Those are different genres. The moment the game takes the screen, it stops being a desktop toy.

### Law 2 — Every element must be legible on any wallpaper

The game has no idea what's behind it. Could be a black background. Could be a white document. Could be a photo of a cat. The game must be visible in all three cases.

**Consequences:**

- No element may rely on a solid fill for contrast.
- Every shape must have a stroke, a halo, or an inverted fill that guarantees visibility.
- The player paddle is white with a black rim. The AI paddle is black with a white rim. This is intentional.
- Paddles are never hollow outlines. Hollow outlines disappear on backgrounds that match the stroke color.

**Violations:** single-color elements without contrast. Hollow shapes. Thin strokes under 2 pixels.

**Why:** The original AI paddle was a hollow white outline. It disappeared on white wallpapers. The user lost points against an invisible opponent. That's not a bug — that's a design failure.

### Law 3 — The game does not steal focus

The window may be on top. It may be visible. It may even capture keyboard input when the user clicks on it. But it does not pull focus away from other applications on a timer.

**Consequences:**

- No auto-focus loop.
- Focus is grabbed on `showEvent` and on user interaction only.
- If the user clicks another window, the game respects that and lets it happen.
- Escape and F still work when the game has focus. If it doesn't have focus, the tray icon is the fallback.

**Violations:** any timer that calls `activateWindow`, `raise_`, or `setForegroundWindow` on a schedule.

**Why:** The first version grabbed focus every second. This made the game unplayable as an ambient overlay because the user couldn't use their computer. That's not ambient. That's hostile.

---

## Part II — Laws of presence

### Law 4 — The game never demands attention

Desk Pong does not notify. It does not flash. It does not play a sound to indicate "you should look at me." It waits.

**Consequences:**

- No notifications.
- No autoplay audio on launch.
- No flashing taskbar icon.
- Sounds play only in response to events the player is already watching for.
- A point scored plays a sound. A ball bouncing plays a sound. Neither plays unless the game is actively being played.

**Violations:** any sound effect triggered by an event the player didn't cause. Any visual that flashes without a preceding input.

**Why:** An ambient desktop toy loses its purpose the moment it becomes a thing you have to *manage*. The user should be able to ignore Desk Pong entirely and have it never intrude.

### Law 5 — Quit is a promise, not a request

When the user says quit, the process ends. Not "the window closes." Not "the event loop exits." The process.

**Consequences:**

- `os._exit(0)` is the only valid quit path.
- Cleanup happens before the exit, not after.
- No `QApplication.quit()` — that's a polite request to an event loop that may not be listening.
- No `sys.exit()` — that raises an exception that can be caught.

**Violations:** any quit that routes through Qt's normal teardown.

**Why:** The original quit called `QApplication.quit()` and stopped the timers. The result was a frozen window and a process that stayed alive indefinitely. The user reported it as "the game just paused." That's worse than a crash, because the user can't tell it's broken.

### Law 6 — Audio is generated, never shipped

No `.wav`, `.mp3`, `.ogg`, or `.flac` files appear in the repository. Every sound is synthesized at startup from a list of tones.

**Consequences:**

- The `SOUNDS` dictionary in `DeskPong.py` is the entire audio asset library.
- The `_synth_wav` function converts tone specs into PCM samples.
- Temp files are created in the OS temp directory and deleted on quit.
- If Qt Multimedia is unavailable, the game runs silently with no functional loss.

**Violations:** any audio file added to the repo. Any dependency on a codec library. Any runtime download of audio.

**Why:** Shipping audio files means dealing with licensing, deployment (PyInstaller `--add-data`), file size, and cross-platform audio format quirks. Synthesizing means dealing with none of it. The savings aren't in file size — they're in operational complexity.

### Law 7 — The game never cheats

The AI opponent is beatable at every difficulty level. It has real weaknesses. It does not read the ball's future position with perfect accuracy. It does not teleport. It does not have abilities the player cannot see.

**Consequences:**

- The AI's prediction goes through the same physics simulation as the player's perception of the ball.
- Every AI ability has a cooldown and a visible signal.
- Every difficulty level has a nonzero aim error.
- Reaction delays are real, not cosmetic.
- The INSANE difficulty is genuinely hard, but a skilled human can still beat it.

**Violations:** hidden AI advantages. Invisible ability fires. Cooldowns that don't apply. Reaction times below human perception thresholds.

**Why:** A game that cheats isn't a game. It's a slot machine. The point of pong is that both sides play by the same rules, and the better player wins.

---

## Part III — Laws of engineering

### Law 8 — The game is one file

`DeskPong.py` contains the entire game. No imports from local modules. No package structure.

**Consequences:**

- All state lives in one widget class.
- All config lives at the top of the file.
- All helpers, entities, and rendering code is in the same file.
- Distribution is "send one file."

**Violations:** splitting into modules. Adding a `utils.py`, `config.py`, or `render.py`.

**Why:** This is a single-file game. Splitting it would add import friction, distribution friction, and mental friction for no gain. If the file reaches 5000 lines, this law should be revisited. At 1300, it stands.

### Law 9 — Nothing is cached that doesn't need to be

Static content is cached as `QPixmap`. Dynamic content is drawn every frame. The line between them is drawn by "does this change between frames?"

**Consequences:**

- Menu background — cached (changes only on resize or mode change).
- Center line — cached (never changes except on resize).
- Score digits — cached per value (changes only when a point is scored).
- Paddles, balls, trails — drawn fresh (change every frame).

**Violations:** caching something that changes frequently (wastes memory, adds invalidation bugs). Redrawing something static every frame (wastes CPU).

**Why:** The original version redrew the entire menu — panel, title, subtitle, hairlines, controls — every frame. That's wasteful and, on slow machines, visible. Caching the static parts dropped per-frame paint cost from ~40 operations to ~3.

### Law 10 — Every state change is explicit

When the game changes scene, the change goes through `_set_scene`. When the game resets state, the reset is in `_begin_game`. When the cache is invalidated, it's called out.

**Consequences:**

- No implicit state transitions.
- No "the scene changed because a variable flipped."
- Reset blocks are visible and complete.

**Violations:** mutating `self._scene` directly. Resetting fields inline instead of in `_begin_game`. Letting cache go stale silently.

**Why:** Silent state changes are how bugs hide. Making them explicit means you can read the code and know exactly when the game is in each mode.

### Law 11 — Failures are documented, not hidden

Every failure is written down. In the changelog, in the collaboration file, in this document.

**Consequences:**

- The `Deep-Audit.md` file lists 34 issues, including critical ones.
- The `collaboration.md` file lists every mistake the AI made.
- The `CHANGELOG.md` file is honest about the initial version's flaws.
- No "this is fine" coverups.

**Violations:** hiding bugs. Retconning history. Claiming a feature works when it doesn't. Marking an issue as "won't fix" without a reason.

**Why:** Any future contributor deserves to know what's wrong. Silent bugs become permanent bugs. Documented bugs become fixed bugs.

### Law 12 — No dependency without justification

The project has exactly one external runtime dependency: PyQt6. Everything else is standard library.

**Consequences:**

- Adding a dependency requires a written justification.
- CairoSVG was tried and rejected (native dependency). Pillow was adopted because it has wheels.
- PyInstaller is a build-time dependency, not a runtime one.
- NumPy, requests, asyncio, etc. are absent and should stay absent unless they solve a real problem.

**Violations:** pulling in a library "just in case." Using a heavyweight solution for a lightweight problem. Adding a dependency without documenting why.

**Why:** Every dependency is a future breakage. Every library will eventually pin a version that doesn't install on some Python. Every native extension is a wheel that might not exist for ARM64. The only way to be bulletproof is to have as few as possible.

---

## Part IV — Laws of development

### Law 13 — The user's words are the spec

When the user says "make it black and white," that's the spec. When they say "actually kill the game and stop everything," that's a requirement, not a suggestion.

**Consequences:**

- Design decisions are made by the user, not the AI.
- The AI proposes. The user approves or rejects.
- When the AI's idea conflicts with the user's request, the user wins.
- When the user is vague, the AI asks. When the user is specific, the AI executes.

**Violations:** adding features the user didn't ask for. Changing the design because the AI thought it looked better. Ignoring a specific request in favor of a "better" alternative.

**Why:** The user is the one playing the game. The AI is a tool. The tool does not get to redesign the product.

### Law 14 — Every rewrite is a gift, not a habit

The project has been rewritten from scratch approximately five times. Every rewrite was justified by a fundamental change in the requirements.

**Consequences:**

- Rewrites happen when the architecture is wrong.
- Rewrites happen when the requirements change fundamentally (3D → 2D).
- Rewrites happen when the current code is beyond repair.
- Rewrites do NOT happen because the AI prefers a different style.

**Violations:** rewriting to "clean up" without a functional reason. Rewriting because the AI had a new idea. Rewriting because the first version was "not elegant enough."

**Why:** Every rewrite throws away tested code. It's a big investment. It should be reserved for problems that actually need it.

### Law 15 — Documentation ships with the code

Every release includes a README, a CHANGELOG, and (if the release is significant) a GUIDE. The docs are part of the artifact.

**Consequences:**

- The README explains the project to a new user.
- The CHANGELOG explains what changed and why.
- The GUIDE explains how to modify the code.
- The COLLABORATION file credits every contributor.
- The DEEP-AUDIT file records every known issue.

**Violations:** shipping code without docs. Writing docs "later." Treating documentation as secondary.

**Why:** Code without documentation is a private artifact. Code with documentation is a public one. Desk Pong is meant to be usable by anyone who finds it, not just the person who wrote it.

### Law 16 — Every idea gets a chance

The AI is allowed to propose anything. Weird physics. New gamemodes. Experimental rendering. Nothing is off the table during design.

**Consequences:**

- The `Brainstorm` phase is unconstrained.
- The `Build` phase is highly constrained.
- Ideas that fail get documented.
- Ideas that succeed get shipped.

**Violations:** dismissing an idea without trying it. Silencing a proposal because it "sounds weird."

**Why:** The three gamemodes in Desk Pong exist because the user asked for something strange and the AI took it seriously. "Chaos mode" and "Crap mode" would not exist in a more conservative design process. The weirdness is the point.

---

## Part V — Laws that emerged from failure

Some laws exist because violating them broke something specific. Those are the ones worth writing down twice.

### Law 17 — Never fight the OS with ctypes

When Qt offers native support for a problem, use Qt. When it doesn't, reconsider the problem. Do not reach for `ctypes` unless every alternative has been exhausted.

**Where this came from:** the Windows keyboard hook. 80 lines of ctypes that solved a problem that didn't exist once the window was configured correctly. It crashed on 64-bit Windows for a week. It was deleted in a single commit. Nothing of value was lost.

### Law 18 — Native dependencies are a trap

If a Python library wraps a native DLL, assume the DLL won't be there on the target machine. Prefer pure-Python alternatives. When none exist, wrap the native call in a try/except and degrade gracefully.

**Where this came from:** CairoSVG. It works on Linux. It works on macOS. On Windows it fails unless the user manually installs Cairo. The fix was to stop using CairoSVG and use Pillow, which ships wheels.

### Law 19 — The process dies when you say so

Quit is not a suggestion. It's not a request to an event loop. It's a syscall that ends the process. If cleanup needs to happen, it happens first. Then `os._exit(0)`.

**Where this came from:** the tray icon keeping the Qt event loop alive after `QApplication.quit()` was called. The user saw a frozen window and a process they couldn't kill without Task Manager.

### Law 20 — Focus is not yours to take

A window gets focus when the user gives it focus. Not on a timer. Not on an interval. Not "just to make sure it stays responsive." The user decides where their keyboard input goes.

**Where this came from:** the 1 Hz focus grab timer that made the game unusable as a background overlay. Removed. Not replaced.

---

## Part VI — Laws that should not be broken

If you fork this project and change something, these are the changes that break the identity. Everything else is fair game.

| Do not change | Why |
|---|---|
| Transparency | It stops being a desktop toy and becomes a windowed game. |
| Solid paddles with contrast rims | The hollow-outline version was invisible on white wallpapers. |
| `os._exit(0)` for quit | Anything else can hang the process on Windows. |
| Synthesized audio | Ship a WAV and the project stops being zero-asset. |
| Single-file distribution | Splitting the module adds friction for no gain. |
| Monochrome palette | Color was tried. The user rejected it. |
| No network access | The moment the game phones home, it stops being ambient. |

If you change one of these, do it deliberately, document why, and update this file. Don't drift.

---

## Part VII — Laws that are open for debate

Not every law is settled. These are the ones the project has taken a stance on but could reasonably revisit.

- **Single file vs. multiple files.** Currently one file. If the file hits 3000+ lines, the answer might change.
- **`os._exit` vs. graceful shutdown.** The game exits hard. It doesn't save state because there's no state to save. If the game ever adds persistence, this law needs review.
- **Monochrome palette.** The user chose this. Some might prefer a color scheme. The current answer is: no.
- **No installer.** The game is a single `.exe`. An installer would add a shortcut, an uninstaller, an icon in the Start menu. Not currently needed.
- **No volume control.** Sound is at 0.85. A volume slider would be nice. Not currently a priority.

Add to this list if you find a law that should be reconsidered. Don't unilaterally change the law — propose the change and let the project decide.

---

## Connections

- [[README]] — user-facing overview
- [[CHANGELOG]] — what changed, release by release
- [[GUIDE]] — deep technical reference
- [[collaboration]] — who made what
- [[Deep-Audit]] — the 34 known issues, ranked
- [[How Desk Pong Was Made]] — the development log
- [[DeskPong.py]] — the source the laws govern

---

## Open questions

- **How many of these laws are universal to game design vs. specific to Desk Pong?** Some are clearly specific ("screen belongs to the user"). Others are general ("never fight the OS with ctypes"). A separate document could split them.
- **Should laws have version numbers?** Currently they're numbered 1–20 in the order they were discovered. A future version might renumber by category.
- **What happens when two laws conflict?** Law 4 (never demand attention) and Law 5 (quit is a promise) could theoretically conflict if the game wanted to confirm-before-quit. Currently they don't, but the conflict resolution isn't defined.
- **Are there laws missing?** Every time the project hits a new failure, a new law is likely to emerge. This document is a living thing.
- **Should the laws be enforced programmatically?** A test that verifies "no hollow outlines" or "no focus-grab timers" could be added. It's a strange idea but not impossible.

---

## A closing note

The laws in this document are not aspirational. Every one of them exists because something broke.

- The screen laws exist because the first version was a full-screen opaque game.
- The presence laws exist because the second version stole focus and refused to quit.
- The engineering laws exist because the third version was fragile in ways that weren't obvious until they broke.
- The development laws exist because the AI kept wanting to rewrite things.

This is what a "living constitution" looks like for a small project. Every law is a scar. Every scar is a story. The story is the game.

---

*Twenty laws. One file. If you break one, know why.*
