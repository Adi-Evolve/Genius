import os
import asyncio
import tempfile
import base64
import hashlib
import threading
import edge_tts

# Default speech configurations
DEFAULT_VOICE = "hi-IN-SwaraNeural"  # Warm Hindi female teacher voice
DEFAULT_RATE = "-10%"               # Slightly slower for classroom intelligibility

def run_async_in_thread(coro):
    """Safely runs an async coroutine in a dedicated background thread.
    
    Prevents 'Event loop is already running' conflicts in Streamlit.
    """
    result = []
    exception = []

    def target():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            res = loop.run_until_complete(coro)
            result.append(res)
        except Exception as e:
            exception.append(e)
        finally:
            loop.close()

    thread = threading.Thread(target=target)
    thread.start()
    thread.join()

    if exception:
        raise exception[0]
    return result[0] if result else None

async def _generate_audio_file(text: str, output_path: str, voice: str, rate: str):
    """Internal coroutine to invoke edge-tts and save to disk."""
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)

def generate_tts_base64(text: str, voice: str = DEFAULT_VOICE, rate: str = DEFAULT_RATE) -> str:
    """Generates base64 encoded MP3 audio data for a given text.
    
    Uses edge-tts. Returns the base64 string directly for HTML embedding.
    """
    if not text.strip():
        return ""
        
    # Generate temp file path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        temp_path = temp_audio.name
        
    try:
        # Run edge-tts asynchronously in background thread
        coro = _generate_audio_file(text, temp_path, voice, rate)
        run_async_in_thread(coro)
        
        # Read the file contents and convert to base64
        with open(temp_path, "rb") as audio_file:
            audio_data = audio_file.read()
            base64_audio = base64.b64encode(audio_data).decode("utf-8")
            
        return base64_audio
    except Exception as e:
        print(f"[TTS Error] Failed to generate speech for text '{text[:30]}...': {e}")
        return ""
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

def get_text_hash(text: str) -> str:
    """Computes an MD5 hash of text for caching purposes."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()
