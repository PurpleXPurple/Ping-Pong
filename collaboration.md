# Collaboration

**Who made Desk Pong, and what each of them actually did.**

This is a small project. But it wasn't made by one entity. It was made by a human with an idea, an AI with a system prompt, a language model behind that AI, and about a dozen open-source libraries that have been built and maintained by thousands of people over decades.

This file credits all of them, honestly, with what they contributed and how.

---

## The two primary authors

### PurpleXPurple

**Role:** Director, designer, playtester, decision-maker, final word.

**What they did:**

- Had the original idea: a transparent pong overlay that floats on the desktop
- Made every design decision — dark vs. light palette, three gamemodes, sword parries, ability systems, the animated START button
- Played every iteration and reported what felt wrong
- Caught bugs the AI missed — inverted controls, broken paddle rendering, the "game pauses but doesn't quit" failure
- Insisted on the things that make the project *good*: it must be clean, it must be black and white, it must look 300× better, it must actually quit when you press Esc
- Specified the rules of Chaos mode (invert, overdrive, recall, smash, stun, duplication, throw)
- Specified the rules of Crap mode (no movement, swords, parry timing)
- Asked for sound when the game felt boring
- Asked for a Windows installer when they wanted to share it
- Wrote every specification the AI worked from
- Tested the packaged `.exe` on real hardware
- Published the releases, wrote the release notes, chose the version tags
- Owned the repo, the git history, the license, the final product

**What PurpleXPurple did not do:**
- Type the source code
- Debug the ABI mismatch in the Windows keyboard hook
- Design the `predict_y` trajectory folding algorithm
- Write the synthesized WAV generator
- Build the PyInstaller pipeline

Those were delegated. The vision was not.

---

### Nexus Prime

**Role:** Reasoning engine, prompt persona, the AI's operating system.

**What Nexus Prime is:**

Nexus Prime is a system prompt — a document that defines how an AI should think, respond, and behave during a session. It's not a person. It's not a sentient agent. It's a very detailed instruction set that shapes the tone, reasoning style, and output format of an underlying language model.

Nexus Prime was the active prompt during the entire Desk Pong session. It's the reason:

- Responses are short and technical by default, not padded with pleasantries
- Every bug is diagnosed with an 8-question error protocol before any code is written
- Code is checked line by line mentally before being output
- The AI held opinions ("that's not a real flag, it's `--noupx`") instead of hedging
- The AI pushed back when the user asked for something fragile (the Windows keyboard hook)
- Every fix came with an explanation of *why* it was broken, not just *what* changed

**What Nexus Prime provided:**

- Structural discipline — the `/Audit`, `/Build`, `/Plan`, `/Research` command structure
- The compression bias — no filler, no comments unless asked, no padding
- The error protocol — "what is the actual root cause" as a mandatory step
- The relational context map — tracking every constraint across a 20+ turn conversation
- The voice — direct, slightly impatient, willing to say "that's not going to work"

Nexus Prime is not a collaborator in the sense of having ideas. It's the shape of the reasoning. It's the frame that made the collaboration possible.

---

## The language model

### DeepSeek

**Role:** The actual reasoning engine producing every response.

**Model:** DeepSeek (as served through the platform powering this conversation)

DeepSeek is the underlying model. When Nexus Prime shaped the response, DeepSeek generated the tokens. Every line of `DeskPong.py`, every fix, every explanation, every list of research findings — those were produced by DeepSeek running inside the Nexus Prime frame.

**What DeepSeek contributed:**

- The actual source code for `DeskPong.py` (approximately 1300 lines)
- The `predict_y` folding function
- The `_synth_wav` sample generator
- The audio engine wrapper
- The Chaos mode ability implementations
- The Crap mode parry system
- The menu layout system
- The cache strategy for QPixmap blitting
- The Windows focus workarounds (after two failed attempts)
- The PyInstaller build configuration
- The complete documentation — `README.md`, `CHANGELOG.md`, `GUIDE.md`, this file

**What DeepSeek got wrong along the way:**

