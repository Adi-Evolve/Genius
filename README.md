# Genius — Voice-Native AI Teaching Co-Pilot

**Genius** is a hands-free, voice-first AI classroom co-pilot designed for Indian government classrooms. The teacher interacts with it using natural **Hinglish** (a blend of colloquial Hindi and English). Genius listens, retrieves grounded textbook knowledge from the NCERT syllabus, and projects dynamic chalkboard simulations and quiz cards onto the smart board, completely narrated by a warm male teacher voice.

---

## 🚀 Key Features

1. **Concept Samjhao (Concept Explanation)**:
   - Voice-triggered concept explanations grounded in the NCERT curriculum (RAG).
   - Interactive, custom 2D canvas chalkboard simulations for:
     - **Leaf Photosynthesis**: Water, carbon dioxide, and light molecules moving and converting to glucose and oxygen.
     - **Bohr Atomic Model**: Electrons orbiting a central positive nucleus with particle trails.
     - **Current Electricity**: Closed/open wire circuit, battery, rheostat slider, lightbulb, switch click toggle, and flowing charge carriers.
     - **States of Matter**: Thermal particle motion toggle tabs (Solid, Liquid, Gas).
     - **DNA Helix**: Rotating double-stranded 3D-projected cosine helix.
2. **Quick Voice Quiz**:
   - Voice-triggered multiple-choice questions dynamically generated based on the active topic.
   - Verbal question announcements, answer cards, and live scoring.
   - Hands-free voice answer checking (e.g., *"Option B"*).
3. **Dictation Mode (with Photo OCR)**:
   - Side-by-side chalkboard layout showing English text dictations on the left and Hindi translations on the right.
   - NCERT passage dropdown menu with read-aloud functionality.
   - **Textbook Photo OCR**: Direct image/camera file upload translating textbook screenshots into board dictations using Groq Multimodal Vision.
