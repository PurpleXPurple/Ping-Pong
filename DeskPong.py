"""Desk Pong — fullscreen transparent pong. Esc kills instantly."""

import os
import subprocess
import sys


def _bootstrap():
    try:
        import PyQt6.QtWidgets  # noqa: F401
        return
    except ImportError:
        pass
    print("[DeskPong] PyQt6 not found. Installing...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "--upgrade", "--disable-pip-version-check", "PyQt6",
        ])
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"[DeskPong] Auto-install failed: {e}")
        sys.exit(1)
    print("[DeskPong] Restarting...")
    os.execv(sys.executable, [sys.executable, *sys.argv])


_bootstrap()


import math
import random
import struct
import tempfile
import time
from collections import deque

from PyQt6.QtCore import QEvent, QPointF, QRectF, Qt, QTimer, QUrl
from PyQt6.QtGui import (QAction, QColor, QFont, QIcon, QKeySequence,
                         QPainter, QPainterPath, QPen, QPixmap, QShortcut)
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon, QWidget

try:
    from PyQt6.QtMultimedia import QSoundEffect
    HAS_SOUND = True
except Exception:
    HAS_SOUND = False


# =========================================================================
# Config
# =========================================================================

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
BALL_SPEEDS = [
    ("SLOW",   dict(base=0.090, mx=0.240, speedup=1.015)),
    ("NORMAL", dict(base=0.120, mx=0.330, speedup=1.022)),
    ("FAST",   dict(base=0.160, mx=0.440, speedup=1.028)),
]
GAMEMODES = ["CLASSIC", "CHAOS", "CRAP"]

DEFAULT_DIFF, DEFAULT_SPEED, DEFAULT_MODE = 0, 1, 0

PADDLE_W         = 18
PADDLE_H_FRAC    = 0.155
PADDLE_MARGIN_X  = 46
PLAYER_ACCEL     = 5800.0
PLAYER_DAMP      = 11.0
PLAYER_MAX_FRAC  = 1.25
BALL_R_FRAC      = 0.0085
BALL_MAX_ANGLE   = 1.00
TRAIL_LEN        = 24
WIN_SCORE        = 11
SERVE_DELAY_S    = 0.75
BANNER_S         = 2.6
FPS_MS           = 16
MAX_DT           = 0.05

CD_INVERT, CD_OVER, CD_RECALL, CD_SMASH = 1.8, 4.5, 3.5, 7.0
SMASH_SPEED      = 1.55
SMASH_WOBBLE     = 620.0
STUN_S           = 4.0
MAX_BALLS        = 3
MAX_AI_PADDLES   = 2
AI_CD_DUPE_BALL  = 10.0
AI_CD_DUPE_PAD   = 15.0
AI_CD_THROW      = 14.0

CRAP_WIN_PX      = 140.0
CRAP_WHIFF_LOCK  = 0.22
CRAP_PERFECT_PX  = 60.0

C_PANEL_BG   = QColor(  8,   8,  10, 238)
C_PANEL_EDGE = QColor(255, 255, 255,  26)
C_HAIRLINE   = QColor(255, 255, 255,  28)
C_TEXT_HI    = QColor(255, 255, 255, 235)
C_TEXT       = QColor(255, 255, 255, 190)
C_TEXT_LO    = QColor(255, 255, 255, 105)
C_KEYCAP_EDGE= QColor(255, 255, 255,  72)


# =========================================================================
# Sound
# =========================================================================

SOUNDS = {
    "click":    [(880, 0.035, "square", 0.18)],
    "hover":    [(660, 0.020, "sine",   0.08)],
    "paddle":   [(440, 0.065, "sine",   0.28)],
    "wall":     [(300, 0.045, "sine",   0.22)],
    "score":    [(600, 0.070, "sine",   0.28), (450, 0.070, "sine", 0.28),
                 (300, 0.110, "sine",   0.28)],
    "win":      [(400, 0.090, "sine",   0.28), (550, 0.090, "sine", 0.28),
                 (700, 0.090, "sine",   0.28), (900, 0.180, "sine", 0.28)],
    "power":    [(700, 0.050, "square", 0.18), (1000, 0.060, "square", 0.18)],
    "smash":    [(800, 0.045, "square", 0.28), (400, 0.080, "square", 0.28),
                 (180, 0.130, "square", 0.28)],
    "stun":     [(200, 0.240, "square", 0.22)],
    "dupe":     [(600, 0.045, "sine",   0.22), (900, 0.045, "sine", 0.22)],
    "throw":    [(300, 0.070, "sine",   0.22), (700, 0.080, "sine", 0.22)],
    "parry":    [(1100, 0.055, "square", 0.22)],
    "perfect":  [(700, 0.045, "sine",   0.22), (1100, 0.045, "sine", 0.22),
                 (1500, 0.090, "sine",   0.22)],
    "whiff":    [(180, 0.055, "square", 0.16)],
    "mode":     [(500, 0.040, "sine",   0.20), (750, 0.040, "sine", 0.20)],
}


def _synth_wav(tones, rate=22050):
    samples = []
    for (freq, dur, wave, vol) in tones:
        n = int(dur * rate)
        attack = max(1, int(0.004 * rate))
        release = max(1, int(min(0.06, dur * 0.5) * rate))
        for i in range(n):
            t = i / rate
            if i < attack:
                env = i / attack
            elif i > n - release:
                env = max(0.0, (n - i) / release)
            else:
                env = 1.0
            ph = 2.0 * math.pi * freq * t
            s = math.sin(ph) if wave == "sine" else (
                1.0 if math.sin(ph) >= 0.0 else -1.0)
            samples.append(int(s * env * vol * 32767.0))
    data = struct.pack("<%dh" % len(samples), *samples)
    header = (b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVE"
              + b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, rate,
                                      rate * 2, 2, 16)
              + b"data" + struct.pack("<I", len(data)))
    return header + data


class SoundEngine:
    def __init__(self):
        self._effects = {}
        self._dir = None
        self._ready = False

    def init(self):
        if self._ready or not HAS_SOUND:
            self._ready = True
            return
        self._ready = True
        try:
            self._dir = tempfile.mkdtemp(prefix="deskpong_sfx_")
            for name, tones in SOUNDS.items():
                path = os.path.join(self._dir, name + ".wav")
                if not os.path.exists(path):
                    with open(path, "wb") as f:
                        f.write(_synth_wav(tones))
                eff = QSoundEffect()
                eff.setSource(QUrl.fromLocalFile(path))
                eff.setVolume(0.85)
                self._effects[name] = eff
        except Exception as e:
            print(f"[DeskPong] Sound init failed: {e}")
            self._effects.clear()

    def play(self, name):
        e = self._effects.get(name)
        if e is not None:
            try:
                e.play()
            except Exception:
                pass

    def shutdown(self):
        self._effects.clear()
        if self._dir is None:
            return
        try:
            for f in os.listdir(self._dir):
                os.unlink(os.path.join(self._dir, f))
            os.rmdir(self._dir)
        except Exception:
            pass


SFX = SoundEngine()


# =========================================================================
# Helpers
# =========================================================================

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def lerp(a, b, t):
    return a + (b - a) * t


def ease_out(t):
    t = clamp(t, 0.0, 1.0)
    return 1.0 - (1.0 - t) ** 3


def predict_y(x0, y0, vx, vy, target_x, top, bottom):
    if abs(vx) < 1e-6:
        return y0
    t = (target_x - x0) / vx
    if t < 0.0:
        return y0
    y = y0 + vy * t
    span = bottom - top
    if span <= 0.0:
        return top
    period = 2.0 * span
    y = (y - top) % period
    if y < 0.0:
        y += period
    if y > span:
        y = period - y
    return top + y


def make_tray_icon():
    pm = QPixmap(32, 32)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(0, 0, 0, 220))
    p.drawEllipse(QPointF(16.5, 16.5), 11.0, 11.0)
    p.setBrush(QColor(255, 255, 255))
    p.drawEllipse(QPointF(16.0, 16.0), 9.0, 9.0)
    p.end()
    return QIcon(pm)


# =========================================================================
# Entities
# =========================================================================

class Ball:
    __slots__ = ("x", "y", "vx", "vy", "r", "alive", "is_clone",
                 "smash_t", "smash_phase", "smash_owner", "trail")

    def __init__(self, x, y, r, is_clone=False):
        self.x, self.y, self.r = x, y, r
        self.vx = self.vy = 0.0
        self.alive = True
        self.is_clone = is_clone
        self.smash_t = 0.0
        self.smash_phase = 0.0
        self.smash_owner = None
        self.trail = deque(maxlen=TRAIL_LEN)


