# Genius — Frontend Design Blueprint
### 🎨 Classroom-Native UI: Full Design Specification & Build Instructions

> **Design DNA:** "A government school classroom brought into the browser — chalk on a slate-green board, worn wood, the smell of chalk dust, a teacher's voice filling the room."

---

## Table of Contents

1. [Design Concept & Philosophy](#1-design-concept--philosophy)
2. [Technology Stack](#2-technology-stack)
3. [Performance: Solving Streamlit Lag](#3-performance-solving-streamlit-lag)
4. [Logo & Brand Assets (Nano Banana Prompts)](#4-logo--brand-assets-nano-banana-prompts)
5. [Design Token System](#5-design-token-system)
6. [Custom Icon System (No Generic Emojis)](#6-custom-icon-system-no-generic-emojis)
7. [Page-by-Page Design Specification](#7-page-by-page-design-specification)
   - [7.1 Landing / Wake Screen](#71-landing--wake-screen)
   - [7.2 Main Teaching Dashboard](#72-main-teaching-dashboard)
   - [7.3 Concept Explanation View](#73-concept-explanation-view)
   - [7.4 Quiz Mode View](#74-quiz-mode-view)
   - [7.5 Session Summary Panel](#75-session-summary-panel)
   - [7.6 Settings / Setup Drawer](#76-settings--setup-drawer)
8. [Left Sidebar — The Wooden Teacher's Rack](#8-left-sidebar--the-wooden-teachers-rack)
9. [Smart Board Display Panel](#9-smart-board-display-panel)
10. [Global Animations & Motion System](#10-global-animations--motion-system)
11. [Chalk Font System](#11-chalk-font-system)
12. [Hot-Reload Dev Setup (No Server Restart)](#12-hot-reload-dev-setup-no-server-restart)
13. [File & Folder Structure](#13-file--folder-structure)
14. [Component Build Order (Implementation Sequence)](#14-component-build-order-implementation-sequence)
15. [Responsive & Smart Board Optimisation](#15-responsive--smart-board-optimisation)
16. [Complete CSS Token Reference](#16-complete-css-token-reference)

---

## 1. Design Concept & Philosophy

### The Core Metaphor

Genius's entire visual identity is **a real Indian government school classroom rendered in the browser**. Not cartoon-ish, not skeuomorphic-ugly — *genuine, affectionate, precise*. Every design decision flows from one question: *"What would this feel like if the classroom was on the screen?"*

### Three Visual Anchors

```
┌────────────────────────────────────────────────────────────────────┐
│  🪵 WOODEN SIDEBAR          🟢 CHALK BOARD             🔆 DUSTY   │
│  ─────────────────          ──────────────             SUNLIGHT   │
│  Brown wood grain           Slate green                            │
│  (left, fixed)              background                Ambient FX  │
│                             White/cream chalk         particle     │
│  Teacher's tools            writing                  system on    │
│  hang here like             Chalk-dust smear          board hover │
│  on a wooden rack           texture overlay                        │
└────────────────────────────────────────────────────────────────────┘
```

### What Makes This Unique vs Generic AI Sites

| Generic AI Tool | Genius |
|---|---|
| White/purple gradient hero | Textured slate-green "board" with chalk marks |
| Inter font, button with rounded corners | Caveat / Patrick Hand (chalk-written feel) |
| Dark sidebar with icons | Wood-grain brown sidebar with SVG "chalk-drawn" labels |
| Blue glowing "Send" button | Chalk circle "tap to speak" button with ring animation |
| Cards with shadows | "Written on the board" panels with chalk-border style |
| Loading spinner | Chalk being drawn animation |
| Generic microphone icon | Custom chalk-sketch mic SVG |

### Signature Element

**The board comes alive when Genius speaks.** During AI response generation, chalk particles drift upward from the writing area — a CSS particle system using tiny `div` elements — while text appears stroke-by-stroke in a chalk-writing animation. This one moment is the thing people will *remember* about Genius.

---

## 2. Technology Stack

### Frontend Layer

```
┌─────────────────────────────────────────────────────────┐
│             GENIUS FRONTEND STACK                     │
│                                                          │
│  Framework : Streamlit 1.41+                             │
│  Hot Reload: Watchdog + Nodemon-equivalent approach      │
│  Custom CSS: st.markdown(unsafe_allow_html=True)         │
│  JS Bridge : st.components.v1.html() for WebRTC/audio   │
│  Fonts     : Google Fonts (Caveat, Kalam, Tiro Devanagari│
│              Rangkap, Literata)                          │
│  Icons     : Custom SVG icon set (chalk-sketch style)    │
│  Animation : CSS keyframes + JS IntersectionObserver    │
│  3D/Visual : Three.js (loaded in st.components.v1.html) │
│  Charts    : Plotly via st.plotly_chart                  │
│  Assets    : Nano Banana generated PNGs + CSS gradients  │
└─────────────────────────────────────────────────────────┘
```

### Why Streamlit + Custom HTML/CSS (not switching to FastAPI/React)

The hackathon brief specifies *"simple web interface (Streamlit, Gradio)"*. We stay on Streamlit but **treat it as a shell** — injecting complete, hand-crafted CSS and HTML through:
- `st.markdown(css, unsafe_allow_html=True)` — global styles
- `st.components.v1.html(html, height=N)` — rich interactive panels (Three.js viewer, audio UI)
- `st.empty()` + container tricks — dynamic content without full reruns

This gives us 95% of what a pure React app would give visually, without violating the brief.

---

## 3. Performance: Solving Streamlit Lag

Streamlit's main performance killer: **whole-script reruns on any widget interaction**.

### Solutions Implemented

#### 3.1 Session State Caching Architecture

```python
# genius/state.py
import streamlit as st
from functools import lru_cache

def init_state():
    """Call once at top of every page. All mutable state lives here."""
    defaults = {
        "current_mode": "idle",        # idle | explaining | quizzing | summary
        "session_topic": None,
        "quiz_scores": [],
        "transcript": [],
        "audio_ready": False,
        "tts_cache": {},               # topic_key → base64 audio
        "viz_cache": {},               # topic_key → html snippet
        "adaptive_profile": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

@st.cache_resource                     # persists across reruns, shared between sessions
def load_rag_engine():
    from genius.rag import build_engine
    return build_engine()

@st.cache_data(ttl=3600)              # cache per-topic content for 1 hour
def get_concept_explanation(topic: str, grade: str, lang: str):
    engine = load_rag_engine()
    return engine.explain(topic, grade, lang)
```

#### 3.2 Hot Reload Without Restarting the Server

**Method: `watchdog` + Streamlit's built-in `--server.runOnSave=true`**

```bash
# Install
pip install watchdog

# Start dev server with hot reload
streamlit run app.py \
  --server.runOnSave=true \
  --server.fileWatcherType=watchdog \
  --server.headless=false \
  --browser.gatherUsageStats=false
```

For the CSS/HTML files (which Streamlit doesn't auto-watch), use a **separate file watcher** that touches `app.py` on any `.css` or `.html` change:

```python
# devwatch.py — run alongside streamlit in a second terminal
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TouchHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if any(event.src_path.endswith(ext) for ext in ['.css', '.html', '.js']):
            Path('app.py').touch()  # triggers Streamlit hot reload
            print(f"↻ Reloading → {event.src_path}")

observer = Observer()
observer.schedule(TouchHandler(), path='genius/', recursive=True)
observer.start()
print("🔍 Watching for CSS/HTML/JS changes...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
```

**Start with:**
```bash
# Terminal 1
streamlit run app.py --server.runOnSave=true --server.fileWatcherType=watchdog

# Terminal 2
python devwatch.py
```

#### 3.3 Disable Unnecessary Reruns

```python
# At top of app.py
st.set_page_config(
    page_title="Genius",
    page_icon="🎓",          # replaced by actual favicon PNG
    layout="wide",
    initial_sidebar_state="collapsed",   # we build our own sidebar
)

# Fragment decorator (Streamlit 1.37+) — reruns ONLY this fragment, not the whole script
@st.fragment
def quiz_scoreboard():
    """This updates live without triggering a full-page rerun."""
    scores = st.session_state.quiz_scores
    # render scoreboard

@st.fragment(run_every=2)             # auto-refresh TTS status every 2s
def audio_status_indicator():
    if st.session_state.audio_ready:
        st.markdown('<div class="audio-ready-pulse"></div>', unsafe_allow_html=True)
```

#### 3.4 Pre-render Static HTML Panels

All "board panels" that don't change often are pre-rendered into `st.session_state` as HTML strings and written with a single `st.markdown()` call — no re-rendering on widget interaction:

```python
if "board_html" not in st.session_state or force_refresh:
    st.session_state["board_html"] = render_board_panel(topic, explanation)

st.markdown(st.session_state["board_html"], unsafe_allow_html=True)
```

---

## 4. Logo & Brand Assets (Nano Banana Prompts)

### 4.1 What is Nano Banana?

**Nano Banana** is Google's AI image generator powered by **Gemini 2.5 Flash Image** (model: `gemini-2.5-flash-image` via Gemini API, also accessible free at Google AI Studio). Use these prompts to generate assets — the user generates them and drops PNGs into `genius/static/assets/`.

### 4.2 Logo — "G" Lettermark

**Use this prompt in Google AI Studio (select Nano Banana / Gemini Image):**

```
Prompt:
A stylish single letter "G" logo icon, chalk-art style on a dark forest-green slate background.
The letter G is hand-drawn in thick white chalk strokes, slightly rough texture as if drawn on a real blackboard.
The "G" has a subtle curve, almost calligraphic — not typeface rigid.
Around the G, a faint halo of chalk dust in soft white.
The letter has a small teacher's pointer icon incorporated subtly at the bottom right of the G, like a tiny diagonal line — a nod to classroom teaching.
Clean circular composition. No background beyond the slate green square.
No watermarks, no text other than the G. Output as a square icon, flat art, minimal, professional.
Style: Indian classroom blackboard aesthetic, chalk illustration.
```

**Output:** Save as `genius/static/assets/logo_G.png` (1024×1024 PNG)

### 4.3 Sidebar Background Texture

```
Prompt:
A seamless tileable wooden plank texture. 
The wood is warm medium brown, like aged teak or classroom furniture — Bharat-style school wood.
Grain lines run vertically. The texture has subtle scratches, chalk dust caught in the grain, minor dents.
Very realistic, physical texture. No cartoon. Flat top-lit lighting.
The color is warm brown #8B5E3C range. Seamless horizontal tile.
1024x1024 px. No people, no furniture, just the raw wood surface texture.
```

**Output:** Save as `genius/static/assets/wood_sidebar.jpg` (set to tile in CSS)

### 4.4 Chalk Dust Overlay / Board Texture

```
Prompt:
A dark slate-green chalkboard surface texture, seamlessly tileable.
Color: deep muted green, similar to #2D5016 to #3A6B1A range.
Surface has fine chalk dust smears, occasional faint white streaks from wiping,
small chalk residue patches, subtle imperfections like tiny pits and scratches.
Realistic school blackboard texture, NOT cartoon. Very subtle, doesn't dominate.
The texture should feel like a board that's been used for a semester.
1024×1024 px. Seamlessly tileable. No text, no symbols.
```

**Output:** Save as `genius/static/assets/board_texture.jpg`

### 4.5 Chalk-Written Decorative Elements (set of 3)

```
Prompt 1 — Decorative border corners:
Hand-drawn chalk corner ornaments, white on transparent background.
Four corner designs: simple scrollwork, a small star, a tiny atom, and a leaf.
Chalk texture, slightly rough strokes. Loose, hand-drawn feeling.
For a classroom blackboard. PNG with transparent background. 4 corners arranged in a 2x2 grid.

Prompt 2 — "Speak to Genius" circular badge:
A circular chalk-drawn badge on transparent background.
Outer circle in rough chalk white strokes, like drawn freehand with chalk.
Inside the circle, a microphone shape made of simple chalk strokes.
Below the mic, three small vertical bars (sound waves) in chalk.
Simple, iconic, hand-drawn feel. White chalk strokes, transparent background.
200×200 px. No text.

Prompt 3 — Subject icons set (6 icons):
Six educational subject icons, all in chalk-sketch style, white on transparent background.
Row 1: Atom (physics), Flask/beaker (chemistry), DNA helix (biology)
Row 2: Book (general), Calculator (maths), Globe (social studies)
Each icon roughly 150×150 px. Loose chalk-drawing style.
White chalk strokes, slightly rough texture. Transparent background. 3x2 grid layout.
```

**Outputs:** Save in `genius/static/assets/icons/`

### 4.6 Genius Mascot — "Guru Ji" (Optional Enhancement)

```
Prompt:
A simple, friendly chalk-drawn avatar icon for an AI teacher named "Genius".
A stylized face with round glasses, simple smile, and a teacher's graduation cap.
Chalk-sketch style, white strokes on transparent/dark background.
Cartoon but not childish — professional teacher aesthetic.
Think "wise owl with glasses" energy but as a human face.
Very minimal strokes, iconic style. No body, just the head/face, roughly circular composition.
150×150 px. White chalk on transparent background.
```

**Output:** `genius/static/assets/gurujii_avatar.png`

---

## 5. Design Token System

All colors, fonts, and spacing are defined in a single CSS block injected at app startup:

```css
/* genius/static/css/tokens.css — loaded via st.markdown() */
:root {
  /* ── BOARD (Main Content) ─────────────── */
  --board-green:      #2A5C1B;   /* deep slate green — main bg */
  --board-green-mid:  #3A7A25;   /* lighter green for panels */
  --board-green-edge: #1E4412;   /* darker edges/borders */
  --chalk-white:      #F5F2E8;   /* primary text on board */
  --chalk-cream:      #EDE8D6;   /* slightly warmer chalk */
  --chalk-yellow:     #F5E642;   /* highlight chalk — "key term" */
  --chalk-pink:       #F5A0A0;   /* error/incorrect highlight */
  --chalk-blue:       #9BCAE8;   /* secondary chalk colour */
  --chalk-orange:     #F5B842;   /* accent / score badges */
  --chalk-dust:       rgba(245,242,232,0.04); /* dust overlay */

  /* ── WOOD SIDEBAR ─────────────────────── */
  --wood-base:        #6B4226;   /* main sidebar brown */
  --wood-dark:        #4A2D18;   /* darker wood grain depth */
  --wood-light:       #8B5E3C;   /* lighter grain highlights */
  --wood-trim:        #3D2010;   /* sidebar border / edge */
  --wood-text:        #F5E6C8;   /* labels on wood */
  --wood-icon:        #D4A96A;   /* icons on wood */

  /* ── ACCENTS ──────────────────────────── */
  --speak-red:        #E8504A;   /* mic button active state */
  --speak-idle:       #C8A96A;   /* mic button idle — golden */
  --quiz-green:       #5FCB6A;   /* correct answer glow */
  --quiz-red:         #E85F5F;   /* wrong answer */
  --score-gold:       #F5C842;   /* score / timer */

  /* ── TYPOGRAPHY ───────────────────────── */
  --font-chalk:       'Caveat', 'Kalam', cursive;            /* chalk writing */
  --font-chalk-alt:   'Patrick Hand', 'Kalam', cursive;       /* UI labels */
  --font-hindi:       'Tiro Devanagari Hindi', serif;          /* Hindi text */
  --font-english:     'Literata', Georgia, serif;              /* explained content */
  --font-ui:          'Outfit', system-ui, sans-serif;         /* system UI only */

  /* ── SCALE ─────────────────────────────── */
  --fs-board-xl:   2.8rem;    /* big board text — topic titles */
  --fs-board-lg:   1.8rem;    /* section headings */
  --fs-board-md:   1.2rem;    /* body explanation text */
  --fs-board-sm:   0.95rem;   /* labels and captions */
  --fs-sidebar:    0.85rem;   /* sidebar labels */

  /* ── SPACING ─────────────────────────────── */
  --sidebar-width:    260px;
  --board-padding:    2rem;
  --chalk-radius:     4px;    /* everything on a board is barely rounded */

  /* ── SHADOWS / DEPTH ─────────────────── */
  --chalk-glow:  0 0 12px rgba(245,242,232,0.15);
  --wood-shadow: inset -4px 0 12px rgba(0,0,0,0.4);
}
```

---

## 6. Custom Icon System (No Generic Emojis)

All icons are custom chalk-sketch SVGs — no emoji, no Font Awesome, no Material Icons.

### Icon Philosophy

Every icon looks like a teacher drew it on the board in 3 seconds — clean intention, slightly imperfect stroke, unmistakably purposeful.

### Icon Set Specification

Each icon is an inline SVG using `stroke="var(--chalk-white)"` or `stroke="var(--wood-icon)"`:

```
genius/static/icons/
├── ic_microphone.svg       ← Voice record / "bolo"
├── ic_board_write.svg      ← Explanation mode
├── ic_quiz_bell.svg        ← Quiz mode
├── ic_book_open.svg        ← NCERT source reference
├── ic_atom.svg             ← Physics/Science subject
├── ic_flask.svg            ← Chemistry subject
├── ic_dna.svg              ← Biology subject
├── ic_calculator.svg       ← Maths subject
├── ic_globe.svg            ← Social Studies subject
├── ic_timer.svg            ← Quiz countdown
├── ic_star_score.svg       ← Score/Achievement
├── ic_settings_gear.svg    ← Settings
├── ic_history_scroll.svg   ← Session history
├── ic_speaker_wave.svg     ← TTS speaking state
├── ic_eraser.svg           ← Clear / reset
├── ic_chalk_pointer.svg    ← "Currently explaining" cursor
└── ic_class_bell.svg       ← Session start/end
```

### Sample SVG Icon (Microphone — chalk-sketch style)

```svg
<!-- ic_microphone.svg -->
<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none">
  <!-- Mic body — slightly imperfect rectangle with rounded top -->
  <path d="M11 6 Q11 3 16 3 Q21 3 21 6 L21 16 Q21 20 16 20 Q11 20 11 16 Z"
        stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"
        fill="none" opacity="0.95"/>
  <!-- Mic stand curve -->
  <path d="M8 16 Q8 24 16 24 Q24 24 24 16"
        stroke="currentColor" stroke-width="1.8" stroke-linecap="round" fill="none" opacity="0.9"/>
  <!-- Stand pole -->
  <line x1="16" y1="24" x2="16" y2="29" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
  <!-- Base -->
  <line x1="12" y1="29" x2="20" y2="29" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
  <!-- Subtle chalk-dust marks (tiny dashes) -->
  <line x1="13" y1="10" x2="14.5" y2="10" stroke="currentColor" stroke-width="0.8" opacity="0.4"/>
  <line x1="13" y1="13" x2="14" y2="13" stroke="currentColor" stroke-width="0.8" opacity="0.3"/>
</svg>
```

### How to Load Icons in Streamlit

```python
# genius/ui/icons.py
from pathlib import Path

ICON_DIR = Path("genius/static/icons")

def icon(name: str, size: int = 24, color: str = "var(--chalk-white)") -> str:
    """Returns inline SVG HTML string for the given icon name."""
    svg_path = ICON_DIR / f"ic_{name}.svg"
    if not svg_path.exists():
        return f'<span style="width:{size}px;height:{size}px;display:inline-block"></span>'
    content = svg_path.read_text()
    # Inject size and color
    content = content.replace('width="32"', f'width="{size}"')
    content = content.replace('height="32"', f'height="{size}"')
    content = content.replace('stroke="currentColor"', f'stroke="{color}"')
    return content

# Usage in Streamlit:
# st.markdown(icon("microphone", size=32) + "<span>Bolo</span>", unsafe_allow_html=True)
```

---

## 7. Page-by-Page Design Specification

---

### 7.1 Landing / Wake Screen

**Purpose:** The very first screen — loads when Genius opens. Teacher sees this before speaking. Should be immersive and immediately tell them what this is.

**URL/Route:** `app.py` → mode=`idle`

#### Layout ASCII Wireframe

```
┌─────────────────────────────────────────────────────────┐
│                   [BOARD TEXTURE BG]                     │
│                                                          │
│          ·  ·  ·  (floating chalk dust particles)  ·    │
│                                                          │
│              ╔═══════════════════════════╗               │
│              ║   [G logo — chalk-drawn]  ║               │
│              ║        Genius          ║               │
│              ║   वाणी गुरु               ║               │
│              ╚═══════════════════════════╝               │
│                                                          │
│         "Apni class mein ek digital saathi"              │
│        "अपनी क्लास में एक डिजिटल साथी"                   │
│                                                          │
│    ┌──────────────────────────────────────────┐          │
│    │    [ 🎤 MIC ICON ]  "Bolo, class shuru   │          │
│    │         karo..."                         │          │
│    │     [  TAP & HOLD TO SPEAK  ]            │          │
│    └──────────────────────────────────────────┘          │
│                                                          │
│   OR TYPE A COMMAND:  [________________] [→]             │
│                                                          │
│   Class: [9th ▾]    Subject: [Science ▾]   Language: [Hi/En ▾]
│                                                          │
│            Powered by AI4Bharat + Groq                   │
└─────────────────────────────────────────────────────────┘
```

#### Features & Interactions

| Element | Behaviour |
|---|---|
| **Chalk dust particles** | 20–30 tiny `div` elements, CSS-animated upward drift, random x-position, 3–8s cycle, `opacity: 0.3–0.6` |
| **Logo "G"** | Fades in on load, subtle chalk-glow pulse every 4s |
| **"Genius" title** | Written using `--font-chalk`, `letter-spacing: 0.05em`, `color: var(--chalk-white)` |
| **Hindi subtitle** | Appears 0.5s after English, `--font-hindi`, slightly smaller |
| **MIC button** | Circular, pulsing chalk-white ring on idle. On press: ring expands + chalk-red fill. On release: ring collapses + audio is sent |
| **Text fallback input** | Standard input but styled as "writing on the board" — `border-bottom: 2px dashed var(--chalk-cream); background: transparent; color: var(--chalk-white)` |
| **Class/Subject dropdowns** | Custom-styled selects with chalk-style appearance |

#### CSS for Landing Screen

```css
/* ── WAKE SCREEN ── */
.wake-screen {
  min-height: 100vh;
  background-image: url('/app/static/assets/board_texture.jpg');
  background-size: 512px 512px;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.wake-screen::before {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(
    135deg,
    rgba(26,48,14,0.6) 0%,
    rgba(42,92,27,0.3) 50%,
    rgba(26,48,14,0.7) 100%
  );
  pointer-events: none;
}

/* Logo */
.vg-logo-ring {
  width: 120px; height: 120px;
  border: 3px solid var(--chalk-cream);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  animation: chalk-glow-pulse 4s ease-in-out infinite;
  margin-bottom: 1.5rem;
}

@keyframes chalk-glow-pulse {
  0%, 100% { box-shadow: 0 0 8px rgba(245,242,232,0.2); }
  50%       { box-shadow: 0 0 24px rgba(245,242,232,0.5), 0 0 48px rgba(245,242,232,0.2); }
}

/* Title */
.vg-title {
  font-family: var(--font-chalk);
  font-size: 3.5rem;
  color: var(--chalk-white);
  text-shadow: 2px 2px 0 rgba(0,0,0,0.3), 0 0 20px rgba(245,242,232,0.1);
  letter-spacing: 0.04em;
  line-height: 1;
  text-align: center;
}
.vg-title-hindi {
  font-family: var(--font-hindi);
  font-size: 1.6rem;
  color: var(--chalk-cream);
  opacity: 0.85;
  text-align: center;
  margin-top: 0.25rem;
}
.vg-tagline {
  font-family: var(--font-chalk-alt);
  font-size: 1.05rem;
  color: var(--chalk-cream);
  opacity: 0.7;
  letter-spacing: 0.02em;
  text-align: center;
  margin: 1rem 0 2rem;
}

/* Mic Button */
.mic-button {
  width: 80px; height: 80px;
  background: transparent;
  border: 3px solid var(--speak-idle);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  position: relative;
  transition: border-color 0.2s;
}
.mic-button::after {
  content: '';
  position: absolute; inset: -8px;
  border: 1.5px solid var(--speak-idle);
  border-radius: 50%;
  opacity: 0.5;
  animation: mic-ring-pulse 2s ease-in-out infinite;
}
.mic-button.recording {
  border-color: var(--speak-red);
  background: rgba(232,80,74,0.12);
  animation: recording-pulse 0.5s ease-in-out infinite alternate;
}
@keyframes mic-ring-pulse {
  0%   { transform: scale(1);   opacity: 0.5; }
  100% { transform: scale(1.2); opacity: 0; }
}
@keyframes recording-pulse {
  from { box-shadow: 0 0 0 0 rgba(232,80,74,0.4); }
  to   { box-shadow: 0 0 0 16px rgba(232,80,74,0); }
}
```

#### Chalk Dust Particle System

```html
<!-- Injected via st.components.v1.html() -->
<div id="chalk-dust-container" aria-hidden="true"></div>
<style>
.chalk-particle {
  position: fixed;
  width: 3px; height: 3px;
  background: rgba(245,242,232,0.5);
  border-radius: 50%;
  pointer-events: none;
  animation: float-up linear infinite;
}
@keyframes float-up {
  0%   { transform: translateY(0) translateX(0); opacity: 0; }
  10%  { opacity: var(--opacity); }
  90%  { opacity: var(--opacity); }
  100% { transform: translateY(-120px) translateX(var(--drift)); opacity: 0; }
}
</style>
<script>
(function() {
  const container = document.getElementById('chalk-dust-container');
  const count = 25;
  for (let i = 0; i < count; i++) {
    const p = document.createElement('div');
    p.className = 'chalk-particle';
    const x = Math.random() * window.innerWidth;
    const y = 100 + Math.random() * (window.innerHeight - 200);
    const dur = 4 + Math.random() * 6;
    const delay = Math.random() * -dur;
    const drift = (Math.random() - 0.5) * 40 + 'px';
    const opacity = 0.2 + Math.random() * 0.4;
    p.style.cssText = `left:${x}px;top:${y}px;animation-duration:${dur}s;animation-delay:${delay}s;
      --opacity:${opacity};--drift:${drift};width:${1+Math.random()*3}px;height:${1+Math.random()*3}px;`;
    container.appendChild(p);
  }
})();
</script>
```

---

### 7.2 Main Teaching Dashboard

**Purpose:** The core working screen — teacher is actively teaching. This is the "classroom live" mode.

**Layout:** 3-column — Wood Sidebar | Board | Info Rail

#### Layout ASCII Wireframe

```
┌──────────┬────────────────────────────────────┬──────────┐
│  WOODEN  │                                    │  CHALK   │
│  SIDEBAR │        🟢 CHALK BOARD              │  RAIL    │
│  260px   │              MAIN                  │  200px   │
│          │                                    │          │
│  [logo]  │  ┌──────────────────────────────┐  │  CLASS:  │
│          │  │  Current Topic:              │  │  9th B   │
│ 📚 Topics│  │  "Photosynthesis"            │  │          │
│ ─────── │  │  ──────────────────          │  │  SUBJECT │
│ SCIENCE  │  │                              │  │  Science │
│ > Physics│  │  [VISUAL PANEL]              │  │          │
│ > Chem   │  │  (3D / diagram / PhET)       │  │  ─────── │
│ > Bio    │  │                              │  │  TIMER   │
│          │  └──────────────────────────────┘  │  [00:24] │
│ 🎯 Modes │  │                              │  │          │
│ ─────── │  │  EXPLANATION TEXT PANEL     │  │  STREAK  │
│ Explain  │  │  ─────────────────────────  │  │   🌟 5   │
│ Quiz     │  │  "Photosynthesis matlab hai │  │          │
│ Dictate  │  │   plants ka apna khana      │  │  RECENT  │
│          │  │   banane ka process..."     │  │  ─────── │
│ ⚙ Setup  │  │                              │  │  > Atoms │
│ ─────── │  └──────────────────────────────┘  │  > Speed │
│ History  │                                    │  > Forces│
│          │  ┌──── VOICE COMMAND BAR ───────┐  │          │
│ Class 9B │  │  🎤 [TAP] Bolo kuch bhi...   │  │  BOARD   │
│ 32 stud. │  │  or type: [____________] →   │  │  MODE:   │
│          │  └──────────────────────────────┘  │  EXPLAIN │
└──────────┴────────────────────────────────────┴──────────┘
```

#### Features Checklist

- [ ] **Wood sidebar** — fixed left, wood-grain texture, never scrolls
- [ ] **Chalk board area** — scrollable, green background, always the widest column
- [ ] **Info rail** — right side, shows class meta + quick stats
- [ ] **Voice command bar** — fixed bottom of board area, always visible
- [ ] **Live "writing" animation** — text appears stroke-by-stroke when AI is responding
- [ ] **Mode indicator** — top of board shows current mode (Explain / Quiz / Idle) in chalk label style
- [ ] **Keyboard shortcut hints** — bottom of sidebar in small chalk text: "Ctrl+M = Mic, Ctrl+Q = Quiz"

---

### 7.3 Concept Explanation View

**Purpose:** Genius is actively explaining a concept. The board is "writing itself."

**Triggered by:** Teacher says "Photosynthesis samjhao" or similar command

#### Layout

```
┌──────────┬────────────────────────────────────────────────┐
│  SIDEBAR │                                                 │
│          │  ┌── TOPIC HEADER ──────────────────────────┐   │
│ [current │  │   PHOTOSYNTHESIS    [page ref: NCERT 10] │   │
│ topic    │  │   प्रकाश संश्लेषण                          │   │
│ highlight│  └─────────────────────────────────────────┘   │
│ in chalk │                                                 │
│ yellow]  │  ┌── VISUAL PANEL ──────────────────────────┐   │
│          │  │                                           │   │
│          │  │   [PhET SIM / THREE.JS / MANIM VIDEO]    │   │
│          │  │        (300–400px height)                 │   │
│          │  │                                           │   │
│ QUICK    │  └─────────────────────────────────────────┘   │
│ CONCEPTS │                                                 │
│ ─────── │  ┌── EXPLANATION PANEL ─────────────────────┐   │
│ [recent  │  │  Chalk handwriting animation:            │   │
│ topics   │  │                                           │   │
│ listed   │  │  "Dekho class, plants khud apna khaana   │   │
│ as chalk │  │   banate hain. Isme 3 cheezein chahiye:  │   │
│ written  │  │   ☀ Suraj ki roshni (sunlight)           │   │
│ list]    │  │   💧 Paani (H₂O)                         │   │
│          │  │   🌬 Carbon Dioxide (CO₂)"               │   │
│          │  │                                           │   │
│          │  │  [HINDI VERSION TOGGLE ⇄]                │   │
│          │  │                                           │   │
│          │  │  KEY TERMS BOX: ═══════════════          │   │
│          │  │  [Chlorophyll] [Glucose] [Sunlight]      │   │
│          │  └─────────────────────────────────────────┘   │
│          │                                                 │
│          │  ┌── ACTION BAR ────────────────────────────┐   │
│          │  │  [🎤 More details]  [Quiz lo]  [Next →]  │   │
│          │  └─────────────────────────────────────────┘   │
└──────────┴────────────────────────────────────────────────┘
```

#### Chalk Writing Animation

The most important visual in the entire app. Text appears as if being written in real time:

```css
/* Writing animation — each character appears with a slight delay */
.chalk-write {
  overflow: hidden;
  white-space: pre-wrap;
  font-family: var(--font-chalk);
  font-size: var(--fs-board-md);
  color: var(--chalk-white);
  line-height: 1.8;
}

/* Applied per-word via JS — each word gets class with index delay */
.chalk-word {
  display: inline-block;
  opacity: 0;
  animation: chalk-appear 0.15s forwards;
}

@keyframes chalk-appear {
  from {
    opacity: 0;
    filter: blur(2px);
    transform: translateY(2px);
  }
  to {
    opacity: 1;
    filter: blur(0);
    transform: translateY(0);
  }
}
```

```javascript
// Chalk word-by-word animation
function animateChalkText(containerEl, text, wordsPerSecond = 4) {
  const words = text.split(' ');
  containerEl.innerHTML = '';
  words.forEach((word, i) => {
    const span = document.createElement('span');
    span.className = 'chalk-word';
    span.textContent = word + ' ';
    span.style.animationDelay = `${i / wordsPerSecond}s`;
    containerEl.appendChild(span);
  });
}
```

#### Key Terms Display

```css
.key-terms-box {
  border: 2px solid var(--chalk-yellow);
  border-style: solid;
  padding: 0.75rem 1rem;
  margin-top: 1.5rem;
  position: relative;
  background: rgba(245,230,66,0.06);
}
.key-terms-box::before {
  content: 'Key Terms';
  font-family: var(--font-chalk);
  font-size: 0.85rem;
  color: var(--chalk-yellow);
  position: absolute;
  top: -0.6em;
  left: 1rem;
  background: var(--board-green);
  padding: 0 0.5rem;
  letter-spacing: 0.05em;
}
.key-term-chip {
  display: inline-block;
  border: 1.5px solid var(--chalk-yellow);
  color: var(--chalk-yellow);
  font-family: var(--font-chalk-alt);
  font-size: 0.9rem;
  padding: 2px 10px;
  margin: 4px;
  border-radius: 2px;
  cursor: pointer;
  transition: background 0.15s;
}
.key-term-chip:hover {
  background: rgba(245,230,66,0.15);
}
```

#### NCERT Source Badge

```css
.ncert-badge {
  font-family: var(--font-chalk-alt);
  font-size: 0.75rem;
  color: var(--chalk-blue);
  border: 1px solid var(--chalk-blue);
  padding: 2px 8px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  opacity: 0.8;
}
```

---

### 7.4 Quiz Mode View

**Purpose:** Voice-triggered quiz display. Teacher says "Ab quiz lo" → this view activates.

**Key experience:** The board clears with an "erasing" animation, then quiz content appears chalk-written.

#### Layout

```
┌──────────┬──────────────────────────────────────────────────┐
│  SIDEBAR │  ┌── QUIZ HEADER ─────────────────────────────┐   │
│          │  │  ❓ QUIZ TIME!   ━━━━━━━━━ [TIMER: 0:30]  │   │
│ SCORES   │  │  Photosynthesis pe 5 sawaal                 │   │
│ ─────── │  └─────────────────────────────────────────────┘  │
│          │                                                    │
│  Class   │  ┌── QUESTION BOARD ──────────────────────────┐   │
│  Score:  │  │                                             │   │
│  72%     │  │   Q1. Photosynthesis mein kya banta hai?   │   │
│          │  │                                             │   │
│  TOP:    │  │   ┌─────────┐  ┌─────────┐                 │   │
│  8/10    │  │   │ A. CO₂  │  │ B. O₂   │                 │   │
│          │  │   └─────────┘  └─────────┘                 │   │
│  WRONG:  │  │   ┌─────────┐  ┌─────────┐                 │   │
│  CO₂     │  │   │C. Glucose│ │D. Water  │                 │   │
│          │  │   └─────────┘  └─────────┘                 │   │
│ REVEAL   │  │                                             │   │
│ ANSWER:  │  │  Teacher reveals: [A] [B] [C] [D]          │   │
│ [VOICE   │  │                                             │   │
│  CMD]    │  │  [Say "Jawab A hai" or click]               │   │
│          │  └─────────────────────────────────────────────┘  │
│          │                                                    │
│          │  ┌── LIVE SCOREBOARD ─────────────────────────┐   │
│          │  │  Correct: ██████████░░  68%                 │   │
│          │  │  Wrong:   ███░░░░░░░░  22%                  │   │
│          │  │  Blank:   ██░░░░░░░░░  10%                  │   │
│          │  └─────────────────────────────────────────────┘  │
│          │                                                    │
│          │  [🎤 Next question]   [See explanation]   [End]   │
└──────────┴──────────────────────────────────────────────────┘
```

#### Quiz Card CSS

```css
.quiz-option-card {
  border: 2px solid var(--chalk-cream);
  background: transparent;
  padding: 1rem 1.25rem;
  cursor: pointer;
  font-family: var(--font-chalk);
  font-size: var(--fs-board-md);
  color: var(--chalk-white);
  transition: background 0.2s, border-color 0.2s;
  position: relative;
  min-width: 140px;
}

/* Option label (A, B, C, D) in corner */
.quiz-option-card::before {
  content: attr(data-label);
  font-family: var(--font-chalk);
  font-size: 0.75rem;
  color: var(--chalk-cream);
  opacity: 0.6;
  position: absolute;
  top: 4px; left: 8px;
}

.quiz-option-card:hover {
  background: rgba(245,242,232,0.08);
  border-color: var(--chalk-white);
}

.quiz-option-card.correct {
  border-color: var(--quiz-green);
  background: rgba(95,203,106,0.12);
  animation: correct-glow 0.4s ease;
}

.quiz-option-card.wrong {
  border-color: var(--quiz-red);
  background: rgba(232,95,95,0.1);
  animation: wrong-shake 0.3s ease;
}

@keyframes correct-glow {
  0%   { box-shadow: 0 0 0 0 rgba(95,203,106,0.6); }
  50%  { box-shadow: 0 0 0 16px rgba(95,203,106,0); }
  100% { box-shadow: none; }
}

@keyframes wrong-shake {
  0%,100% { transform: translateX(0); }
  25%      { transform: translateX(-6px); }
  75%      { transform: translateX(6px); }
}
```

#### Board Erase Transition (Quiz → Explain and vice versa)

```css
/* Board wipe: left-to-right white streak then new content */
.board-erase {
  animation: board-wipe 0.6s ease-in-out;
}

@keyframes board-wipe {
  0%   { opacity: 1; filter: none; }
  30%  { opacity: 0.6; filter: blur(1px) brightness(1.3); }
  60%  { opacity: 0.2; filter: blur(3px) brightness(1.6); }
  100% { opacity: 0; }
}

.board-appear {
  animation: board-chalk-in 0.8s ease-out;
}

@keyframes board-chalk-in {
  0%   { opacity: 0; filter: blur(4px); }
  100% { opacity: 1; filter: none; }
}
```

#### Quiz Score Progress Bar

```css
.quiz-bar-track {
  height: 12px;
  background: rgba(245,242,232,0.1);
  border: 1px solid rgba(245,242,232,0.2);
  border-radius: 2px;
  overflow: hidden;
}

.quiz-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.quiz-bar-fill.correct { background: var(--quiz-green); }
.quiz-bar-fill.wrong   { background: var(--quiz-red); }
.quiz-bar-fill.blank   { background: var(--chalk-cream); opacity: 0.3; }

.quiz-timer {
  font-family: var(--font-chalk);
  font-size: 2rem;
  color: var(--score-gold);
  text-shadow: 0 0 10px rgba(245,200,66,0.4);
}
.quiz-timer.urgent {
  color: var(--quiz-red);
  animation: timer-urgent-pulse 0.5s ease-in-out infinite alternate;
}
@keyframes timer-urgent-pulse {
  from { opacity: 1; text-shadow: 0 0 4px rgba(232,95,95,0.3); }
  to   { opacity: 0.7; text-shadow: 0 0 16px rgba(232,95,95,0.6); }
}
```

---

### 7.5 Session Summary Panel

**Purpose:** End of class / on demand — shows what was covered, quiz results, topics for next time.

**Triggered by:** "Class khatam karo" or sidebar "Summary" button

#### Layout

```
┌──────────┬────────────────────────────────────────────────────┐
│  SIDEBAR │  ┌── SESSION SUMMARY ─────────────────────────┐    │
│          │  │                                              │    │
│          │  │   📋 Aaj ki class — 27 Jan                  │    │
│          │  │   Class 9-B  |  Science  |  45 min          │    │
│          │  │                                              │    │
│          │  │   TOPICS COVERED  ════════════════          │    │
│          │  │   ✓  Photosynthesis                          │    │
│          │  │   ✓  Chlorophyll                             │    │
│          │  │   ✓  Light Reactions                         │    │
│          │  │   ✗  Dark Reactions (skipped)                │    │
│          │  │                                              │    │
│          │  │   QUIZ RESULTS  ═══════════════════          │    │
│          │  │   5 questions | Score: 72%                   │    │
│          │  │   Weak area: CO₂ absorption                  │    │
│          │  │   Strong: Glucose synthesis                  │    │
│          │  │                                              │    │
│          │  │   NEXT CLASS SUGGESTIONS ════════════        │    │
│          │  │   → Dark Reactions (continue)                │    │
│          │  │   → ATP production                           │    │
│          │  │   → Revise: CO₂ role (class struggled)       │    │
│          │  │                                              │    │
│          │  │   [📥 Download PDF]  [🔄 New Session]       │    │
│          │  └──────────────────────────────────────────────┘   │
└──────────┴────────────────────────────────────────────────────┘
```

---

### 7.6 Settings / Setup Drawer

**Purpose:** Teacher configures Genius once — class, subject, language, voice, difficulty level.

**Triggered by:** Sidebar "Setup" icon

#### Layout

```
┌──────────┬────────────────────────────────────────────────────┐
│  SIDEBAR │  ┌── SETTINGS DRAWER ─────────────────────────┐    │
│          │  │   ⚙  Genius Setup                        │    │
│          │  │   ──────────────────────────                │    │
│          │  │                                              │    │
│          │  │   CLASS          [9th  ▾]                    │    │
│          │  │   SUBJECT        [Science ▾]                 │    │
│          │  │   MEDIUM/LANG    [Hinglish ▾]                │    │
│          │  │   STUDENT COUNT  [32]                        │    │
│          │  │   SCHOOL NAME    [Govt Sr Sec School...]     │    │
│          │  │                                              │    │
│          │  │   VOICE SETTINGS ════════════════            │    │
│          │  │   AI Voice: [Priya — Female ▾]              │    │
│          │  │   Speed:    [●●○○○] Normal                   │    │
│          │  │   Volume:   [●●●○○]                          │    │
│          │  │                                              │    │
│          │  │   AI SETTINGS ═══════════════════            │    │
│          │  │   Detail Level: [Simple ● Medium ○ Deep ○]  │    │
│          │  │   Quiz Difficulty: [Easy ○ Medium ● Hard ○] │    │
│          │  │   NCERT Edition: [2024 ▾]                    │    │
│          │  │                                              │    │
│          │  │   [Save & Start Class]                       │    │
│          │  └──────────────────────────────────────────────┘   │
└──────────┴────────────────────────────────────────────────────┘
```

---

## 8. Left Sidebar — The Wooden Teacher's Rack

The sidebar is the soul of the classroom aesthetic. It must feel like the wooden rack/shelf/cabinet at the front of a classroom.

### Visual Properties

```css
/* genius/static/css/sidebar.css */
.sidebar {
  width: var(--sidebar-width);
  min-height: 100vh;
  position: fixed;
  left: 0; top: 0;
  background-image: url('/app/static/assets/wood_sidebar.jpg');
  background-size: 260px auto;
  box-shadow: var(--wood-shadow), 4px 0 20px rgba(0,0,0,0.4);
  border-right: 3px solid var(--wood-trim);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  z-index: 100;
}

/* Wood grain overlay for realism */
.sidebar::after {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(
    180deg,
    rgba(74,45,24,0.3) 0%,
    rgba(107,66,38,0.1) 40%,
    rgba(74,45,24,0.3) 100%
  );
  pointer-events: none;
}

/* Logo area at top */
.sidebar-logo {
  padding: 1.25rem 1rem;
  border-bottom: 1px solid rgba(212,169,106,0.2);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.sidebar-logo img {
  width: 36px; height: 36px;
  border-radius: 50%;
}
.sidebar-logo-text {
  font-family: var(--font-chalk);
  font-size: 1.3rem;
  color: var(--wood-text);
  letter-spacing: 0.03em;
}

/* Section labels — chalk-written look on wood */
.sidebar-section-label {
  font-family: var(--font-chalk-alt);
  font-size: 0.7rem;
  color: var(--wood-icon);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 0.75rem 1rem 0.25rem;
  opacity: 0.75;
}

/* Nav items */
.sidebar-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-family: var(--font-chalk-alt);
  font-size: 0.9rem;
  color: var(--wood-text);
  transition: background 0.15s;
  border-radius: 2px;
  margin: 1px 4px;
}
.sidebar-item:hover {
  background: rgba(212,169,106,0.12);
}
.sidebar-item.active {
  background: rgba(212,169,106,0.2);
  border-left: 3px solid var(--chalk-yellow);
  color: var(--chalk-yellow);
}
.sidebar-item svg {
  opacity: 0.8;
  flex-shrink: 0;
}

/* Class info badge at bottom */
.sidebar-class-info {
  margin-top: auto;
  padding: 0.75rem 1rem;
  border-top: 1px solid rgba(212,169,106,0.15);
  font-family: var(--font-chalk-alt);
  font-size: 0.8rem;
  color: var(--wood-text);
  opacity: 0.7;
}
```

### Sidebar Navigation Items (with custom icons)

| Icon (chalk SVG) | Label | Action |
|---|---|---|
| `ic_board_write.svg` | Explain | Switch to Explain mode |
| `ic_quiz_bell.svg` | Quiz | Trigger quiz mode |
| `ic_book_open.svg` | NCERT | Browse curriculum |
| `ic_history_scroll.svg` | History | View past sessions |
| `ic_settings_gear.svg` | Setup | Open settings drawer |
| `ic_eraser.svg` | Clear Board | Reset current view |

---

## 9. Smart Board Display Panel

The main board area is the canvas. It must feel like a real board that content is being *written onto*.

### Board Panel Structure

```
Board Container
├── Board Header Bar (topic + mode badge + ncert ref)
├── Visual Panel (Three.js / PhET iframe / static diagram)
├── Explanation Panel (chalk-write animated text)
├── Key Terms Box (chalk border, yellow highlight)
└── Action Bar (quick command buttons)
```

### Board CSS

```css
.board-container {
  margin-left: var(--sidebar-width);
  min-height: 100vh;
  background-image: url('/app/static/assets/board_texture.jpg');
  background-size: 512px 512px;
  padding: var(--board-padding);
  position: relative;
}

/* Subtle chalk grid lines — like printed board */
.board-container::before {
  content: '';
  position: fixed;
  inset: 0;
  margin-left: var(--sidebar-width);
  background-image:
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 38px,
      rgba(245,242,232,0.04) 38px,
      rgba(245,242,232,0.04) 39px
    );
  pointer-events: none;
  z-index: 0;
}

/* Visual panel — "a section of the board" */
.board-visual-panel {
  width: 100%;
  min-height: 300px;
  background: rgba(26,48,14,0.5);
  border: 1.5px solid rgba(245,242,232,0.2);
  position: relative;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* Chalk-drawn corner marks on panels */
.board-visual-panel::before,
.board-visual-panel::after {
  content: '';
  position: absolute;
  width: 16px; height: 16px;
  border-color: rgba(245,242,232,0.4);
  border-style: solid;
  border-width: 0;
}
.board-visual-panel::before {
  top: 6px; left: 6px;
  border-top-width: 2px;
  border-left-width: 2px;
}
.board-visual-panel::after {
  bottom: 6px; right: 6px;
  border-bottom-width: 2px;
  border-right-width: 2px;
}
```

---

## 10. Global Animations & Motion System

### Principles

1. **Chalk writes, doesn't type** — text never just appears; it animates in word-by-word or stroke-by-stroke
2. **Board clears before new content** — mode transitions have an erase-then-write sequence
3. **Particles are ambient, not distracting** — chalk dust floats at low opacity always
4. **Voice visualisation** — when mic is active, a waveform or ripple shows on the board
5. **One big animation per interaction** — don't pile effects; choose the one that matters

### Complete Animation Library

```css
/* 1. Page load — board fades in from dark */
@keyframes board-fade-in {
  from { opacity: 0; filter: brightness(0.5); }
  to   { opacity: 1; filter: brightness(1); }
}

/* 2. Chalk writing (word by word) */
@keyframes chalk-word-in {
  from { opacity: 0; filter: blur(1.5px); transform: translateY(3px); }
  to   { opacity: 1; filter: blur(0);     transform: translateY(0); }
}

/* 3. Board erase sweep (left to right) */
@keyframes board-erase-sweep {
  0%   { clip-path: inset(0 100% 0 0); }
  100% { clip-path: inset(0 0% 0 0); }
}

/* 4. Panel slide in from bottom */
@keyframes slide-up {
  from { transform: translateY(20px); opacity: 0; }
  to   { transform: translateY(0);    opacity: 1; }
}

/* 5. Mic recording pulse */
@keyframes mic-pulse {
  0%   { box-shadow: 0 0 0 0   rgba(232,80,74,0.7); }
  70%  { box-shadow: 0 0 0 16px rgba(232,80,74,0); }
  100% { box-shadow: 0 0 0 0   rgba(232,80,74,0); }
}

/* 6. Voice waveform (when TTS is speaking) */
@keyframes wave-bar {
  0%,100% { transform: scaleY(0.3); }
  50%     { transform: scaleY(1); }
}

/* 7. Score celebration */
@keyframes score-pop {
  0%   { transform: scale(0.8); opacity: 0; }
  60%  { transform: scale(1.1); opacity: 1; }
  100% { transform: scale(1);   opacity: 1; }
}

/* 8. Wrong answer shake */
@keyframes shake-wrong {
  0%,100% { transform: translateX(0); }
  20%,60% { transform: translateX(-8px); }
  40%,80% { transform: translateX(8px); }
}

/* 9. Chalk dust float (particles) */
@keyframes dust-float {
  0%   { transform: translateY(0) translateX(0) rotate(0deg);   opacity: 0; }
  10%  { opacity: var(--p-opacity); }
  90%  { opacity: var(--p-opacity); }
  100% { transform: translateY(-80px) translateX(var(--drift)) rotate(360deg); opacity: 0; }
}

/* 10. Timer countdown tick */
@keyframes timer-tick {
  0%   { transform: scale(1); }
  50%  { transform: scale(1.04); }
  100% { transform: scale(1); }
}
```

### Voice Waveform Visualiser

Displayed while TTS is speaking — 5 vertical bars that animate at different speeds:

```html
<div class="voice-wave" aria-label="Speaking...">
  <span class="wave-bar" style="animation-delay:0s"></span>
  <span class="wave-bar" style="animation-delay:0.1s"></span>
  <span class="wave-bar" style="animation-delay:0.2s"></span>
  <span class="wave-bar" style="animation-delay:0.15s"></span>
  <span class="wave-bar" style="animation-delay:0.05s"></span>
</div>

<style>
.voice-wave {
  display: flex; align-items: center; gap: 3px;
  height: 28px;
}
.wave-bar {
  width: 3px;
  height: 100%;
  background: var(--chalk-blue);
  border-radius: 2px;
  animation: wave-bar 0.5s ease-in-out infinite alternate;
  transform-origin: bottom;
}
</style>
```

---

## 11. Chalk Font System

### Fonts to Load

```html
<!-- In the HTML head injected via st.markdown -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;600;700&family=Kalam:wght@300;400;700&family=Patrick+Hand&family=Tiro+Devanagari+Hindi&family=Outfit:wght@300;400;500&family=Literata:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
```

### Font Usage Map

| Font | Variable | Use |
|---|---|---|
| **Caveat** (wt 400–700) | `--font-chalk` | Board headings, topic titles, main chalk text |
| **Kalam** (wt 300–700) | `--font-chalk` (fallback) | Explanation body text on board |
| **Patrick Hand** | `--font-chalk-alt` | UI labels, sidebar items, button text |
| **Tiro Devanagari Hindi** | `--font-hindi` | Hindi/Devanagari text on board |
| **Literata** | `--font-english` | Clean explained content (bilingual mode) |
| **Outfit** | `--font-ui` | Settings, dropdowns, metadata — non-chalk UI only |

### Chalk Text Rendering Tips

```css
/* Make Caveat/Kalam look more chalk-like */
.chalk-text {
  font-family: var(--font-chalk);
  color: var(--chalk-white);
  /* Slight roughness via text-shadow */
  text-shadow:
    0.5px 0.5px 0 rgba(245,242,232,0.3),
    -0.5px -0.5px 0 rgba(245,242,232,0.15);
  /* Prevent crisp rendering */
  -webkit-font-smoothing: subpixel-antialiased;
}

/* Chalk headings — bigger, bolder, slightly uneven */
.chalk-heading {
  font-family: var(--font-chalk);
  font-weight: 700;
  font-size: var(--fs-board-xl);
  color: var(--chalk-white);
  letter-spacing: 0.03em;
  line-height: 1.1;
}

/* Hindi text block */
.hindi-text {
  font-family: var(--font-hindi);
  color: var(--chalk-cream);
  font-size: 1.1em;
  line-height: 1.9;
  opacity: 0.9;
}
```

---

## 12. Hot-Reload Dev Setup (No Server Restart)

### Full Dev Setup Script

Create `start_dev.sh` at project root:

```bash
#!/bin/bash
# Genius Development Startup Script
# Starts Streamlit with hot-reload AND a file watcher for CSS/HTML changes

echo "🎓 Starting Genius Dev Server..."
echo ""

# Kill any existing instances
pkill -f "streamlit run app.py" 2>/dev/null
pkill -f "python devwatch.py"  2>/dev/null
sleep 1

# Start Streamlit with hot reload
streamlit run app.py \
  --server.runOnSave=true \
  --server.fileWatcherType=watchdog \
  --server.port=8501 \
  --server.headless=false \
  --browser.gatherUsageStats=false \
  --theme.base="dark" \
  --theme.backgroundColor="#2A5C1B" \
  --theme.secondaryBackgroundColor="#1E4412" \
  --theme.textColor="#F5F2E8" \
  --theme.primaryColor="#F5C842" &

STREAMLIT_PID=$!
echo "✅ Streamlit started (PID: $STREAMLIT_PID)"

# Start CSS/HTML watcher
python devwatch.py &
WATCHER_PID=$!
echo "✅ File watcher started (PID: $WATCHER_PID)"

echo ""
echo "🌐 Genius → http://localhost:8501"
echo "🔍 Watching: genius/**/*.css, *.html, *.js"
echo ""
echo "Press Ctrl+C to stop all processes"

# Wait for Ctrl+C and clean up
trap "kill $STREAMLIT_PID $WATCHER_PID 2>/dev/null; echo '🛑 Stopped.'" INT
wait
```

```bash
chmod +x start_dev.sh
./start_dev.sh
```

### Streamlit Theme Config

Create `.streamlit/config.toml`:

```toml
[theme]
base = "dark"
backgroundColor          = "#2A5C1B"
secondaryBackgroundColor = "#1E4412"
textColor                = "#F5F2E8"
primaryColor             = "#F5C842"
font                     = "sans serif"

[server]
runOnSave         = true
fileWatcherType   = "watchdog"
port              = 8501
headless          = false
enableCORS        = false
enableXsrfProtection = true
maxUploadSize     = 50

[browser]
gatherUsageStats  = false
serverAddress     = "localhost"

[runner]
fastReruns        = true
magicEnabled      = false
```

---

## 13. File & Folder Structure

```
genius/
│
├── app.py                          # Main Streamlit entry point
├── devwatch.py                     # CSS/HTML hot-reload watcher
├── start_dev.sh                    # Dev startup script
├── requirements.txt                # Python dependencies
│
├── .streamlit/
│   └── config.toml                 # Streamlit theme & server config
│
├── genius/
│   ├── __init__.py
│   ├── state.py                    # Session state management
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── rag.py                  # NCERT RAG engine
│   │   ├── llm.py                  # Groq / LLM integration
│   │   ├── stt.py                  # Whisper / IndicConformer STT
│   │   ├── tts.py                  # edge-tts / Indic-Parler TTS
│   │   └── adaptive.py             # Adaptive learning loop
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── icons.py                # SVG icon loader
│   │   ├── layout.py               # Page layout builder
│   │   ├── sidebar.py              # Sidebar component
│   │   ├── board.py                # Main board component
│   │   ├── quiz.py                 # Quiz mode UI
│   │   ├── summary.py              # Session summary
│   │   ├── settings.py             # Settings drawer
│   │   └── particles.py            # Chalk dust particle system
│   │
│   ├── viz/
│   │   ├── __init__.py
│   │   ├── threejs_renderer.py     # Three.js scene builder
│   │   ├── phet_mapper.py          # PhET simulation selector
│   │   └── diagram_builder.py      # SVG diagram generator
│   │
│   └── data/
│       ├── ncert/                  # NCERT PDFs and indexed chunks
│       ├── topic_phet_map.json     # topic → PhET URL mapping
│       └── session_logs/           # Per-class session logs
│
├── static/
│   ├── css/
│   │   ├── tokens.css              # Design token system
│   │   ├── layout.css              # Overall layout
│   │   ├── sidebar.css             # Wood sidebar
│   │   ├── board.css               # Board/chalk area
│   │   ├── quiz.css                # Quiz components
│   │   ├── animations.css          # All @keyframes
│   │   └── fonts.css               # Font imports + chalk text styles
│   │
│   ├── js/
│   │   ├── chalk_animate.js        # Chalk writing animation
│   │   ├── particles.js            # Chalk dust system
│   │   ├── audio_bridge.js         # WebRTC mic bridge
│   │   └── voice_wave.js           # Speaking waveform
│   │
│   ├── icons/
│   │   ├── ic_microphone.svg
│   │   ├── ic_board_write.svg
│   │   ├── ic_quiz_bell.svg
│   │   └── ... (all 16 icons)
│   │
│   └── assets/
│       ├── logo_G.png              # Generated by Nano Banana
│       ├── wood_sidebar.jpg        # Wood texture (Nano Banana)
│       ├── board_texture.jpg       # Chalk board texture (Nano Banana)
│       ├── gurujii_avatar.png      # Mascot (Nano Banana, optional)
│       └── icons/                  # Subject icons (Nano Banana)
│
└── tests/
    ├── test_rag.py
    ├── test_tts.py
    └── test_ui_render.py
```

---

## 14. Component Build Order (Implementation Sequence)

Build in this exact order to always have a working, demonstrable app:

### Phase 0 — Foundation (Day 1, first 2 hours)
1. `app.py` — bare Streamlit app, page config set
2. `.streamlit/config.toml` — dark green theme
3. `static/css/tokens.css` — all CSS variables
4. `static/css/fonts.css` — font imports
5. `devwatch.py` + `start_dev.sh` — hot reload working
6. Verify: green screen with chalk fonts loads in browser ✅

### Phase 1 — Shell (Day 1, next 4 hours)
7. `ui/sidebar.py` — wood sidebar with icons (mock data)
8. `ui/board.py` — board container with texture
9. `static/css/sidebar.css` + `board.css`
10. `ui/particles.py` — chalk dust floating
11. Verify: classroom look with sidebar and board visible ✅

### Phase 2 — Landing Page (Day 1, last 2 hours)
12. Wake screen with logo, title, mic button
13. Chalk particle animation
14. Class/subject selector dropdowns
15. Verify: landing page looks like a classroom ✅

### Phase 3 — Voice & AI Core (Day 2)
16. `ai/stt.py` — Whisper STT working
17. `ai/tts.py` — edge-tts TTS working
18. `ai/llm.py` — Groq API integration
19. `ai/rag.py` — NCERT index + retrieval
20. Basic text response on board: type question → chalk text appears
21. Verify: full text pipeline works ✅

### Phase 4 — Explanation View (Day 3)
22. Chalk writing animation for responses
23. `viz/phet_mapper.py` — PhET simulation iframe for 10 key topics
24. Key terms box
25. NCERT source badge
26. Hindi/English toggle
27. Verify: ask about Photosynthesis → PhET sim + chalk explanation ✅

### Phase 5 — Quiz Mode (Day 4)
28. `ui/quiz.py` — full quiz UI
29. Board erase → quiz appear transition
30. Answer cards with correct/wrong animation
31. Score progress bars
32. Timer with urgent state
33. Verify: "quiz lo" → quiz appears, answers graded ✅

### Phase 6 — Polish & Summary (Day 5)
34. Session summary view
35. Settings drawer
36. Voice waveform during TTS
37. All 16 SVG icons complete
38. Nano Banana assets dropped in
39. Mobile/smart board responsive CSS
40. Final bug fixes, performance check

---

## 15. Responsive & Smart Board Optimisation

### Smart Board Mode

The smart board is a large screen (typically 65–86 inch, landscape, running a browser at ~1080p or ~1440p). Optimise for this:

```css
/* Smart board specific — activate with ?mode=board URL param */
@media (min-width: 1400px) {
  :root {
    --fs-board-xl:   3.5rem;   /* bigger text, readable from back of class */
    --fs-board-lg:   2.2rem;
    --fs-board-md:   1.4rem;
    --sidebar-width: 280px;
    --board-padding: 2.5rem;
  }

  /* Larger quiz cards for all students to see */
  .quiz-option-card {
    min-height: 80px;
    font-size: 1.3rem;
  }

  /* Bigger voice waveform */
  .voice-wave .wave-bar { width: 5px; }
}

/* Mobile (teacher's phone used as remote) */
@media (max-width: 768px) {
  :root {
    --sidebar-width: 0px;
    --board-padding: 1rem;
    --fs-board-xl:   2rem;
  }

  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s;
  }
  .sidebar.open {
    transform: translateX(0);
  }

  /* Full-width board on mobile */
  .board-container {
    margin-left: 0;
    padding-top: 60px; /* header bar with hamburger */
  }
}
```

### Offline/Low-Bandwidth Fallback

```python
# genius/ui/board.py
import streamlit as st

def render_board_panel(topic, content, viz_type="auto"):
    """
    Render the board. Falls back gracefully:
    Online + fast: Three.js / PhET simulation (iframe)
    Online + slow: Static SVG diagram
    Offline:       Text-only chalk panel
    """
    # Check connectivity flag from session state
    if st.session_state.get("offline_mode", False):
        return render_text_only_panel(topic, content)

    if viz_type == "phet":
        phet_url = get_phet_url(topic)
        if phet_url:
            return render_phet_panel(phet_url)

    if viz_type == "threejs":
        return render_threejs_panel(topic, content)

    return render_svg_diagram_panel(topic, content)
```

---

## 16. Complete CSS Token Reference

Quick-reference card for developers:

```
COLORS
──────
--board-green       #2A5C1B    Main board background
--chalk-white       #F5F2E8    Primary text
--chalk-cream       #EDE8D6    Secondary text
--chalk-yellow      #F5E642    Highlights, key terms
--chalk-pink        #F5A0A0    Errors, warnings
--chalk-blue        #9BCAE8    Secondary accent
--chalk-orange      #F5B842    Badges, scores
--wood-base         #6B4226    Sidebar main brown
--speak-red         #E8504A    Mic active
--speak-idle        #C8A96A    Mic idle
--quiz-green        #5FCB6A    Correct answer
--quiz-red          #E85F5F    Wrong answer
--score-gold        #F5C842    Score display

FONTS
─────
--font-chalk        Caveat, Kalam         Board writing
--font-chalk-alt    Patrick Hand          UI labels
--font-hindi        Tiro Devanagari Hindi Hindi text
--font-english      Literata              Body explanations
--font-ui           Outfit                Settings UI only

SPACING
───────
--sidebar-width     260px
--board-padding     2rem
--chalk-radius      4px

FONT SIZES
──────────
--fs-board-xl       2.8rem    Topic titles
--fs-board-lg       1.8rem    Section headings
--fs-board-md       1.2rem    Body text
--fs-board-sm       0.95rem   Labels
--fs-sidebar        0.85rem   Sidebar items

SHADOWS
───────
--chalk-glow        0 0 12px rgba(245,242,232,0.15)
--wood-shadow       inset -4px 0 12px rgba(0,0,0,0.4)
```

---

## 17. Summary: What You Will Show the Judges

When you demo Genius, the experience flow is:

1. **Open browser → Landing screen** — classroom green board, Genius logo glowing, chalk particles floating. Immediate "oh, this is different."

2. **Say "Photosynthesis samjhao" or type it** — mic button glows red, waveform appears. Board clears with erase animation.

3. **Board comes alive** — chalk text writes itself word-by-word. PhET simulation or Three.js animation fills the visual panel. Key terms appear in yellow chalk box. Hindi toggle works.

4. **Say "Ab quiz lo"** — board wipes clean. Quiz cards appear chalk-drawn. Timer counts down. Teacher says "Jawab C hai" — options glow green/red. Score bar fills.

5. **Session Summary** — "Class khatam karo" → summary panel shows topics covered, quiz score, what to revise next time.

**No generic fonts. No purple gradients. No emoji icons. No white cards on grey backgrounds. Every pixel tells the classroom story.**

---

*Genius Frontend Blueprint v1.0 — Built for India's classrooms.*
