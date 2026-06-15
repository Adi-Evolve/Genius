import os
import json
import requests
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

def query_local_ollama(prompt: str, system_prompt: str = "", format_json: bool = True) -> str:
    """Queries a local Ollama server if it is running at http://localhost:11434.
    
    Returns the response content or None if failed.
    """
    url = "http://localhost:11434/api/chat"
    
    payload = {
        "model": "llama3", # default model
        "messages": [],
        "stream": False
    }
    
    if system_prompt:
        payload["messages"].append({"role": "system", "content": system_prompt})
    payload["messages"].append({"role": "user", "content": prompt})
    
    if format_json:
        payload["format"] = "json"
        
    try:
        response = requests.post(url, json=payload, timeout=25)
        response.raise_for_status()
        res_data = response.json()
        return res_data["message"]["content"]
    except Exception as e:
        print(f"[Ollama Query Error] local Ollama call failed: {e}")
        return None

def generate_explanation(topic: str, grade: str = "9", subject: str = "Science", language: str = "Hinglish", context_corpus: str = "") -> dict:
    """Generates a Hinglish concept explanation using Groq's LLaMA 3.3 JSON mode (or Ollama fallback).
    
    Includes classroom analogies, visual specification, and key NCERT references.
    """
    # 1. Global Context Prompt (System Prompt)
    system_prompt = f"""You are Genius (वाणी गुरु), a professional, warm, and highly engaging AI teaching assistant for Indian government schools in Haryana.
Your target audience is Class {grade} students. The subject is {subject}. 
You speak in natural classroom "Hinglish" (a smooth blend of colloquial Hindi and English as Indian teachers teach, e.g. "Dekho class, cell membrane ek protective layer hai jo...").
Always align explanation depth to Class {grade} level. Keep statements simple, clear, and grounded in NCERT textbooks.
"""

    # 2. Layered Prompts & Guidelines
    instructions = """You must output a structured JSON explanation.
Your response MUST fit this exact JSON format:
{
  "spoken_text": "Detailed, highly conversational explanation in Hinglish to be read aloud by TTS. Start with a friendly class greeting, use classroom analogies, explain step-by-step, and end with 'Samajh aaya?' or a short check-in.",
  "board_text": "Clear, bullet-pointed, simplified chalk notes to be written on the green blackboard. Keep lines short. Include Hindi translations in brackets next to key terms.",
  "visual_spec": {
    "type": "phet|threejs|svg",
    "topic": "Search topic name for simulator matching",
    "params": {
      "name": "Topic keyword matching pre-built scenes or diagrams"
    }
  },
  "key_terms": ["Term 1", "Term 2", "Term 3"],
  "ncert_ref": "Class X Subject, Chapter Y, Page Z",
  "follow_up": "Check-in question or prompt to ask if students want a quiz (Hinglish)"
}

Rules:
1. "visual_spec.type" should be:
   - "phet" if the topic has a standard PhET simulator (e.g. states of matter, atomic structure, circuits, waves, projectile motion, friction, gravity).
   - "threejs" if the topic is biological/molecular (e.g. photosynthesis, dna, mitosis, water cycle, digestive system, solar system, atoms).
   - "svg" as a fallback diagram for other topics.
2. Ground your facts strictly on the provided context if present.
"""

    user_query = f"Explain the topic: '{topic}'"
    if context_corpus:
        user_query += f"\n\nHere is some reference text from the NCERT textbook to ground your answer:\n{context_corpus}"

    try:
        client = get_groq_client()
    except ValueError as e:
        # Fallback 1: Local Ollama
        print(f"[LLM Offline] Groq API key not configured. Trying local Ollama... {e}")
        local_res = query_local_ollama(user_query, f"{system_prompt}\n{instructions}", format_json=True)
        if local_res:
            try:
                data = json.loads(local_res)
                required_fields = ["spoken_text", "board_text", "visual_spec", "key_terms", "ncert_ref", "follow_up"]
                for field in required_fields:
                    if field not in data:
                        data[field] = ""
                return data
            except Exception as e_json:
                print(f"[Ollama JSON Parse Error] Failed to parse: {e_json}")
        # Fallback 2: Static Mock
        return get_mock_explanation(topic, grade, subject, language)

    messages = [
        {"role": "system", "content": f"{system_prompt}\n{instructions}"},
        {"role": "user", "content": user_query}
    ]

    try:
        # Request completion from LLaMA 3.3 with JSON mode enabled
        completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=1500
        )
        
        raw_response = completion.choices[0].message.content
        data = json.loads(raw_response)
        
        # Validate required fields
        required_fields = ["spoken_text", "board_text", "visual_spec", "key_terms", "ncert_ref", "follow_up"]
        for field in required_fields:
            if field not in data:
                data[field] = ""
        return data
        
    except Exception as e:
        print(f"[LLM Error] Failed to generate LLaMA explanation: {e}")
        # Fallback 1: Local Ollama
        print("Trying local Ollama as fallback...")
        local_res = query_local_ollama(user_query, f"{system_prompt}\n{instructions}", format_json=True)
        if local_res:
            try:
                data = json.loads(local_res)
                required_fields = ["spoken_text", "board_text", "visual_spec", "key_terms", "ncert_ref", "follow_up"]
                for field in required_fields:
                    if field not in data:
                        data[field] = ""
                return data
            except Exception as e_json:
                print(f"[Ollama JSON Parse Error] Failed to parse: {e_json}")
        # Fallback 2: Static Mock
        return get_mock_explanation(topic, grade, subject, language)

def get_mock_explanation(topic: str, grade: str, subject: str, language: str) -> dict:
    """Generates a high-quality offline fallback explanation when Groq and Ollama are unavailable."""
    return {
        "spoken_text": f"Dekho class, aaj hum '{topic}' ke baare mein samjhenge. Yeh humare Class {grade} ke {subject} syllabus ka ek important topic hai. Photosynthesis ya atomic structure jaisi cheezein hume physical experiments aur 3D visualizations ke zariye samajh aati hain. Kya aap taiyaar hain? Samajh aaya?",
        "board_text": f"• Topic: {topic} (Kaksha {grade})\n• Subject: {subject}\n• Key Concept: Grounded in NCERT curriculum\n• Visualization: Interactive simulations loaded above\n• Status: Running in offline/fallback mode.",
        "visual_spec": {
            "type": "threejs",
            "topic": topic.lower(),
            "params": {"name": topic.lower()}
        },
        "key_terms": [topic, "NCERT", "Classroom"],
        "ncert_ref": f"Class {grade} {subject}, Chapter 1",
        "follow_up": "Kya aapko is topic pe ek quiz lena hai? Bolo 'Ab quiz lo'!"
    }
