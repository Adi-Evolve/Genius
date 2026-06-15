import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import core modules
from core.stt import transcribe_audio_bytes
from core.intent import classify_intent
from core.llm import generate_explanation, generate_quiz, get_groq_client_async, safe_parse_json
from core.tts import generate_tts_base64
from core.rag import search_ncert_curriculum

load_dotenv()

app = FastAPI(title="Genius AI Backend", description="Backend services for the Genius Voice AI Teaching Assistant")

# Configure CORS for local browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CommandRequest(BaseModel):
    text: str

@app.get("/")
async def root():
    return {"status": "online", "message": "Genius AI Backend is running."}

@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Receives audio file from browser recording, transcribes, and classifies intent."""
    try:
        audio_bytes = await file.read()
        ext = file.filename.split(".")[-1] if file.filename else "webm"
        
        # Transcribe
        transcription = await transcribe_audio_bytes(audio_bytes, ext)
        if not transcription:
            return {
                "transcription": "",
                "intent": "idle",
                "topic": ""
            }
            
        # Classify intent
        intent, topic = classify_intent(transcription)
        return {
            "transcription": transcription,
            "intent": intent,
            "topic": topic
        }
    except Exception as e:
        print(f"[API Error] Transcribe failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/command")
async def command(request: CommandRequest):
    """Parses a typed text command for intent and topic."""
    try:
        text = request.text
        intent, topic = classify_intent(text)
        return {
            "transcription": text,
            "intent": intent,
            "topic": topic
        }
    except Exception as e:
        print(f"[API Error] Command routing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/explain")
async def explain(topic: str, grade: str = "9", subject: str = "Science", language: str = "Hinglish"):
    """Fetches NCERT context and generates concept explanation along with TTS audio."""
    try:
        # 1. Query RAG
        context = search_ncert_curriculum(topic, grade, subject)
        
        # 2. Query LLM
        explanation = await generate_explanation(topic, grade, subject, language, context)
        
        # 3. Generate TTS audio
        audio_base64 = ""
        if explanation.get("spoken_text"):
            audio_base64 = await generate_tts_base64(explanation["spoken_text"])
            
        return {
            "explanation": explanation,
            "audio_base64": audio_base64
        }
    except Exception as e:
        print(f"[API Error] Explanation generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/quiz/generate")
async def generate_quiz_endpoint(topic: str, grade: str = "9", subject: str = "Science"):
    """Generates 5 multiple-choice questions for the active topic."""
    try:
        context = search_ncert_curriculum(topic, grade, subject)
        questions = await generate_quiz(topic, grade, subject, context)
        return {
            "questions": questions
        }
    except Exception as e:
        print(f"[API Error] Quiz generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tts")
async def tts(text: str, voice: str = "hi-IN-MadhurNeural", rate: str = "-10%"):
    """Converts a specific text to base64 audio."""
    try:
        audio_base64 = await generate_tts_base64(text, voice, rate)
        return {
            "audio_base64": audio_base64
        }
    except Exception as e:
        print(f"[API Error] TTS failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class OCRRequest(BaseModel):
    image_base64: str

@app.post("/api/dictate/ocr")
async def dictate_ocr(request: OCRRequest):
    """Performs image OCR on base64 encoded photo using Llama 3.2 Vision and returns transcription and translation."""
    try:
        client = await get_groq_client_async()
        
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all readable textbook passage text from this image and translate it to Hindi. Return the result in a JSON object with 'transcription' containing the extracted English text and 'translation' containing the translated Hindi text. Do not output anything other than JSON."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{request.image_base64}"
                            }
                        }
                    ]
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            response_format={"type": "json_object"}
        )
        
        content = chat_completion.choices[0].message.content
        parsed = safe_parse_json(content)
        return parsed
    except Exception as e:
        print(f"[API Error] OCR failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

