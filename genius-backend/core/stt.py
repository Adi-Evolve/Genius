import os
import tempfile
from groq import AsyncGroq
from dotenv import load_dotenv

# Load env variables
load_dotenv()

async def get_groq_client_async():
    """Initializes and returns the AsyncGroq client if API key is present."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("Groq API key not configured. Please add it to your .env file.")
    return AsyncGroq(api_key=api_key)

async def transcribe_audio_bytes(audio_bytes: bytes, file_ext: str = "webm") -> str:
    """Sends audio bytes directly to Groq Whisper STT API and returns transcribed text asynchronously."""
    try:
        client = await get_groq_client_async()
    except ValueError as e:
        print(f"[STT Offline] Groq client not configured: {e}")
        return ""
    
    # Save the bytes temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_path = temp_audio.name
        
    try:
        with open(temp_path, "rb") as file:
            transcription = await client.audio.transcriptions.create(
                file=(f"audio.{file_ext}", file.read()),
                model="whisper-large-v3-turbo",
                # Prompt helps Whisper bias toward Hinglish transcription rules
                prompt="class, samjhao, photosynthesis, prakash sanshleshan, math, science, hindi, english, Hinglish code-switching, quiz lo",
                response_format="json",
                language="hi" # Hinting Hindi increases Hinglish accuracy
            )
        return transcription.text
    except Exception as e:
        print(f"[STT Error] Failed to transcribe audio: {e}")
        return ""
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