class Paddle:
    __slots__ = ("x", "y", "w", "h", "vy", "stun_t", "is_ai", "alive", "flash")

    def __init__(self, x, y, w, h, is_ai):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.vy = 0.0
        self.stun_t = 0.0
        self.is_ai = is_ai
        self.alive = True
        self.flash = 0.0


# =========================================================================
# Button
# =========================================================================

class Button:
    __slots__ = ("label", "kind", "on_click", "rect", "value",
                 "hovered", "pressed", "hover_t", "press_t", "flash_t",
                 "pulse_t")

    def __init__(self, label, kind="option", on_click=None):
        self.label = label
        self.kind = kind
        self.on_click = on_click
        self.value = ""
        self.rect = QRectF()
        self.hovered = False
        self.pressed = False
        self.hover_t = 0.0
        self.press_t = 0.0
        self.flash_t = 0.0
        self.pulse_t = 0.0

    def update(self, dt):
        self.pulse_t += dt
        tgt = 1.0 if self.hovered else 0.0
        self.hover_t += (tgt - self.hover_t) * min(1.0, dt * 14.0)
        if self.press_t > 0.0:
            self.press_t = max(0.0, self.press_t - dt / 0.16)
        if self.flash_t > 0.0:
            self.flash_t = max(0.0, self.flash_t - dt / 0.30)

    def contains(self, pt):
        return self.rect.contains(pt)

    def fire(self):
        self.press_t = 1.0
        self.flash_t = 1.0
        SFX.play("click")
        if self.on_click:
            self.on_click()


# =========================================================================
# Main widget
# =========================================================================

