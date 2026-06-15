import os
import tempfile
from groq import Groq
from dotenv import load_dotenv

# Load env variables
load_dotenv()

def get_groq_client():
    """Initializes and returns the Groq client if API key is present."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("Groq API key not configured. Please add it to your .env file.")
    return Groq(api_key=api_key)

def transcribe_audio_bytes(audio_bytes: bytes, file_ext: str = "webm") -> str:
    """Sends audio bytes directly to Groq Whisper STT API and returns transcribed text."""
    try:
        client = get_groq_client()
    except ValueError as e:
        # Graceful degradation in offline/no-key mode
        print(f"[STT Offline] Groq client not configured. Voice command is inactive. {e}")
        return ""
    
    # Save the bytes temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_path = temp_audio.name
        
    try:
        with open(temp_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(f"audio.{file_ext}", file.read()),
                model="whisper-large-v3-turbo",
                # Prompt helps Whisper bias toward Hinglish transcription rules
                prompt="class, samjhao, photosynthesis, prakash sanshleshan, math, science, hindi, english, Hinglish code-switching",
                response_format="json",
                language="hi" # Hinting Hindi increases Hinglish accuracy
            )
        return transcription.get("text", "")
    except Exception as e:
        print(f"[STT Error] Failed to transcribe audio: {e}")
        return ""
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

def classify_intent(text: str) -> tuple[str, str]:
    """Classifies transcription text into intents (explain, quiz, dictating, activity, clear, summary) and extracts the topic if applicable.
    
    Returns:
        tuple: (intent_name, topic)
    """
    text_lower = text.lower().strip()
    
    # Check for empty input
    if not text_lower:
        return "idle", ""
        
    # 1. Clear Board Intent
    if any(keyword in text_lower for keyword in ["clear board", "wipe board", "saaf karo", "mitao", "clean board", "wipe"]):
        return "clear", ""
        
    # 2. Quiz Intent
    if any(keyword in text_lower for keyword in ["quiz lo", "take quiz", "test lo", "ask question", "start quiz", "quiz shuru", "sawaal poocho"]):
        return "quiz", ""
        
    # 3. Class Summary / End Class Intent
    if any(keyword in text_lower for keyword in ["class khatam", "stop class", "summary lo", "summarize class", "end class", "report card"]):
        return "summary", ""

    # 4. Dictation Intent
    if any(keyword in text_lower for keyword in ["dictation", "dictate", "shrutlekh", "translation", "translate"]):
        # Clean topic from text
        topic = clean_topic_keywords(text, ["dictation lo", "dictation", "dictate", "shrutlekh", "translation", "translate"])
        return "dictating", topic

    # 5. Activity Intent
    if any(keyword in text_lower for keyword in ["activity", "experiment", "lab", "practical", "karke dikhao", "simulation"]):
        topic = clean_topic_keywords(text, ["activity on", "experiment on", "activity", "experiment", "lab", "practical", "simulation"])
        return "activity", topic
        
    # 6. Explain Intent (Default)
    topic = clean_topic_keywords(text, [
        "samjhao", "explain", "batao", "what is", "kya hota hai", 
        "kya hai", "ke bare mein", "ko samjhao", "define"
    ])
    
    return "explain", topic

def clean_topic_keywords(text: str, prefixes: list[str]) -> str:
    """Helper to clean intent prefixes and Hinglish grammar particles from topics."""
    text_lower = text.lower().strip()
    topic = text
    
    for prefix in prefixes:
        if text_lower.startswith(prefix):
            topic = text[len(prefix):].strip()
        elif text_lower.endswith(prefix):
            topic = text[:-len(prefix)].strip()
            
    # Extra cleaning for Hinglish particles and punctuation
    topic = topic.replace(" ko ", " ").replace(" ke ", " ").replace(" ka ", " ").strip("?,. ")
    return topic