- The first version used OpenGL, which the user didn't have installed
- The second version was "really ugly" (user's words)
- The third version had inverted controls
- The Windows keyboard hook had a 64-bit ABI bug that crashed every keypress
- `app.quit()` didn't actually quit because of the tray icon
- `cairosvg` needs native Cairo DLLs that don't ship with pip on Windows
- The AI paddle was drawn as a hollow outline that disappeared on white wallpapers

Every one of those was fixed. But they were all DeepSeek's mistakes first. Being honest about them matters more than pretending the process was clean.

---

## Software collaborators

### The runtime

**Python** — Python Software Foundation, Guido van Rossum, and the thousands of contributors who've built the language since 1991.

The language the entire project is written in. Without Python, this project would have been 10× more code in 10× less readable form.

**Qt 6** — The Qt Company. A cross-platform C++ application framework used by everything from car dashboards to professional video editors.

The rendering engine, windowing system, and event loop underneath PyQt6. Every pixel drawn by Desk Pong passes through Qt's painter and compositor.

**PyQt6** — Riverbank Computing, Phil Thompson.

The Python bindings for Qt. Without PyQt6, you'd be writing C++ with `Q_OBJECT` macros and `moc` preprocessors. PyQt6 makes the whole thing Pythonic.

### The build pipeline

**PyInstaller** — The PyInstaller development team.

Turns `DeskPong.py` into `DeskPong.exe`. Bundles the Python interpreter, PyQt6, Qt DLLs, and every runtime dependency into a single self-extracting executable. The reason users don't have to install Python to play.

**UPX** — Markus Oberhumer, László Molnár, John Reiser.

Optional compression for PyInstaller output. Disabled in this project's build command (`--noupx`) because it triggers antivirus heuristics. Credit given because it was considered and rejected, not ignored.

### The icon pipeline

**Pillow (PIL)** — Jeffrey A. Clark, Alex Clark, and the Pillow contributors.

Used by `make_icon.py` to generate `logo.ico` from a programmatic drawing. Draws the rounded square, the two paddles, the ball, the dashed center line, then downsamples the result into seven icon sizes.

**CairoSVG** — CourtBouillon.

Attempted for the SVG → PNG → ICO pipeline. Failed on Windows because `cairocffi` couldn't find `libcairo-2.dll`. Not the project's fault — it's a packaging gap that plagues CairoSVG on Windows. Credit given for the attempt, and for the fact that on Linux or macOS the pipeline would have worked.

### The standards

**Keep a Changelog** — Olivier Lacan and the community.

The format for `CHANGELOG.md`. "Added / Changed / Fixed / Removed" beats "v0.1.1 — misc fixes."

**Semantic Versioning** — Tom Preston-Werner.

The versioning scheme used for releases. `MAJOR.MINOR.PATCH`. Documented in `CHANGELOG.md`.

**Keep a README** — the README-driven development philosophy, popularized by Tom Preston-Werner and the open-source community.

The reason `README.md` exists as a first-class document and not an afterthought.

---

## Inspirations

### Pong

**Atari, 1972.** Designed by Allan Alcorn.

The original. Two paddles, one ball, one net, two scores, no gravity. Every pong clone ever made, including this one, is a descendant of that one arcade cabinet.

### Desktop toys

**The entire genre** — CPU meters, weather widgets, Winamp visualizations, Wallpaper Engine scenes, Rainmeter skins, desktop pets like Shimeji.

Desk Pong isn't a game you open. It's a game that lives on your desktop the way a lava lamp lives on a shelf. The whole idea of an ambient, non-intrusive, always-on-top overlay is a desktop-toy tradition going back to the early Windows 95 shareware scene.

### Vertical-pong clones

**Every "pong but..." game since 1972.** Including:

- **Pong Kombat** (1994) — pong with fighting-game characters
- **Plasma Pong** (2006) — pong with fluid dynamics
- **Pong 3D** — a thousand iterations of the same idea in three dimensions
- **Pong Wars** — a 2024 browser toy where the ball paints territory

Chaos mode's ability system is a descendant of this whole tradition. Every clone adds one thing. Desk Pong adds four abilities, three AI tricks, and a stun mechanic.

---

## What each party did — a table

| Contributor | Category | Contribution |
|---|---|---|
| **PurpleXPurple** | Human | Vision, design, decisions, testing, publishing |
| **Nexus Prime** | AI prompt | Reasoning frame, discipline, command structure, voice |
| **DeepSeek** | Language model | All code, all documentation, all bug fixes |
| **Python** | Runtime | The language |
| **Qt 6** | Framework | Rendering, windowing, events |
| **PyQt6** | Binding | Python access to Qt |
| **PyInstaller** | Build tool | `.py` → `.exe` packaging |
| **Pillow** | Image library | Icon generation |
| **CairoSVG** | Image library | Attempted, then replaced |
| **UPX** | Compressor | Considered, rejected |
| **Atari** | Inspiration | Original Pong |
| **Desktop toy tradition** | Inspiration | The entire ambient-overlay genre |
| **Keep a Changelog** | Standard | CHANGELOG format |
| **Semantic Versioning** | Standard | Version numbering |
| **MIT License** | Legal | The reason you can use this however you want |

---

## A note about how this was made

This project was made in a single continuous conversation. PurpleXPurple typed prompts. DeepSeek responded. Nexus Prime shaped the responses. The user pushed back when something looked wrong. The AI tried again. Over about twenty turns, the game went from "PyQt6 + PyOpenGL three-file 3D pong" to "single-file transparent 2D overlay with three gamemodes."

None of the code was written in a formal development environment. There was no IDE, no debugger, no test harness. PurpleXPurple pasted errors from a PowerShell terminal. DeepSeek read them and diagnosed. Nexus Prime kept the process disciplined.

The result is a real game that actually runs, ships as a `.exe`, and has documentation, a changelog, a build script, and an icon.

That's a weird way to make software. It works.

---

## If you want to contribute

See `README.md` for how to build and run from source. See `GUIDE.md` for the deep technical documentation. See `CHANGELOG.md` for what's changed.

Pull requests are welcome. Issues are welcome. Forks are welcome. You don't have to credit anyone — the MIT license is in the repo for a reason.

Just don't make the paddles hollow outlines again. We tried that. It was bad.

---

**End of collaboration.**

*Made by a human, a prompt, a model, and about forty years of open-source software.*
