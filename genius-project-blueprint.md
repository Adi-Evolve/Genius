# Genius — Voice-Native AI Teaching Co-Pilot for Indian Government Classrooms
### Project Blueprint, Architecture & Implementation Plan — v1.0

> **वाणी (Vaani)** = voice/speech, **गुरु (Guru)** = teacher. *Tagline: "Bolo, aur class jeevant ho jaaye" — Speak, and the class comes alive.*

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement — Our Reading of the Brief](#2-problem-statement--our-reading-of-the-brief)
3. [Design Philosophy — Non-Negotiables](#3-design-philosophy--non-negotiables)
4. [Research & Inspiration — Competitive Landscape](#4-research--inspiration--competitive-landscape)
5. [System Architecture](#5-system-architecture)
6. [Technology Stack (Free & Open-Source First)](#6-technology-stack-free--open-source-first)
7. [UI/UX Design](#7-uiux-design)
8. [The AI Brain — Pipeline Deep Dive](#8-the-ai-brain--pipeline-deep-dive)
9. [Multi-Modal Visualization Engine](#9-multi-modal-visualization-engine)
10. [Voice-Triggered Quizzing Module](#10-voice-triggered-quizzing-module)
11. [Adaptive Learning & the "Self-Improvement" Loop](#11-adaptive-learning--the-self-improvement-loop)
12. [Deployment Plan — ₹0 Operating Cost](#12-deployment-plan--0-operating-cost)
13. [Implementation Roadmap](#13-implementation-roadmap)
14. [Evaluation & Success Metrics](#14-evaluation--success-metrics)
15. [Risks & Mitigations](#15-risks--mitigations)
16. [Future Scope](#16-future-scope)
17. [References & Further Reading](#17-references--further-reading)

---

## 1. Executive Summary

**Genius** is a hands-free, voice-first AI co-pilot that sits beside a teacher in a Haryana government classroom. The teacher talks to it in natural Hinglish — the way they'd talk to a colleague — and Genius listens, thinks against the actual NCERT syllabus, and instantly projects a spoken explanation **and** a synchronized visual (a diagram, an animation, an interactive 3D model, or a quiz card) onto the smart board. No typing, no clicking, no app-switching mid-lesson.

Out of the four requirement options in the brief, we have built our prototype around **two that form a complete teaching loop**:

- **Live Concept Simplification** — the teacher says *"Photosynthesis samjhao with diagram"* and Genius explains it conversationally in Hinglish while drawing/animating the right visual (2D diagram for processes, 3D/interactive model for chemistry, biology and physics structures).
- **Voice-Triggered Quizzing** — immediately after (or anytime), the teacher says *"Ab quiz lo"* and Genius verbally announces questions, displays answer-choice cards on the board, and keeps a live class scoreboard.

Together these form a **teach → check → adapt** cycle: every quiz result becomes training signal for Genius's adaptive layer, which gradually learns *which explanation style works for which topic in which class* — the "self-learning" capability the brief asks for, implemented honestly as a class-level contextual bandit (Section 11) rather than an overstated black-box claim.

What makes this **not** "another chatbot wrapper":

- **Grounded, not improvised.** Every explanation is retrieved from an indexed NCERT corpus (RAG) before the LLM speaks — Genius can show *which textbook page* an explanation came from.
- **Hinglish-native.** STT, intent-matching and TTS are all built around the way Indian classrooms actually talk — code-switched Hindi/English, not a translated English bot.
- **Multi-modal by construction.** Every response is a single structured object — spoken text *and* a "visual spec" — so the smart board is never just a chat transcript.
- **₹0 to run.** The entire stack runs on free tiers (Groq, edge-tts, AI4Bharat open models, HuggingFace Spaces) with a fully offline (Ollama-based) fallback for low-connectivity schools.
- **Modular and swappable.** STT engine, LLM, TTS voice, and even the visualization renderer are independent, replaceable blocks — so the team can upgrade pieces over time without a rewrite.

The remainder of this document plans every layer of this system in detail: architecture, UI, AI pipeline, the multi-modal (text / 2D / 3D) visualization engine, the quiz module, the adaptive-learning loop, and a phased build roadmap.

---

## 2. Problem Statement — Our Reading of the Brief

### 2.1 Restating the context

A teacher in a Haryana government school has a smart board, a class that speaks Hinglish, and — like most government-school teachers — very little spare time or technical bandwidth. They need an assistant that:

- Responds to **spoken** commands (hands stay free for writing, pointing, managing the class).
- Understands **Hinglish** (not pure Hindi, not pure English).
- **Projects visuals** on the smart board, not just plays audio.
- Runs as a **simple web interface** (Streamlit/Gradio-class simplicity), usable on the smart board's browser or a teacher's phone.

### 2.2 Choosing 2 of the 4 requirements

The brief asks teams to pick 2 of 4 requirements. We evaluated all four against the goals stated elsewhere in the brief — especially the explicit ask for **3D/animated demonstration of complex subjects (Chemistry, Biology, Physics)** and a system that can **self-improve over time**:

| Requirement | Pedagogical value | Visual-richness potential | Synergy with the "3D demo for complex subjects" goal | Decision |
|---|---|---|---|---|
| **Live Concept Simplification** | Very high — this *is* "teaching." Covers the daily "samjhao na" moment for any topic. | Very high — every concept can carry a diagram, animation, or 3D model. | **Direct match.** This requirement *is* the 3D/animation requirement in disguise. | ✅ **Chosen — Primary** |
| **Voice-Triggered Quizzing** | High — reinforces and assesses what was just taught. | Medium-high — quiz cards, timers, live scoreboards. | Reuses the same visualization engine; its results are the *fuel* for the adaptive-learning loop. | ✅ **Chosen — Secondary** |
| Bilingual Dictation & Translation | Medium — useful utility, but closer to "transcription tool" than "teaching." | Medium — side-by-side text panels. | Lower synergy with the 3D/animation ask. | 🔜 Phase-2 (Section 16) |
| Hands-Free Activity Guide | Medium-high — great for lab/activity periods. | Medium — step lists, timers. | Can be layered *on top of* the visualization engine later (a "guided mode"). | 🔜 Phase-2 (Section 16) |

**Why this pair, specifically:** Concept Simplification and Quizzing form a closed pedagogical loop — *explain → check understanding → know what to fix next time.* That loop is also the cleanest possible demo: a judge can ask Genius to explain mitosis, watch a labelled animation appear with narration, then say "quiz lo" and watch a question card appear with a live scoreboard, all without touching a keyboard. The architecture (Section 5) is deliberately built so that the other two requirements slot in as **new "skills"** without restructuring anything — they are not abandoned, just sequenced later.

---

## 3. Design Philosophy — Non-Negotiables

These principles guided every technical decision in this document:

1. **The teacher stays in charge.** Genius is a co-pilot, not an autopilot. It explains *when asked*, can be interrupted, paused, or overridden at any point ("ruko", "skip karo", "wapas batao").
2. **Grounded over generative.** Concept explanations are retrieved from the actual NCERT textbook corpus before the LLM phrases them. If nothing relevant is found, Genius says so honestly rather than guessing — critical for a tool used in front of a class.
3. **Hinglish is the default language, not a translation layer.** The system is designed around code-switched speech from the ground up (STT, intent matching, and TTS), not "translate to English, think, translate back."
4. **Every concept gets a visual.** Speech-only responses are treated as the *fallback*, not the norm — the smart board should almost always be showing something.
5. **₹0 operating cost.** Every default component in the stack has a genuinely free tier or runs fully offline/local. Paid APIs are listed only as optional upgrades.
6. **Low-bandwidth resilient.** Government schools often have patchy connectivity. The architecture supports a fully local/offline mode (local STT/TTS/LLM via Ollama) with cloud APIs as an accelerator, not a dependency.
7. **Modular, swappable blocks.** STT, LLM, TTS, RAG store, and visual renderers are independent services behind small interfaces — any one can be swapped (e.g., Groq → local Ollama, edge-tts → Indic-Parler-TTS) without touching the rest of the system.
8. **Privacy by default.** No student-identifying data leaves the local network. Quiz/feedback logs used for the adaptive loop are stored locally and anonymised at the class level.
9. **Honest about "self-learning."** We do not claim a black-box AI that magically gets smarter. Section 11 specifies *exactly* what adapts, on what signal, and how — an explainable, class-level contextual-bandit system with a clear roadmap to deeper RL.

---

## 4. Research & Inspiration — Competitive Landscape

Before designing Genius, we surveyed both **private/proprietary** products and **open-source** projects across three areas: (a) AI tutoring/teaching-assistant products, (b) the Indian-language voice-AI ecosystem, and (c) AI-driven visualization/animation for education — including a close look at **Google NotebookLM**, as suggested in the brief. Below is what we found and, more importantly, *what we are deliberately borrowing vs. doing differently*.

### 4.1 Google NotebookLM — "One Grounded Source, Many Output Formats"

NotebookLM's core idea is simple but powerful: a user uploads source material, and the tool then offers **several different ways to consume that same grounded knowledge** from its "Studio" panel — a podcast-style **Audio Overview** (two AI hosts discussing the material), an interactive **Mind Map** (a branching diagram of key concepts and how they relate), a narrated **Video Overview** (slides + voice), and written **Reports/Study Guides/FAQs**. Critically, all of these are generated *from the same underlying source*, so they never contradict each other — and recent updates let users keep multiple versions of each output type side-by-side in the Studio.

**What we borrow:** the *"one grounded brain → many simultaneous output formats"* pattern is exactly the shape of a classroom co-pilot. The same NCERT-grounded explanation of, say, the water cycle should be simultaneously **spoken** (NotebookLM's Audio Overview, but live and conversational instead of a pre-rendered podcast), **diagrammed** (NotebookLM's Mind Map, but as a labelled process diagram instead of a generic concept graph), and available as **on-screen key points** (NotebookLM's Study Guide/Report, condensed to a sidebar).

**What we do differently:** NotebookLM's outputs are *asynchronous and post-hoc* — you upload material, wait, then browse generated artifacts. Genius's outputs must be **synchronous and real-time** (a teacher mid-sentence cannot wait 60 seconds for a podcast to render). We also scope each visual to *one concept at a time* (generated on the fly per question) rather than "map of an entire document," and we add an **interactive 3D/simulation layer** that NotebookLM does not attempt — necessary for the brief's chemistry/biology/physics demonstration requirement.

### 4.2 Sahayak AI & India's GovTech-AI Hackathon Ecosystem

"Sahayak" (Hindi for "helper") has emerged as a recurring theme across recent Indian hackathons — including as a named problem statement in a Google Agentic AI Day hackathon — for AI assistants targeting **multi-grade, low-resource Indian government classrooms**. Typical implementations accept voice/text/image input from the teacher, use Gemini-class models to generate hyper-local stories, differentiated worksheets, and "blackboard-ready" diagrams, and answer student questions ("why is the sky blue?") with simple local-language analogies — usually on a Gemini + Vertex AI Speech-to-Text + Firebase + React stack. This sits alongside real government programmes: Haryana's own AI & Robotics Lab initiative (STEMpedia partnership, 50 schools, 20,000+ students) and the NIPUN Haryana Mission's AI-training pilots for teachers, both of which confirm this is a live, real-world context — not a hypothetical one.

**What we borrow:** the *"teacher speaks a request → AI returns a classroom-ready asset"* interaction model, the emphasis on **simple, local-language analogies** for student questions, and the idea of **board-ready visual aids** generated on demand.

**What we do differently:** Sahayak-style tools are predominantly **pre/post-class prep assistants** — used while planning a lesson or grading, not *during* it. Genius is designed for **live, in-lesson use**: hands-free during the 40-minute period itself, with a tight teach-then-quiz loop and a memory of what worked for *this specific class*. We also deliberately avoid billed Google Cloud services (Vertex AI, Firebase) in favour of free-tier/open-source equivalents (Section 6), directly honouring the brief's "free of cost" requirement.

### 4.3 AI4Bharat — The Open Hinglish-Ready Voice Stack

AI4Bharat (a research lab at IIT Madras) publishes a suite of **open, MIT-licensed** speech models for Indian languages: **IndicConformer**, a compact (≈30M–600M parameter) ASR model covering all 22 scheduled Indian languages and built for real-time/on-device use, and **Indic-Parler-TTS**, a single text-to-speech model that *auto-detects* whether a prompt is Hindi or English and switches voice/accent accordingly. Separately, independent fine-tunes of OpenAI's Whisper — such as *Whisper-Hindi2Hinglish* and *zero-stt-hinglish* — specifically target **Hindi-English code-switched speech**, an area where research shows stock Whisper's word-error-rate climbs noticeably (code-switching is a well-documented hard case for ASR generally, not just for Indian languages).

**What we borrow:** rather than building or fine-tuning our own speech models, Genius **stands on this open stack** — a Hinglish-tuned Whisper variant (or AI4Bharat's IndicConformer) for STT, and Indic-Parler-TTS / Microsoft's free edge-tts Hindi+English neural voices for TTS. Both run acceptably on CPU for a prototype and are completely free.

**What we add:** a lightweight **transliteration-tolerant matching layer** after STT. Classroom Hinglish freely mixes scripts and registers — "photosynthesis ka process," "prakash sanshleshan," "do molecule milke" — so our intent router and RAG query layer normalise and fuzzy-match across Devanagari/Roman script and Hindi/English synonyms before hitting the NCERT index (Section 8.4).

### 4.4 PhET Simulations & "Generative Manim" — Two Ends of the 3D-for-Science Spectrum

At one end, the University of Colorado's **PhET Interactive Simulations** project offers 100+ free, **open-source**, research-validated HTML5 simulations spanning physics, chemistry, biology, earth science and math — from atomic models and circuit builders to pH labs and wave interference — all embeddable directly via iframe and already used in classrooms worldwide. At the other end, projects like **Generative Manim** and **"manimator"** use an LLM (GPT-4o/Claude-class models) to *write Manim code* (the animation engine behind the "3Blue1Brown" YouTube style) from a plain-text prompt and then render a video — powerful for *arbitrary* topics, but rendering takes real wall-clock time and the result is a video, not something interactive.

**What we borrow:** PhET gives us a **zero-effort, instantly interactive 3D/simulation layer** for the highest-value NCERT science topics (states of matter, atomic structure, simple circuits, wave behaviour, acid-base chemistry, and more) — there is no reason to rebuild what already exists and is free. The Generative-Manim line of work *validates* that an LLM can reliably emit working visualization code for a constrained target — which underpins our own approach of having the LLM emit **Three.js scene specifications** for topics PhET doesn't cover.

**What we add — a two-tier 3D strategy** (detailed in Section 9.3): **Tier 1** is a curated library mapping NCERT topics to PhET simulations (instant, reliable, zero compute). **Tier 2** is **LLM-generated Three.js**, used for the long tail — and crucially, every successfully generated Tier-2 scene is **cached and added to the library**, so the asset library *grows over time*. This is itself a concrete, visible form of the "self-learning" the brief asks for: Genius's visual vocabulary literally expands with use.

### 4.5 Open-Source AI Tutors, Pedagogy, and Adaptive/RL Research

Several projects and research systems shaped our pipeline and adaptive-loop design:

- **Khan Academy's Khanmigo** built its entire reputation on the **Socratic method** — deliberately *not* giving direct answers, instead asking guiding questions, while also being one of the first mainstream tools to bake in two-way voice (STT + TTS) from the start.
- **Open TutorAI**, an open-source LLM+RAG tutoring platform, structures its prompts in **layers** — a "global context" layer (what kind of interaction this is: lesson, quiz, review), an "instructional logic" layer (how to sequence the teaching), an "adaptive variable" layer (learner level/progress), and a "post-interaction" layer (what follow-up — quiz, re-explanation, reinforcement — comes next).
- **VTutor** is an open-source SDK for generative-AI pedagogical agents with lip-synced 2D/3D avatars and WebGL rendering — a useful reference if Genius later adds an on-screen "presenter" character.
- **OATutor** and the research system **Korbit** are open/academic intelligent-tutoring systems that use **reinforcement learning to choose the next pedagogical action** (which hint, which problem, which feedback) based on a running model of the learner, with published evidence that personalised, ML-selected feedback measurably improves learning outcomes. A general-purpose open-source reference, **eduadapt-ai**, implements this as a clean pipeline: *interactions → knowledge tracing → RL optimizer → personalised recommendation → outcome → feedback loop*.

**What we borrow:** Khanmigo's instinct to **check for understanding** (we add light "samajh aaya?" check-ins between explanation and quiz, without making the *whole* system Socratic — the brief asks for explanation, so Genius explains first, then checks); Open TutorAI's **layered prompt structure** (Section 8.5); and the **interactions → tracing → RL → recommendation → feedback** loop shape from eduadapt-ai/Korbit/OATutor for our adaptive layer (Section 11).

**What we do differently:** the research RL systems above operate **per-student**, requiring logins and longitudinal data we won't have on day one. Genius v1 operates at the **class level** — *"For Class 9-B, diagram-first explanations are out-performing story-first ones on Biology topics"* — a coarser signal, but one that is immediately computable from a single classroom's worth of data, fully explainable to a teacher, and a credible stepping stone to per-student personalisation later (Section 11.4).

### 4.6 Synthesis — From Inspiration to Genius

| Inspiration | Core idea we borrow | Our adaptation |
|---|---|---|
| Google NotebookLM | One grounded source → many simultaneous output formats (audio, visual map, notes) | Real-time, per-concept multi-modal output instead of post-hoc, whole-document outputs; adds an interactive 3D layer |
| Sahayak AI / India GovTech hackathons | Voice-driven, India-context AI helper for teachers; board-ready visual aids | Shift from pre/post-class prep tool to a **live, hands-free, in-lesson co-pilot**; fully free/open stack (no Vertex/Firebase billing) |
| AI4Bharat (IndicConformer, Indic-Parler-TTS, Whisper-Hinglish fine-tunes) | Open, free, Hinglish-capable ASR & TTS | Add a transliteration/synonym-tolerant matching layer so NCERT retrieval understands "prakash sanshleshan" ≈ "photosynthesis" |
| PhET Simulations + Generative Manim/manimator | Pre-built interactive sims for common topics; LLM-to-visualization-code for arbitrary topics | Two-tier visualization: curated PhET/asset library first, **cached** LLM-generated Three.js second — library grows with use |
| Khanmigo, Open TutorAI, VTutor, OATutor/Korbit/eduadapt-ai | Socratic check-ins; layered pedagogical prompting; RL-driven adaptive teaching | Light "check understanding" prompts (not full Socratic); layered prompt design; **class-level** contextual bandit instead of per-student deep RL |

---