4. **Hands-Free Lab Activity Guide**:
   - Step-by-step checklist guide for class experiments (e.g. leaf starch test, Ohm's law).
   - Circular countdown canvas timer.
   - Speech command parser recognizing navigations (e.g. *"next"*, *"back"*, *"start timer"*, *"pause"*).

---

## 🛠️ Tech Stack

### Frontend & UI Layout
- **Streamlit**: Wrapping and rendering the single-page HTML app.
- **Microphone Self-Healing Iframe**: Patches parent iframe permissions to bypass browser permission blocks.
- **HTML5 Canvas Simulation Engine**: Handles DPI scaling and automatic self-healing redraws when elements transition into view.
- **Vanilla CSS (tokens.css, layout.css, board.css)**: Implements a warm, dark-brown wood sidebar combined with a clean classroom chalkboard aesthetic.

### AI Pipeline & Models
- **Groq Whisper ASR (`whisper-large-v3-turbo`)**: Captures speech, biased toward Hinglish terminology via specific prompt styling.
- **Groq LLM (`llama-3.3-70b-versatile`)**: Generates explanations and structured quizzes in JSON format.
- **Groq Multimodal Vision (`meta-llama/llama-4-scout-17b-16e-instruct`)**: Transcribes and translates uploaded textbook screenshots (OCR).
- **Edge-TTS (`hi-IN-MadhurNeural`)**: Powers a warm male Hindi teacher voice running asynchronously.
- **RAG Engine (ChromaDB / SentenceTransformers)**: Contextual semantic search against NCERT textbook files, with keyword match fallbacks for Hindi/Hinglish synonyms.

---

## 🧠 Prompt Design

### 1. Hinglish Code-Switching Explanation Prompt
The LLM (`llama-3.3-70b-versatile`) is instructed to output a structured JSON spec containing both speech transcriptions and board elements:
```json
{
  "title": "Topic Name",
  "subtitle": "Hindi Subtitle · NCERT Class X · Ch. Y",
  "spoken_text": "Namaste class! Aaj hum baat karenge photosynthesis ke bare mein. Dekho, leaves ke andar... [conversational Hinglish]",
  "board_text": "• Photosynthesis [प्रकाश संश्लेषण] is food making process in plants...",
  "hindi_text": "प्रकाश संश्लेषण वह प्रक्रिया है जिसके द्वारा...",
  "visual_type": "threejs",
  "visual_name": "photosynthesis",
  "key_terms": ["Chlorophyll", "Glucose [C₆H₁₂O₆]"],
  "ncert_ref": "Class 9 Science, Chapter 6, Page 82"
}
```

### 2. Multimodal OCR Prompt
Used by the vision scanner to extract textbook passage text and instantly translate it:
```
Extract all readable textbook passage text from this image and translate it to Hindi. 
Return the result in a JSON object with 'transcription' containing the extracted English text 
and 'translation' containing the translated Hindi text. Do not output anything other than JSON.
```

---

## 🌐 Localization Strategy

Indian classrooms rely on a blend of colloquial Hindi and technical English. Genius tackles this with:
1. **Transliteration Mapping**: Maps Devanagari or Romanized Hindi synonyms to standard scientific keywords:
   - `prakash sanshleshan` / `प्रकाश संश्लेषण` ➔ `photosynthesis`
   - `vidyut dhara` / `bijli` ➔ `current electricity`
   - `parmanu structure` ➔ `atomic structure`
2. **Accented Neural TTS**: Utilizing Microsoft’s `hi-IN-MadhurNeural` Hindi accent to make English terminology sound natural and clear to regional students.
3. **Double-Board Presentation**: Keeps the technical term and English description on the primary board, with a sliding translation overlay in Hindi Devanagari.

---

## 📂 Project Structure

```
genius/
├── app.py                       # Streamlit app router & entry point
├── devwatch.py                  # Auto-reload file watcher (touches app.py on asset edits)
├── requirements.txt             # Primary Python library requirements
├── start_dev.bat                # Windows setup boot batch file
├── data/                        # Static local database files & curriculum indices
│   └── ncert_chunks.json        # Pre-processed NCERT textbook fragments for RAG
├── static/                      # Frontend styling assets
│   ├── css/                     # Modulised CSS files (board, layout, activity, fonts)
│   └── js/                      # Swappable JS helper utilities
├── genius-backend/              # FastAPI server backend
│   ├── main.py                  # API routes (OCR, Explain, transcribe)
│   ├── requirements.txt         # Backend Python dependencies
│   └── core/                    # Core modules (ASR, TTS, LLM, RAG)
│       ├── intent.py            # Intent and topic classifier
│       ├── llm.py               # Llama client & schema parser
│       ├── rag.py               # ChromaDB semantic search fallback
│       ├── stt.py               # Whisper audio transcriber
│       └── tts.py               # Async Edge-TTS engine
└── genius/                      # Streamlit frontend package
    ├── state.py                 # Streamlit state manager
    ├── ui/
    │   ├── index.html           # Main Chalkboard SPA (HTML5, JS, Canvas, CSS)
    │   ├── landing.py           # Streamlit landing view
    │   └── layout.py            # Streamlit layout viewport wrapper (allow-microphone)
```

---

## 💻 Getting Started & Local Setup

### 1. Prerequisites
- Python 3.10 or higher
- A Groq API Key (added to `.env`)

### 2. Environment Configuration
Create a `.env` file in the root directory (and inside `genius-backend/` if launching separately):
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r genius-backend/requirements.txt
```

### 4. Running the Project

#### Start the FastAPI Backend Server
Launch the API backend on port `8000` (required for transcribing, explanations, OCR, and Edge-TTS):
```bash
cd genius-backend
uvicorn main:app --reload --port 8000
```

#### Start the Streamlit Frontend & File Watcher
Double-click `start_dev.bat` or run:
```bash
# Terminal 1: Starts devwatch to auto-update Streamlit on HTML/JS/CSS edits
python devwatch.py

# Terminal 2: Starts Streamlit UI
streamlit run app.py --server.runOnSave true --server.fileWatcherType watchdog
```
Now, open your browser at [http://localhost:8501](http://localhost:8501) to interact with Genius.