class DeskPong(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Desk Pong")
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_KeyboardFocusChange, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

        self._fit_to_screen()
        self._pw = float(PADDLE_W)
        self._ph = max(60.0, self._h * PADDLE_H_FRAC)
        self._br = max(6.0, self._h * BALL_R_FRAC)
        self._lx = float(PADDLE_MARGIN_X)
        self._rx = self._w - float(PADDLE_MARGIN_X) - self._pw

        self._diff_idx = DEFAULT_DIFF
        self._speed_idx = DEFAULT_SPEED
        self._mode_idx = DEFAULT_MODE
        self._cfg = {**DIFFICULTIES[DEFAULT_DIFF][1],
                     **BALL_SPEEDS[DEFAULT_SPEED][1]}

        self._balls: list[Ball] = []
        self._player: Paddle | None = None
        self._ai_paddles: list[Paddle] = []

        self._player_score = 0
        self._ai_score = 0
        self._rally = 0
        self._serve_delay = 0.0
        self._pending_dir = 1
        self._banner_text = ""
        self._banner_t = 0.0
        self._flash_text = ""
        self._flash_t = 0.0

        self._ai_react_t = 0.0
        self._ai_err = 0.0
        self._ai_sign = 0

        self._cd_invert = self._cd_over = 0.0
        self._cd_recall = self._cd_smash = 0.0
        self._ai_cd_dupe_ball = AI_CD_DUPE_BALL
        self._ai_cd_dupe_pad = AI_CD_DUPE_PAD
        self._ai_cd_throw = AI_CD_THROW

        self._crap_side = 1
        self._crap_active = False
        self._crap_whiff_lock = 0.0
        self._crap_perfect_flash = 0.0
        self._crap_ai_planned_t = None
        self._crap_ring_t = 0.0

        self._keys = set()
        self._scene = "menu"
        self._scene_t = 0.0

        self._cache = {}
        self._ability_btns: list[Button] = []
        self._quitting = False

        self._rebuild_fonts()
        self._compute_layout()

        self._btn_start = Button("START", "primary", self._on_start)
        self._btn_mode  = Button("GAMEMODE", "option", self._cycle_mode)
        self._btn_diff  = Button("AI SKILL", "option", self._cycle_diff)
        self._btn_speed = Button("BALL SPEED", "option", self._cycle_speed)
        self._buttons = (self._btn_start, self._btn_mode,
                         self._btn_diff, self._btn_speed)
        self._refresh_options()
        self._place_buttons()
        self._build_ability_buttons()

        # Esc + F: three redundant paths, all Qt-native.
        for key in (Qt.Key.Key_Escape, Qt.Key.Key_F):
            sc = QShortcut(QKeySequence(key), self)
            sc.setContext(Qt.ShortcutContext.ApplicationShortcut)
            sc.activated.connect(self._quit)
            sc.setAutoRepeat(False)

        self._last_t = time.perf_counter()
        self._timer = QTimer(self)
        self._timer.setInterval(FPS_MS)
        self._timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

        self._focus_timer = QTimer(self)
        self._focus_timer.setInterval(1000)
        self._focus_timer.timeout.connect(self._ensure_focus)
        self._focus_timer.start()

    # -- focus ------------------------------------------------------------

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._grab_focus_now)
        QTimer.singleShot(60, self._grab_focus_now)
        QTimer.singleShot(200, self._grab_focus_now)

    def _grab_focus_now(self):
        self.raise_()
        self.activateWindow()
        self.setFocus(Qt.FocusReason.OtherFocusReason)

    def _ensure_focus(self):
        if self._quitting:
            return
        try:
            if not self.isActiveWindow():
                self._grab_focus_now()
        except Exception:
            pass

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.ActivationChange and self.isActiveWindow():
            self._keys.clear()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._keys.clear()

    def eventFilter(self, obj, event):
        if self._quitting:
            return True
        if event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_F):
                self._quit()
                return True
        return super().eventFilter(obj, event)

    # -- screen -----------------------------------------------------------

    def _fit_to_screen(self):
        scr = QApplication.primaryScreen()
        if scr is None:
            self.resize(1280, 720)
            self._w, self._h = 1280.0, 720.0
            return
        geo = scr.geometry()
        self.setGeometry(geo)
        self._w, self._h = float(geo.width()), float(geo.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._w, self._h = float(self.width()), float(self.height())
        self._ph = max(60.0, self._h * PADDLE_H_FRAC)
        self._br = max(6.0, self._h * BALL_R_FRAC)
        self._rx = self._w - float(PADDLE_MARGIN_X) - self._pw
        self._rebuild_fonts()
        self._compute_layout()
        self._place_buttons()
        self._build_ability_buttons()
        self._cache.clear()

    # -- fonts & layout ---------------------------------------------------

    def _rebuild_fonts(self):
        s = clamp(self._h / 1080.0, 0.88, 1.35)
        self._s = s

        def f(size, weight=QFont.Weight.Normal, ls=0):
            fo = QFont("Segoe UI")
            fo.setPixelSize(max(9, int(size * s)))
            fo.setWeight(weight)
            if ls:
                fo.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, ls * s)
            return fo

        self._f_title  = f(30, QFont.Weight.Black, 8)
        self._f_sub    = f(10, QFont.Weight.Medium, 3)
        self._f_start  = f(15, QFont.Weight.Bold, 6)
        self._f_opt    = f(12, QFont.Weight.DemiBold, 2)
        self._f_opt_v  = f(12, QFont.Weight.Medium, 2)
        self._f_head   = f(10, QFont.Weight.Bold, 4)
        self._f_key    = f(10, QFont.Weight.Bold, 1)
        self._f_keyw   = f(9, QFont.Weight.Bold, 1)
        self._f_body   = f(12, QFont.Weight.Normal, 0)
        self._f_score  = f(44, QFont.Weight.Black, 2)
        self._f_banner = f(32, QFont.Weight.Black, 8)
        self._f_small  = f(10, QFont.Weight.Medium, 1)

    def _compute_layout(self):
        s = self._s
        pad = 38.0 * s
        self._panel_w = 480.0 * s
        y = 0.0
        self._y_title = y + 40.0 * s;  y = self._y_title + 44.0 * s
        self._y_sub = y - 4.0 * s;     y = self._y_sub + 26.0 * s
        self._y_div1 = y + 4.0 * s;    y = self._y_div1 + 12.0 * s
        self._y_start = y + 8.0 * s;   y = self._y_start + 58.0 * s
        self._y_div2 = y + 14.0 * s;   y = self._y_div2 + 12.0 * s

        opt_h = 52.0 * s
        gap = 8.0 * s
        self._y_opt1 = y + 6.0 * s;    y = self._y_opt1 + opt_h + gap
        self._y_opt2 = y;              y = self._y_opt2 + opt_h + gap
        self._y_opt3 = y;              y = self._y_opt3 + opt_h + 14.0 * s
        self._y_div3 = y;              y = self._y_div3 + 20.0 * s
        self._y_chead = y;             y = self._y_chead + 24.0 * s
        self._y_crows = y;             y = self._y_crows + 4.0 * s
        self._row_h = 27.0 * s
        rows = 6
        content_h = y + rows * self._row_h + pad

        self._panel_h = content_h + pad
        self._h_start = 58.0 * s
        self._h_opt = opt_h

        px = (self._w - self._panel_w) * 0.5
        py = (self._h - self._panel_h) * 0.5
        self._px, self._py = px, py
        self._panel = QRectF(px, py, self._panel_w, self._panel_h)

        self._cx = px + pad
        self._cw = self._panel_w - pad * 2.0

        for k in ("_y_title", "_y_sub", "_y_div1", "_y_start", "_y_div2",
                  "_y_opt1", "_y_opt2", "_y_opt3", "_y_div3",
                  "_y_chead", "_y_crows"):
            setattr(self, k, getattr(self, k) + py)

    def _place_buttons(self):
        self._btn_start.rect = QRectF(self._cx, self._y_start,
                                      self._cw, self._h_start)
        self._btn_mode.rect  = QRectF(self._cx, self._y_opt1,
                                      self._cw, self._h_opt)
        self._btn_diff.rect  = QRectF(self._cx, self._y_opt2,
                                      self._cw, self._h_opt)
        self._btn_speed.rect = QRectF(self._cx, self._y_opt3,
                                      self._cw, self._h_opt)

    def _build_ability_buttons(self):
        s = self._s
        pill_w = 108.0 * s
        pill_h = 30.0 * s
        gap = 10.0 * s
        total = 4 * pill_w + 3 * gap
        x0 = (self._w - total) * 0.5
        y0 = self._h - pill_h - 22.0 * s
        labels = ("INVERT", "BOOST", "PULL", "SMASH")
        cbs = (self._try_invert, self._try_overdrive,
               self._try_recall, self._try_smash)
        self._ability_btns = []
        for i, (lbl, cb) in enumerate(zip(labels, cbs)):
            b = Button(lbl, "option", cb)
            b.rect = QRectF(x0 + i * (pill_w + gap), y0, pill_w, pill_h)
            self._ability_btns.append(b)

    def _refresh_options(self):
        self._btn_mode.value  = GAMEMODES[self._mode_idx]
        self._btn_diff.value  = DIFFICULTIES[self._diff_idx][0]
        self._btn_speed.value = BALL_SPEEDS[self._speed_idx][0]
        self._cache.clear()

    # -- pixmap helpers ---------------------------------------------------

    def _dpr(self):
        try:
            return float(self.devicePixelRatioF())
        except Exception:
            return 1.0

    def _new_pixmap(self, w, h):
        dpr = self._dpr()
        pm = QPixmap(max(1, int(w * dpr)), max(1, int(h * dpr)))
        pm.setDevicePixelRatio(dpr)
        pm.fill(Qt.GlobalColor.transparent)
        return pm

    # -- scene ------------------------------------------------------------

    def _set_scene(self, name):
        self._scene = name
        self._scene_t = 0.0

    def _on_start(self):
        if self._scene == "menu":
            self._set_scene("starting")

    def _cycle_mode(self):
        self._mode_idx = (self._mode_idx + 1) % len(GAMEMODES)
        self._refresh_options()
        SFX.play("mode")

    def _cycle_diff(self):
        self._diff_idx = (self._diff_idx + 1) % len(DIFFICULTIES)
        self._refresh_options()

    def _cycle_speed(self):
        self._speed_idx = (self._speed_idx + 1) % len(BALL_SPEEDS)
        self._refresh_options()

    @property
    def _mode(self):
        return GAMEMODES[self._mode_idx]

    # -- game start -------------------------------------------------------

    def _begin_game(self):
        self._cfg = {**DIFFICULTIES[self._diff_idx][1],
                     **BALL_SPEEDS[self._speed_idx][1]}
        self._player_score = self._ai_score = 0
        self._banner_text = self._flash_text = ""
        self._banner_t = self._flash_t = 0.0

        self._player = Paddle(self._lx, (self._h - self._ph) * 0.5,
                              self._pw, self._ph, is_ai=False)
        self._ai_paddles = [Paddle(self._rx, (self._h - self._ph) * 0.5,
                                   self._pw, self._ph, is_ai=True)]
        self._balls = []
        self._rally = 0
        self._cd_invert = self._cd_over = self._cd_recall = self._cd_smash = 0.0
        self._ai_cd_dupe_ball = AI_CD_DUPE_BALL
        self._ai_cd_dupe_pad = AI_CD_DUPE_PAD
        self._ai_cd_throw = AI_CD_THROW
        self._ai_sign = 0
        self._ai_react_t = self._ai_err = 0.0
        self._crap_side = 1
        self._crap_active = False
        self._crap_whiff_lock = 0.0
        self._crap_perfect_flash = 0.0
        self._crap_ai_planned_t = None
        self._crap_ring_t = 0.0

        self._cache.clear()
        self._set_scene("playing")

        if self._mode == "CRAP":
            self._crap_serve()
        else:
            self._serve(random.choice((-1, 1)))

    def _serve(self, direction):
        self._rally = 0
        speed = self._w * self._cfg["base"]
        angle = random.uniform(-0.28, 0.28)
        ball = Ball(self._w * 0.5, self._h * 0.5, self._br)
        ball.vx = math.cos(angle) * speed * direction
        ball.vy = math.sin(angle) * speed
        self._balls = [ball]
        self._serve_delay = 0.0
        self._ai_sign = 1 if ball.vx > 0 else (-1 if ball.vx < 0 else 0)
        self._ai_react_t = self._ai_err = 0.0

    def _rally_reset(self, direction):
        if self._balls:
            b = self._balls[0]
            b.x, b.y = self._w * 0.5, self._h * 0.5
            b.vx = b.vy = 0.0
            b.trail.clear()
            b.smash_t = 0.0
        else:
            self._balls = [Ball(self._w * 0.5, self._h * 0.5, self._br)]
        self._balls = self._balls[:1]
        self._pending_dir = direction
        self._serve_delay = SERVE_DELAY_S
        self._ai_sign = 0
        self._rally = 0

    def _score(self, who):
        if who > 0:
            self._player_score += 1
        else:
            self._ai_score += 1
        self._cache.clear()

        if (self._player_score >= WIN_SCORE
                or self._ai_score >= WIN_SCORE):
            self._banner_text = ("YOU WIN"
                                 if self._player_score > self._ai_score
                                 else "AI WINS")
            self._banner_t = BANNER_S
            SFX.play("win")
            self._set_scene("won")
            return

        SFX.play("score")
        if self._mode == "CRAP":
            self._crap_serve()
        else:
            self._rally_reset(1 if who < 0 else -1)

    def _crap_serve(self):
        speed = self._w * self._cfg["base"] * 0.95
        self._balls = [Ball(self._w * 0.5, self._h * 0.5, self._br)]
        self._crap_side = random.choice((-1, 1))
        self._balls[0].vx = speed * self._crap_side
        self._crap_active = False
        self._crap_whiff_lock = 0.0
        self._crap_ai_planned_t = None
        self._crap_ring_t = 0.0
        self._rally = 0

    # -- main loop --------------------------------------------------------

    def _tick(self):
        now = time.perf_counter()
        dt = now - self._last_t
        self._last_t = now
        dt = clamp(dt, 0.0005, MAX_DT)
        self._scene_t += dt
        for b in self._buttons:
            b.update(dt)
        for b in self._ability_btns:
            b.update(dt)

        sc = self._scene
        if sc == "menu":
            self.update(); return
        if sc == "starting":
            if self._scene_t >= 0.42:
                self._begin_game()
            self.update(); return
        if sc == "won":
            self._banner_t -= dt
            if self._banner_t <= 0.0:
                self._banner_text = ""
                self._set_scene("menu")
                self._cache.clear()
            self.update(); return

        if self._banner_t > 0.0:
            self._banner_t = max(0.0, self._banner_t - dt)
        if self._flash_t > 0.0:
            self._flash_t = max(0.0, self._flash_t - dt)

        if self._serve_delay > 0.0:
            self._serve_delay -= dt
            if self._serve_delay <= 0.0:
                self._serve(self._pending_dir)
            self.update(); return

        m = self._mode
        if m == "CRAP":
            self._step_crap(dt)
        elif m == "CHAOS":
            self._step_chaos(dt)
        else:
            self._step_classic(dt)
        self.update()

    # =====================================================================
    # CLASSIC
    # =====================================================================

    def _step_classic(self, dt):
        if not self._balls:
            return
        ball = self._balls[0]
        self._step_player_paddle(dt)
        self._step_ai_paddle(self._ai_paddles[0], ball, dt)
        self._integrate_ball(ball, dt)
        self._bounce_walls(ball)
        self._check_paddle_hits(ball, self._ai_paddles)
        self._check_exits()
        self._ai_reaction_tick(ball)

    # =====================================================================
    # CHAOS
    # =====================================================================

    def _step_chaos(self, dt):
        self._cd_invert = max(0.0, self._cd_invert - dt)
        self._cd_over   = max(0.0, self._cd_over - dt)
        self._cd_recall = max(0.0, self._cd_recall - dt)
        self._cd_smash  = max(0.0, self._cd_smash - dt)
        self._ai_cd_dupe_ball = max(0.0, self._ai_cd_dupe_ball - dt)
        self._ai_cd_dupe_pad  = max(0.0, self._ai_cd_dupe_pad - dt)
        self._ai_cd_throw     = max(0.0, self._ai_cd_throw - dt)

        self._step_player_paddle(dt)

        for pad in self._ai_paddles:
            pad.stun_t = max(0.0, pad.stun_t - dt)
            pad.flash = max(0.0, pad.flash - dt)
            if pad.stun_t <= 0.0:
                ball = self._nearest_incoming_ball(pad)
                if ball is not None:
                    self._step_ai_paddle(pad, ball, dt)
        self._separate_ai_paddles()

        for b in self._balls:
            if not b.alive:
                continue
            self._integrate_ball(b, dt)
            self._bounce_walls(b)
            self._check_paddle_hits(b, self._ai_paddles)
        self._resolve_ball_collisions()
        self._check_exits()

        if self._balls:
            b0 = self._balls[0]
            s = 1 if b0.vx > 0 else (-1 if b0.vx < 0 else 0)
            if s > 0 and self._ai_sign <= 0:
                self._ai_react_t = 0.0
                t = min(self._rally / 8.0, 1.0)
                err = (self._cfg["ai_err0"]
                       + (self._cfg["ai_err1"] - self._cfg["ai_err0"]) * t)
                self._ai_err = random.uniform(-1.0, 1.0) * err * self._h
                self._ai_roll_ability()
            self._ai_sign = s

    def _ai_roll_ability(self):
        if self._ai_cd_throw <= 0.0 and random.random() < 0.30:
            self._ai_throw_player(); return
        if (self._ai_cd_dupe_pad <= 0.0
                and len(self._ai_paddles) < MAX_AI_PADDLES
                and random.random() < 0.45):
            self._ai_duplicate_paddle(); return
        if (self._ai_cd_dupe_ball <= 0.0
                and len(self._balls) < MAX_BALLS
                and random.random() < 0.50):
            self._ai_duplicate_ball()

    def _ai_duplicate_ball(self):
        if not self._balls:
            return
        src = self._balls[0]
        ang = random.uniform(-0.55, 0.55)
        spd = math.hypot(src.vx, src.vy) * 1.02
        clone = Ball(src.x, src.y, self._br, is_clone=True)
        d = 1 if src.vx >= 0 else -1
        clone.vx = math.cos(ang) * spd * d
        clone.vy = math.sin(ang) * spd
        self._balls.append(clone)
        self._ai_cd_dupe_ball = AI_CD_DUPE_BALL
        self._flash("AI: DUPLICATE BALL"); SFX.play("dupe")

    def _ai_duplicate_paddle(self):
        if len(self._ai_paddles) >= MAX_AI_PADDLES:
            return
        base = self._ai_paddles[0]
        offset = random.choice((-1, 1)) * (self._ph * 0.9)
        y = clamp(base.y + offset, 0.0, self._h - self._ph)
        pad = Paddle(self._rx, y, self._pw, self._ph, is_ai=True)
        pad.flash = 1.0
        self._ai_paddles.append(pad)
        self._ai_cd_dupe_pad = AI_CD_DUPE_PAD
        self._flash("AI: DUPLICATE PADDLE"); SFX.play("dupe")

    def _ai_throw_player(self):
        if self._player is None:
            return
        target = self._h * 0.5 + random.uniform(-0.22, 0.22) * self._h
        self._player.y = clamp(target - self._ph * 0.5, 0.0, self._h - self._ph)
        self._player.vy = 0.0
        self._player.flash = 1.0
        self._ai_cd_throw = AI_CD_THROW
        self._flash("AI: THREW YOU"); SFX.play("throw")

    def _nearest_incoming_ball(self, pad):
        best = None; best_t = 1e9
        for b in self._balls:
            if not b.alive or b.vx <= 0.0:
                continue
            dx = pad.x - b.x
            if dx <= 0.0 or abs(b.vx) < 1e-6:
                continue
            t = dx / b.vx
            if t < best_t:
                best_t = t; best = b
        return best

    def _separate_ai_paddles(self):
        if len(self._ai_paddles) < 2:
            return
        a, b = self._ai_paddles[0], self._ai_paddles[1]
        top, bot = (a, b) if a.y < b.y else (b, a)
        overlap = (top.y + top.h) - bot.y
        if overlap > 0.0:
            push = overlap * 0.5
            top.y = clamp(top.y - push, 0.0, self._h - top.h)
            bot.y = clamp(bot.y + push, 0.0, self._h - bot.h)

    def _resolve_ball_collisions(self):
        n = len(self._balls)
        for i in range(n):
            a = self._balls[i]
            if not a.alive:
                continue
            for j in range(i + 1, n):
                b = self._balls[j]
                if not b.alive:
                    continue
                dx = a.x - b.x; dy = a.y - b.y
                rr = a.r + b.r
                if dx * dx + dy * dy <= rr * rr:
                    a.vx, b.vx = b.vx, a.vx
                    a.vy, b.vy = b.vy, a.vy
                    d = math.hypot(dx, dy) or 1.0
                    nx, ny = dx / d, dy / d
                    push = rr - d + 0.5
                    a.x += nx * push * 0.5; a.y += ny * push * 0.5
                    b.x -= nx * push * 0.5; b.y -= ny * push * 0.5

    def _try_invert(self):
        if self._cd_invert > 0.0 or not self._balls:
            return
        for b in self._balls:
            b.vx = -b.vx
        self._cd_invert = CD_INVERT
        self._flash("INVERT"); SFX.play("power")

    def _try_overdrive(self):
        if self._cd_over > 0.0 or not self._balls:
            return
        for b in self._balls:
            b.vx *= 1.55; b.vy *= 1.55
        self._cd_over = CD_OVER
        self._flash("OVERDRIVE"); SFX.play("power")

    def _try_recall(self):
        if self._cd_recall > 0.0 or not self._balls:
            return
        for b in self._balls:
            b.vx = -abs(b.vx) * 1.15
        self._cd_recall = CD_RECALL
        self._flash("RECALL"); SFX.play("power")

    def _try_smash(self):
        if self._cd_smash > 0.0 or not self._balls:
            return
        b = self._balls[0]
        if b.vx <= 0.0:
            self._flash("SMASH BLOCKED"); SFX.play("whiff"); return
        b.smash_t = 1.6; b.smash_phase = 0.0; b.smash_owner = "player"
        b.vx *= SMASH_SPEED; b.vy = 0.0
        self._cd_smash = CD_SMASH
        self._flash("SMASH!"); SFX.play("smash")

    # =====================================================================
    # CRAP
    # =====================================================================

    def _step_crap(self, dt):
        if not self._balls:
            return
        ball = self._balls[0]
        self._crap_whiff_lock = max(0.0, self._crap_whiff_lock - dt)
        self._crap_perfect_flash = max(0.0, self._crap_perfect_flash - dt)

        ball.trail.appendleft((ball.x, ball.y))
        ball.x += ball.vx * dt

        side_paddle_x = self._lx if self._crap_side < 0 else self._rx

        if self._crap_side > 0:
            win_edge = side_paddle_x - CRAP_WIN_PX
        else:
            win_edge = side_paddle_x + self._pw + CRAP_WIN_PX

        if self._crap_side < 0:
            distance = abs(ball.x - (side_paddle_x + self._pw))
            total = CRAP_WIN_PX + (self._w * 0.5)
            self._crap_ring_t = clamp(1.0 - (distance / total), 0.0, 1.0)
        else:
            self._crap_ring_t = 0.0

        if not self._crap_active:
            if self._crap_side > 0 and ball.x >= win_edge:
                self._crap_active = True
                self._plan_ai_parry(ball)
            elif self._crap_side < 0 and ball.x <= win_edge:
                self._crap_active = True

        if self._crap_side > 0 and self._crap_active:
            if self._crap_ai_planned_t is not None:
                self._crap_ai_planned_t -= dt
                if self._crap_ai_planned_t <= 0.0:
                    self._crap_ai_planned_t = None
                    perfect_x = side_paddle_x - CRAP_PERFECT_PX
                    perfect = abs(ball.x - perfect_x) < CRAP_PERFECT_PX * 0.55
                    self._do_parry(-1, perfect, ai=True)

        if self._crap_side > 0:
            if ball.x + ball.r >= side_paddle_x:
                self._crap_miss()
        else:
            if ball.x - ball.r <= side_paddle_x + self._pw:
                self._crap_miss()

    def _plan_ai_parry(self, ball):
        acc = self._cfg.get("parry_acc", 0.60)
        if random.random() < acc:
            speed = abs(ball.vx) or 1.0
            self._crap_ai_planned_t = random.uniform(
                0.05, CRAP_WIN_PX / speed * 0.70)
        else:
            self._crap_ai_planned_t = None

    def _do_parry(self, direction, perfect, ai=False):
        if not self._balls:
            return
        ball = self._balls[0]
        self._rally += 1
        self._crap_active = False
        self._crap_ai_planned_t = None
        self._crap_side = direction
        self._crap_ring_t = 0.0
        speed = abs(ball.vx) * (1.18 if perfect else 1.06)
        speed = min(speed, self._w * self._cfg["mx"])
        ball.vx = speed * direction
        if perfect:
            self._crap_perfect_flash = 0.35
            SFX.play("perfect")
        else:
            SFX.play("parry")

    def _crap_miss(self):
        if self._crap_side > 0:
            self._score(+1)
        else:
            self._score(-1)
        SFX.play("whiff")

    def _crap_player_click(self):
        if self._crap_side != -1 or not self._crap_active:
            if self._crap_whiff_lock <= 0.0:
                self._crap_whiff_lock = CRAP_WHIFF_LOCK
                SFX.play("whiff")
            return
        if self._crap_whiff_lock > 0.0:
            return
        ball = self._balls[0]
        perfect_x = self._lx + self._pw + CRAP_PERFECT_PX
        perfect = abs(ball.x - perfect_x) < CRAP_PERFECT_PX * 0.55
        self._do_parry(+1, perfect, ai=False)

    # =====================================================================
    # Physics helpers
    # =====================================================================

    def _step_player_paddle(self, dt):
        pad = self._player
        if pad is None:
            return
        max_speed = self._h * PLAYER_MAX_FRAC
        dy = 0.0
        if Qt.Key.Key_Up in self._keys or Qt.Key.Key_W in self._keys:
            dy -= 1.0
        if Qt.Key.Key_Down in self._keys or Qt.Key.Key_S in self._keys:
            dy += 1.0
        if dy != 0.0:
            pad.vy += dy * PLAYER_ACCEL * dt
        pad.vy *= max(0.0, 1.0 - PLAYER_DAMP * dt)
        if pad.vy > max_speed: pad.vy = max_speed
        elif pad.vy < -max_speed: pad.vy = -max_speed
        pad.y += pad.vy * dt
        if pad.y < 0.0:
            pad.y = 0.0; pad.vy = 0.0
        elif pad.y > self._h - pad.h:
            pad.y = self._h - pad.h; pad.vy = 0.0

    def _step_ai_paddle(self, pad, ball, dt):
        if pad.stun_t > 0.0:
            return
        if ball.vx > 0.0:
            self._ai_react_t += dt
        if ball.vx <= 0.0 or self._ai_react_t < self._cfg["ai_react"]:
            target = self._h * 0.5
        else:
            top, bot = self._br, self._h - self._br
            target = predict_y(ball.x, ball.y, ball.vx, ball.vy,
                               pad.x, top, bot) + self._ai_err
        speed = self._h * self._cfg["ai_speed"]
        center = pad.y + pad.h * 0.5
        diff = target - center
        if abs(diff) < self._cfg["ai_dead"]:
            return
        step = clamp(diff, -speed * dt, speed * dt)
        pad.y = clamp(pad.y + step, 0.0, self._h - pad.h)

    def _integrate_ball(self, ball, dt):
        ball.trail.appendleft((ball.x, ball.y))
        if ball.smash_t > 0.0:
            ball.smash_t -= dt
            ball.smash_phase += dt
            ball.vy = math.sin(ball.smash_phase * 22.0) * SMASH_WOBBLE
            if ball.smash_t <= 0.0:
                ball.smash_owner = None
        ball.x += ball.vx * dt
        ball.y += ball.vy * dt

    def _bounce_walls(self, ball):
        if ball.y - ball.r < 0.0:
            ball.y = ball.r; ball.vy = abs(ball.vy); SFX.play("wall")
        elif ball.y + ball.r > self._h:
            ball.y = self._h - ball.r; ball.vy = -abs(ball.vy); SFX.play("wall")

    def _check_paddle_hits(self, ball, ai_paddles):
        if ball.vx < 0.0 and self._overlaps(ball, self._player):
            self._bounce_off_paddle(ball, self._player, +1, self._player.vy)
            self._player.flash = 1.0
        if ball.vx > 0.0:
            for pad in ai_paddles:
                if self._overlaps(ball, pad):
                    self._bounce_off_paddle(ball, pad, -1, 0.0)
                    pad.flash = 1.0
                    if ball.smash_owner == "player":
                        pad.stun_t = STUN_S
                        ball.smash_t = 0.0
                        ball.smash_owner = None
                        self._flash("AI STUNNED 4s"); SFX.play("stun")
                    break

    def _overlaps(self, ball, pad):
        if pad is None:
            return False
        return (ball.x + ball.r >= pad.x
                and ball.x - ball.r <= pad.x + pad.w
                and ball.y + ball.r >= pad.y
                and ball.y - ball.r <= pad.y + pad.h)

    def _bounce_off_paddle(self, ball, pad, dir_x, paddle_vy):
        if dir_x > 0:
            ball.x = pad.x + pad.w + ball.r + 0.5
        else:
            ball.x = pad.x - ball.r - 0.5
        self._rally += 1
        base = max(math.hypot(ball.vx, ball.vy), self._w * self._cfg["base"])
        self._speed = min(base * self._cfg["speedup"], self._w * self._cfg["mx"])
        center = pad.y + pad.h * 0.5
        offset = clamp((ball.y - center) / (pad.h * 0.5), -1.0, 1.0)
        angle = offset * BALL_MAX_ANGLE
        ball.vx = math.cos(angle) * self._speed * dir_x
        ball.vy = math.sin(angle) * self._speed + paddle_vy * 0.10
        sp = math.hypot(ball.vx, ball.vy)
        if sp > 1e-4:
            k = self._speed / sp
            ball.vx *= k; ball.vy *= k
        SFX.play("paddle")

    def _check_exits(self):
        alive = []; scored = 0
        for b in self._balls:
            if not b.alive:
                continue
            if b.x - b.r > self._w - PADDLE_MARGIN_X * 0.7:
                scored = +1; continue
            if b.x + b.r < PADDLE_MARGIN_X * 0.7:
                scored = -1; continue
            alive.append(b)
        if scored != 0:
            self._score(scored)
            return
        self._balls = alive

    def _ai_reaction_tick(self, ball):
        s = 1 if ball.vx > 0 else (-1 if ball.vx < 0 else 0)
        if s > 0 and self._ai_sign <= 0:
            self._ai_react_t = 0.0
            t = min(self._rally / 8.0, 1.0)
            err = (self._cfg["ai_err0"]
                   + (self._cfg["ai_err1"] - self._cfg["ai_err0"]) * t)
            self._ai_err = random.uniform(-1.0, 1.0) * err * self._h
        self._ai_sign = s

    def _flash(self, text):
        self._flash_text = text
        self._flash_t = 1.4

    # =====================================================================
    # Input
    # =====================================================================

    def keyPressEvent(self, event):
        k = event.key()
        if k in (Qt.Key.Key_Escape, Qt.Key.Key_F):
            self._quit(); return
        if k == Qt.Key.Key_Backspace:
            if self._scene in ("playing", "won"):
                self._banner_text = ""
                self._banner_t = 0.0
                self._set_scene("menu")
                self._cache.clear()
            return
        if self._scene == "playing":
            m = self._mode
            if m == "CHAOS":
                if k in (Qt.Key.Key_1, Qt.Key.Key_Z):
                    self._try_invert()
                elif k in (Qt.Key.Key_2, Qt.Key.Key_X):
                    self._try_overdrive()
                elif k in (Qt.Key.Key_3, Qt.Key.Key_C):
                    self._try_recall()
                elif k in (Qt.Key.Key_4, Qt.Key.Key_V):
                    self._try_smash()
            elif m == "CRAP":
                if k in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self._crap_player_click()
        self._keys.add(k)

    def keyReleaseEvent(self, event):
        self._keys.discard(event.key())

    def mousePressEvent(self, event):
        self._grab_focus_now()
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = event.position()
        if self._scene == "menu":
            for b in self._buttons:
                if b.contains(pos):
                    b.pressed = True
                    b.press_t = 1.0
                    return
        elif self._scene == "playing":
            m = self._mode
            if m == "CRAP":
                self._crap_player_click()
            elif m == "CHAOS":
                for b in self._ability_btns:
                    if b.contains(pos):
                        b.pressed = True
                        b.press_t = 1.0
                        return

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = event.position()
        if self._scene == "menu":
            for b in self._buttons:
                was = b.pressed
                b.pressed = False
                if was and b.contains(pos):
                    b.fire(); return
        elif self._scene == "playing" and self._mode == "CHAOS":
            for b in self._ability_btns:
                was = b.pressed
                b.pressed = False
                if was and b.contains(pos):
                    b.fire(); return

    def mouseMoveEvent(self, event):
        if self._scene != "menu":
            if self._scene == "playing" and self._mode == "CHAOS":
                pos = event.position()
                any_hover = False
                for b in self._ability_btns:
                    b.hovered = b.contains(pos)
                    any_hover = any_hover or b.hovered
                self.setCursor(Qt.CursorShape.PointingHandCursor if any_hover
                               else Qt.CursorShape.ArrowCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            return
        pos = event.position()
        any_hover = False
        for b in self._buttons:
            was = b.hovered
            b.hovered = b.contains(pos)
            if b.hovered and not was:
                SFX.play("hover")
            any_hover = any_hover or b.hovered
        self.setCursor(Qt.CursorShape.PointingHandCursor if any_hover
                       else Qt.CursorShape.ArrowCursor)

    def _quit(self):
        if self._quitting:
            return
        self._quitting = True
        try:
            SFX.shutdown()
        except Exception:
            pass
        # Raw process exit — no Qt event loop, no tray keep-alive, no threads.
        os._exit(0)

    # =====================================================================
    # Paint
    # =====================================================================

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        sc = self._scene
        if sc == "menu":
            self._paint_menu(p, 1.0)
        elif sc == "starting":
            a = 1.0 - ease_out(self._scene_t / 0.42)
            self._paint_menu(p, a, force_start_hover=True)
        elif sc == "won":
            self._paint_game(p, 1.0)
            self._paint_banner(p)
        else:
            self._paint_game(p, 1.0)
        p.end()

    # --- cached builds --------------------------------------------------

    def _build_center_line(self):
        w, h = int(self._w), int(self._h)
        pm = self._new_pixmap(w, h)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setPen(QPen(QColor(255, 255, 255, 26), 2.5,
                      Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        x = w * 0.5
        dash = max(10.0, h * 0.012)
        gap = dash * 0.85
        y = 0.0
        while y < h:
            p.drawLine(QPointF(x, y), QPointF(x, y + dash))
            y += dash + gap
        p.end()
        return pm

    def _build_score_pixmap(self, value):
        s = self._s
        box_w = int(180.0 * s)
        box_h = int(100.0 * s)
        pm = self._new_pixmap(box_w, box_h)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        p.setFont(self._f_score)
        text = str(value)
        rect = QRectF(0, 0, box_w, box_h)
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            p.setPen(QPen(QColor(0, 0, 0, 190), 1.0))
            p.drawText(rect.translated(dx, dy),
                       Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                       text)
        p.setPen(QPen(QColor(255, 255, 255, 235), 1.0))
        p.drawText(rect,
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, text)
        p.end()
        return pm

    def _build_menu_bg(self):
        s = self._s
        pw = int(self._panel_w)
        ph = int(self._panel_h)
        pm = self._new_pixmap(pw, ph)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        p.translate(-self._px, -self._py)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(C_PANEL_BG)
        p.drawRoundedRect(self._panel, 6.0 * s, 6.0 * s)
        p.setPen(QPen(C_PANEL_EDGE, 1.0))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(self._panel, 6.0 * s, 6.0 * s)

        p.setFont(self._f_title)
        p.setPen(QPen(C_TEXT_HI, 1.0))
        p.drawText(QRectF(self._cx, self._y_title, self._cw, 40.0 * s),
                   Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                   "DESK PONG")
        p.setFont(self._f_sub)
        p.setPen(QPen(C_TEXT_LO, 1.0))
        p.drawText(QRectF(self._cx, self._y_sub, self._cw, 18.0 * s),
                   Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                   "A MINIMAL PONG")
        p.setPen(QPen(C_HAIRLINE, 1.0))
        for yy in (self._y_div1, self._y_div2, self._y_div3):
            p.drawLine(QPointF(self._cx, yy), QPointF(self._cx + self._cw, yy))
        self._paint_controls_static(p)
        p.end()
        return pm

    def _paint_controls_static(self, p):
        s = self._s
        p.setFont(self._f_head)
        p.setPen(QPen(C_TEXT_LO, 1.0))
        p.drawText(QRectF(self._cx, self._y_chead, self._cw, 16.0 * s),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                   "CONTROLS")
        m = self._mode
        if m == "CHAOS":
            rows = ((["\u2191", "\u2193"], "Move"),
                    (["W", "S"], "Move (alt)"),
                    (["1-4"], "Abilities (numpad)"),
                    (["Z X C V"], "Abilities (alt)"),
                    (["ESC"], "Quit"),
                    (["BKSP"], "Back to menu"))
        elif m == "CRAP":
            rows = ((["CLICK"], "Parry (timing)"),
                    (["SPACE"], "Parry (alt)"),
                    (["ESC"], "Quit"),
                    (["BKSP"], "Back to menu"),
                    ([], ""),
                    ([], ""))
        else:
            rows = ((["\u2191", "\u2193"], "Move your paddle"),
                    (["W", "S"], "Move (alt)"),
                    (["ESC"], "Quit"),
                    (["BKSP"], "Back to menu"),
                    ([], ""),
                    ([], ""))

        desc_x = self._cx + 148.0 * s
        y = self._y_crows
        row_h = self._row_h
        for keys, desc in rows:
            if not keys and not desc:
                y += row_h; continue
            x = self._cx
            for k in keys:
                if len(k) == 1:
                    w = 24.0 * s; fnt = self._f_key
                elif len(k) <= 3:
                    w = 34.0 * s; fnt = self._f_key
                else:
                    w = 68.0 * s; fnt = self._f_keyw
                hh = 22.0 * s
                kr = QRectF(x, y + (row_h - hh) * 0.5, w, hh)
                p.setPen(QPen(C_KEYCAP_EDGE, 1.0))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawRoundedRect(kr, 4.0 * s, 4.0 * s)
                p.setFont(fnt)
                p.setPen(QPen(C_TEXT_HI, 1.0))
                p.drawText(kr, Qt.AlignmentFlag.AlignCenter, k)
                x += w + 5.0 * s
            p.setFont(self._f_body)
            p.setPen(QPen(C_TEXT, 1.0))
            p.drawText(QRectF(desc_x, y, self._cx + self._cw - desc_x, row_h),
                       Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                       desc)
            y += row_h

    # --- menu -----------------------------------------------------------

    def _paint_menu(self, p, alpha, force_start_hover=False):
        s = self._s
        entrance = ease_out(min(1.0, self._scene_t / 0.36))
        slide = (1.0 - entrance) * 14.0 * s
        alpha *= entrance
        if alpha <= 0.001:
            return

        key = ("menu_bg", self._mode)
        bg = self._cache.get(key)
        if bg is None:
            bg = self._build_menu_bg()
            self._cache[key] = bg
        p.setOpacity(alpha)
        p.drawPixmap(QPointF(self._px, self._py + slide), bg)
        p.setOpacity(1.0)

        for b in self._buttons:
            r = b.rect.translated(0, slide)
            if b is self._btn_start:
                self._paint_primary(p, b, r, alpha,
                                    force_hover=force_start_hover)
            else:
                self._paint_option(p, b, r, alpha)

    def _paint_primary(self, p, b, rect, alpha, force_hover=False):
        s = self._s
        hover = 1.0 if force_hover else b.hover_t
        scale = (1.0 + 0.012 * hover) * (1.0 - 0.035 * b.press_t)
        cx, cy = rect.center().x(), rect.center().y()
        r = QRectF(cx - rect.width() * scale * 0.5,
                   cy - rect.height() * scale * 0.5,
                   rect.width() * scale, rect.height() * scale)

        lvl = int(lerp(8, 255, hover))
        pulse = 0.5 + 0.5 * math.sin(b.pulse_t * 2.4)
        border_a = int((110 + 100 * pulse) if hover < 0.5 else 255)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(lvl, lvl, lvl, int(255 * alpha)))
        p.drawRoundedRect(r, 4.0 * s, 4.0 * s)

        if b.flash_t > 0.0:
            p.setBrush(QColor(255, 255, 255, int(200 * b.flash_t * alpha)))
            p.drawRoundedRect(r, 4.0 * s, 4.0 * s)

        p.setPen(QPen(QColor(255, 255, 255,
                             min(255, int(border_a * alpha))), 1.4))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(r, 4.0 * s, 4.0 * s)

        txt = int(lerp(255, 0, hover))
        p.setFont(self._f_start)
        p.setPen(QPen(QColor(txt, txt, txt, int(255 * alpha)), 1.0))
        p.drawText(r, Qt.AlignmentFlag.AlignCenter, b.label)

        if hover < 0.9:
            phase = (b.pulse_t * 0.45) % 1.0
            sweep_len = 42.0 * s
            left = r.left() + 10.0 * s
            right = r.right() - sweep_len - 10.0 * s
            if right > left:
                x = left + (right - left) * phase
                fade = max(0.0, math.sin(phase * math.pi)) ** 0.5
                line = QRectF(x, r.bottom() - 3.0 * s, sweep_len, 1.6 * s)
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QColor(255, 255, 255,
                                  int(220 * fade * alpha * (1.0 - hover))))
                p.drawRoundedRect(line, 0.8 * s, 0.8 * s)

    def _paint_option(self, p, b, rect, alpha):
        s = self._s
        hover = b.hover_t
        scale = 1.0 - 0.012 * b.press_t
        cx, cy = rect.center().x(), rect.center().y()
        r = QRectF(cx - rect.width() * scale * 0.5,
                   cy - rect.height() * scale * 0.5,
                   rect.width() * scale, rect.height() * scale)

        if hover > 0.01:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(255, 255, 255, int(14 * hover * alpha)))
            p.drawRoundedRect(r, 3.0 * s, 3.0 * s)
        if b.flash_t > 0.0:
            p.setBrush(QColor(255, 255, 255, int(90 * b.flash_t * alpha)))
            p.drawRoundedRect(r, 3.0 * s, 3.0 * s)

        p.setFont(self._f_opt)
        p.setPen(QPen(C_TEXT, 1.0))
        pad = 20.0 * s
        inner = r.adjusted(pad, 0, -pad, 0)
        p.drawText(inner,
                   Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                   b.label)
        p.setFont(self._f_opt_v)
        p.setPen(QPen(C_TEXT_HI, 1.0))
        p.drawText(inner.translated(4.0 * hover, 0.0),
                   Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                   f"{b.value}   \u203A")

    # --- game -----------------------------------------------------------

    def _paint_game(self, p, alpha):
        cl = self._cache.get("center_line")
        if cl is None:
            cl = self._build_center_line()
            self._cache["center_line"] = cl
        p.setOpacity(alpha)
        p.drawPixmap(0, 0, cl)

        if self._mode == "CRAP":
            self._paint_crap(p, alpha)
        else:
            self._paint_classic_or_chaos(p, alpha)

        self._paint_scores(p, alpha)
        p.setOpacity(1.0)

        if self._flash_t > 0.0:
            self._paint_flash(p)

    def _paint_classic_or_chaos(self, p, alpha):
        p.setPen(Qt.PenStyle.NoPen)
        for ball in self._balls:
            n = len(ball.trail)
            for i in range(n - 1, -1, -1):
                tx, ty = ball.trail[i]
                t = 1.0 - i / n
                a = int(150.0 * t * t * alpha)
                if a <= 0:
                    continue
                c = 190 if ball.is_clone else 255
                radius = ball.r * (0.30 + 0.70 * t)
                p.setBrush(QColor(c, c, c, a))
                p.drawEllipse(QPointF(tx, ty), radius, radius)

        for ball in self._balls:
            self._paint_ball(p, ball, alpha)

        if self._player is not None:
            self._draw_paddle(p, self._player, is_player=True, alpha=alpha)
        for pad in self._ai_paddles:
            if pad.stun_t > 0.0:
                self._draw_paddle(p, pad, is_player=False, alpha=alpha,
                                  stunned=True)
            else:
                self._draw_paddle(p, pad, is_player=False, alpha=alpha)

        if self._mode == "CHAOS":
            self._paint_chaos_hud(p, alpha)

    def _paint_ball(self, p, ball, alpha):
        r = ball.r
        x, y = ball.x, ball.y
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0, int(210 * alpha)))
        p.drawEllipse(QPointF(x, y), r + 1.8, r + 1.8)

        if ball.smash_t > 0.0:
            for i in range(6, 0, -1):
                a = int(55 * alpha * (i / 6.0) ** 1.5)
                p.setBrush(QColor(255, 255, 255, a))
                p.drawEllipse(QPointF(x, y), r + i * 4.5, r + i * 4.5)

        v = 190 if ball.is_clone else 255
        p.setBrush(QColor(v, v, v, int(255 * alpha)))
        p.drawEllipse(QPointF(x, y), r, r)

        if r >= 5.0:
            shadow = QPainterPath()
            shadow.addEllipse(QPointF(x - r * 0.18, y - r * 0.18),
                              r * 0.72, r * 0.72)
            clip = QPainterPath()
            clip.addEllipse(QPointF(x, y), r * 0.92, r * 0.92)
            shadow = shadow.subtracted(clip)
            p.setBrush(QColor(0, 0, 0, int(55 * alpha)))
            p.drawPath(shadow)

    def _draw_paddle(self, p, pad, is_player, alpha, stunned=False):
        s = self._s
        radius = 5.0 * s
        rect = QRectF(pad.x, pad.y, pad.w, pad.h)

        if pad.flash > 0.0:
            p.setPen(Qt.PenStyle.NoPen)
            for i in range(6, 0, -1):
                a = int(140 * pad.flash * alpha * (i / 6.0) ** 1.4)
                if a <= 0:
                    continue
                p.setBrush(QColor(255, 255, 255, a))
                rr = rect.adjusted(-i * 3.5, -i * 2.5, i * 3.5, i * 2.5)
                p.drawRoundedRect(rr, radius + i * 1.5, radius + i * 1.5)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0, int(210 * alpha)))
        p.drawRoundedRect(rect.adjusted(-1.8, -1.8, 1.8, 1.8),
                          radius + 1.5, radius + 1.5)

        if stunned:
            pulse = 0.5 + 0.5 * math.sin(self._scene_t * 14.0)
            a = int((140 + 100 * pulse) * alpha)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(255, 255, 255, a), 2.2))
            p.drawRoundedRect(rect, radius, radius)
        elif is_player:
            p.setBrush(QColor(255, 255, 255, int(255 * alpha)))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(rect, radius, radius)
            p.setPen(QPen(QColor(0, 0, 0, int(70 * alpha)), 1.0))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(rect.adjusted(1.5, 1.5, -1.5, -1.5),
                              radius * 0.7, radius * 0.7)
        else:
            p.setBrush(QColor(0, 0, 0, int(235 * alpha)))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(rect, radius, radius)
            p.setPen(QPen(QColor(255, 255, 255, int(230 * alpha)), 2.0))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(rect.adjusted(1.0, 1.0, -1.0, -1.0),
                              radius * 0.8, radius * 0.8)

        if stunned:
            p.setFont(self._f_small)
            p.setPen(QPen(QColor(255, 255, 255, int(220 * alpha)), 1.0))
            p.drawText(QRectF(pad.x - 20, pad.y - 26 * s, pad.w + 40, 22 * s),
                       Qt.AlignmentFlag.AlignCenter, "!!!")

    def _paint_chaos_hud(self, p, alpha):
        s = self._s
        cds = (self._cd_invert, self._cd_over, self._cd_recall, self._cd_smash)
        cdm = (CD_INVERT, CD_OVER, CD_RECALL, CD_SMASH)
        labels = ("INVERT", "BOOST", "PULL", "SMASH")

        for idx, (b, cd, cd_max, label) in enumerate(
                zip(self._ability_btns, cds, cdm, labels)):
            x, y0 = b.rect.x(), b.rect.y()
            pill_w, pill_h = b.rect.width(), b.rect.height()
            ready = cd <= 0.0
            hover = b.hover_t
            bg_a = int((30 + 22 * hover) if ready else 10)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(255, 255, 255, int(bg_a * alpha)))
            p.drawRoundedRect(b.rect, 4.0 * s, 4.0 * s)
            edge_a = int((60 + 120 * hover) if ready else 40)
            p.setPen(QPen(QColor(255, 255, 255, int(edge_a * alpha)), 1.0))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(b.rect, 4.0 * s, 4.0 * s)

            kr = QRectF(x + 6.0 * s, y0 + 5.0 * s, 24.0 * s, pill_h - 10.0 * s)
            p.setPen(QPen(QColor(255, 255, 255, int(110 * alpha)), 1.0))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(kr, 3.0 * s, 3.0 * s)
            p.setFont(self._f_key)
            tc = 235 if ready else 90
            p.setPen(QPen(QColor(255, 255, 255, int(tc * alpha)), 1.0))
            p.drawText(kr, Qt.AlignmentFlag.AlignCenter, str(idx + 1))

            p.setFont(self._f_small)
            p.setPen(QPen(QColor(255, 255, 255,
                                 int((200 if ready else 80) * alpha)), 1.0))
            p.drawText(QRectF(x + 34.0 * s, y0, pill_w - 40.0 * s, pill_h),
                       Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                       label)

            if not ready:
                frac = 1.0 - (cd / cd_max)
                bar = QRectF(x, y0 + pill_h - 3.0 * s, pill_w * frac, 2.0 * s)
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QColor(255, 255, 255, int(160 * alpha)))
                p.drawRoundedRect(bar, 1.0 * s, 1.0 * s)

    # --- crap -----------------------------------------------------------

    def _paint_crap(self, p, alpha):
        s = self._s
        if self._balls:
            ball = self._balls[0]
            n = len(ball.trail)
            p.setPen(Qt.PenStyle.NoPen)
            for i in range(n - 1, -1, -1):
                tx, ty = ball.trail[i]
                t = 1.0 - i / n
                a = int(150.0 * t * t * alpha)
                if a <= 0:
                    continue
                p.setBrush(QColor(255, 255, 255, a))
                radius = ball.r * (0.30 + 0.70 * t)
                p.drawEllipse(QPointF(tx, ty), radius, radius)

        self._draw_sword(p, self._lx + self._pw * 0.5, self._h * 0.5,
                         0.55 * self._h, alpha)
        self._draw_sword(p, self._rx + self._pw * 0.5, self._h * 0.5,
                         0.55 * self._h, alpha)

        if self._crap_side < 0:
            wx = self._lx + self._pw + CRAP_WIN_PX
            sweet = self._lx + self._pw + CRAP_PERFECT_PX
        else:
            wx = self._rx - CRAP_WIN_PX
            sweet = self._rx - CRAP_PERFECT_PX

        p.setPen(QPen(QColor(255, 255, 255,
                             int((60 if not self._crap_active else 110) * alpha)),
                      1.4))
        y = self._h * 0.18; end = self._h * 0.82; dash = 8.0 * s
        while y < end:
            p.drawLine(QPointF(wx, y), QPointF(wx, y + dash))
            y += dash * 2.0

        p.setPen(QPen(QColor(255, 255, 255,
                             int((80 if not self._crap_active else 160) * alpha)),
                      2.2))
        p.drawLine(QPointF(sweet, self._h * 0.30),
                   QPointF(sweet, self._h * 0.70))

        if self._crap_side < 0 and self._balls:
            t = self._crap_ring_t
            if t > 0.02:
                cx = self._lx + self._pw * 0.5
                cy = self._h * 0.5
                base_r = max(60.0, self._ph * 1.2)
                r = base_r - t * (base_r - self._ph * 0.85)
                a = int((40 + 200 * t * t) * alpha)
                p.setPen(QPen(QColor(255, 255, 255, a), 2.5))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(QPointF(cx, cy), r, r)
                if t > 0.85:
                    p.setPen(QPen(QColor(255, 255, 255, int(240 * alpha)), 3.5))
                    p.drawEllipse(QPointF(cx, cy), r * 0.95, r * 0.95)

        if self._balls:
            self._paint_ball(p, self._balls[0], alpha)

        if self._crap_perfect_flash > 0.0:
            f = self._crap_perfect_flash / 0.35
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(255, 255, 255, int(60 * f * alpha)))
            p.drawRect(QRectF(0, 0, self._w, self._h))

        label = "YOUR PARRY" if self._crap_side < 0 else "AI PARRY"
        p.setFont(self._f_head)
        p.setPen(QPen(QColor(255, 255, 255, int(150 * alpha)), 1.0))
        p.drawText(QRectF(0, self._h * 0.10, self._w, 24 * s),
                   Qt.AlignmentFlag.AlignCenter, label)

        if self._crap_whiff_lock > 0.0:
            a = int(200 * (self._crap_whiff_lock / CRAP_WHIFF_LOCK) * alpha)
            p.setPen(QPen(QColor(255, 255, 255, a), 2.0))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(
                QRectF(self._lx - 20 * s, self._h * 0.5 - 60 * s,
                       self._pw + 40 * s, 120 * s), 6 * s, 6 * s)

    def _draw_sword(self, p, x, y_center, length, alpha):
        s = self._s
        half = length * 0.5
        p.setPen(QPen(QColor(0, 0, 0, int(220 * alpha)), 5.0))
        p.drawLine(QPointF(x, y_center - half), QPointF(x, y_center + half))
        p.setPen(QPen(QColor(255, 255, 255, int(240 * alpha)), 3.0))
        p.drawLine(QPointF(x, y_center - half), QPointF(x, y_center + half))
        p.setPen(QPen(QColor(0, 0, 0, int(220 * alpha)), 6.0))
        p.drawLine(QPointF(x - 14 * s, y_center + half - 14 * s),
                   QPointF(x + 14 * s, y_center + half - 14 * s))
        p.setPen(QPen(QColor(255, 255, 255, int(200 * alpha)), 4.0))
        p.drawLine(QPointF(x - 14 * s, y_center + half - 14 * s),
                   QPointF(x + 14 * s, y_center + half - 14 * s))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0, int(220 * alpha)))
        p.drawEllipse(QPointF(x, y_center + half + 8 * s), 7 * s, 7 * s)
        p.setBrush(QColor(255, 255, 255, int(210 * alpha)))
        p.drawEllipse(QPointF(x, y_center + half + 8 * s), 5 * s, 5 * s)
        p.setBrush(QColor(255, 255, 255, int(140 * alpha)))
        p.drawEllipse(QPointF(x, y_center - half), 5 * s, 5 * s)

    # --- shared ---------------------------------------------------------

    def _paint_scores(self, p, alpha):
        s = self._s
        pad = int(42.0 * s)
        key_l = ("sc_l", self._player_score)
        key_r = ("sc_r", self._ai_score)
        pl = self._cache.get(key_l)
        if pl is None:
            pl = self._build_score_pixmap(self._player_score)
            self._cache[key_l] = pl
        pr = self._cache.get(key_r)
        if pr is None:
            pr = self._build_score_pixmap(self._ai_score)
            self._cache[key_r] = pr
        p.drawPixmap(QPointF(pad, pad), pl)
        right_x = self._w - pad - pr.width() / self._dpr()
        p.drawPixmap(QPointF(right_x, pad), pr)

    def _paint_flash(self, p):
        s = self._s
        a = min(1.0, self._flash_t / 0.45)
        p.setFont(self._f_head)
        sh = QColor(0, 0, 0, int(180 * a))
        fg = QColor(255, 255, 255, int(230 * a))
        rect = QRectF(0, self._h - 92.0 * s, self._w, 26 * s)
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            p.setPen(QPen(sh, 1.0))
            p.drawText(rect.translated(dx, dy),
                       Qt.AlignmentFlag.AlignCenter, self._flash_text)
        p.setPen(QPen(fg, 1.0))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._flash_text)

    def _paint_banner(self, p):
        p.setFont(self._f_banner)
        rect = QRectF(0, self._h * 0.34, self._w, self._h * 0.16)
        fade_in = min(1.0, (BANNER_S - self._banner_t) / 0.30)
        fade_out = min(1.0, self._banner_t / 0.40)
        a = clamp(min(fade_in, fade_out), 0.0, 1.0)
        sh = QColor(0, 0, 0, int(210 * a))
        fg = QColor(255, 255, 255, int(240 * a))
        for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
            p.setPen(QPen(sh, 1.0))
            p.drawText(rect.translated(dx, dy),
                       Qt.AlignmentFlag.AlignCenter, self._banner_text)
        p.setPen(QPen(fg, 1.0))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._banner_text)


# =========================================================================
# Entry
# =========================================================================

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    SFX.init()

    pong = DeskPong()
    app.installEventFilter(pong)

    pong.show()
    pong.raise_()
    pong._grab_focus_now()

    tray = None
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray = QSystemTrayIcon(make_tray_icon())
        menu = QMenu()
        act_quit = QAction("Quit  (Esc)")
        act_quit.triggered.connect(pong._quit)
        menu.addAction(act_quit)
        tray.setContextMenu(menu)
        tray.setToolTip("Desk Pong")
        tray.show()
        app._tray = tray

    rc = app.exec()
    SFX.shutdown()
    if tray is not None:
        tray.hide()
    return rc


if __name__ == "__main__":
    main()