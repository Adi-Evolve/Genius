import os
import tempfile
import base64
import hashlib
import edge_tts

DEFAULT_VOICE = "hi-IN-MadhurNeural"  # Warm Hindi male teacher voice
DEFAULT_RATE = "-10%"               # Slightly slower for classroom intelligibility

async def generate_tts_base64(text: str, voice: str = DEFAULT_VOICE, rate: str = DEFAULT_RATE) -> str:
    """Generates base64 encoded MP3 audio data for a given text asynchronously.
    
    Uses edge-tts. Returns the base64 string directly for HTML embedding.
    """
    if not text.strip():
        return ""
        
    # Generate temp file path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        temp_path = temp_audio.name
        
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(temp_path)
        
        # Read the file contents and convert to base64
        with open(temp_path, "rb") as audio_file:
            audio_data = audio_file.read()
            base64_audio = base64.b64encode(audio_data).decode("utf-8")
            
        return base64_audio
    except Exception as e:
        print(f"[TTS Error] Failed to generate speech: {e}")
        return ""
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

def get_text_hash(text: str) -> str:
    """Computes an MD5 hash of text for caching purposes."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()
