import os
import json
import requests
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

def safe_parse_json(text: str) -> dict:
    """Safely parses JSON strings, stripping any markdown triple backtick enclosures if present."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```json") or lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)

async def query_local_ollama_async(prompt: str, system_prompt: str = "", format_json: bool = True) -> str:
    """Queries a local Ollama server if it is running at http://localhost:11434 asynchronously."""
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "llama3",
        "messages": [],
        "stream": False
    }
    if system_prompt:
        payload["messages"].append({"role": "system", "content": system_prompt})
    payload["messages"].append({"role": "user", "content": prompt})
    if format_json:
        payload["format"] = "json"
        
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        def sync_post():
            return requests.post(url, json=payload, timeout=25)
        response = await loop.run_in_executor(None, sync_post)
        response.raise_for_status()
        res_data = response.json()
        return res_data["message"]["content"]
    except Exception as e:
        print(f"[Ollama Query Error] local Ollama call failed: {e}")
        return None

async def generate_explanation(topic: str, grade: str = "9", subject: str = "Science", language: str = "Hinglish", context_corpus: str = "") -> dict:
    """Generates a Hinglish concept explanation using Groq's LLaMA 3.3 JSON mode asynchronously."""
    system_prompt = f"""You are Genius (वाणी गुरु), a professional, warm, and highly engaging AI teaching assistant for Indian government schools in Haryana.
Your target audience is Class {grade} students. The subject is {subject}. 
You speak in natural classroom "Hinglish" (a smooth blend of colloquial Hindi and English as Indian teachers teach, e.g. "Dekho class, cell membrane ek protective layer hai jo...").
Always align explanation depth to Class {grade} level. Keep statements simple, clear, and grounded in NCERT textbooks.
"""

    instructions = """You must output a structured JSON explanation.
Your response MUST fit this exact JSON format:
{
  "title": "Topic Name",
  "subtitle": "Hindi Title / Subtitle · NCERT Class X · Ch. Y",
  "spoken_text": "Detailed, highly conversational explanation in Hinglish to be read aloud by TTS. Start with a friendly class greeting, use classroom analogies, explain step-by-step, and end with 'Samajh aaya?' or a short check-in.",
  "board_text": "Clear, bullet-pointed, simplified chalk notes to be written on the green blackboard. Keep lines short. Include Hindi translations in brackets next to key terms.",
  "hindi_text": "Hindi translation/summary of the concept for the board display.",
  "visual_type": "phet|threejs|svg",
  "visual_name": "Topic keyword matching pre-built scenes or diagrams (e.g., photosynthesis, atomic structure, dna, states of matter, circuits)",
  "key_terms": ["Term 1", "Term 2", "Term 3"],
  "ncert_ref": "Class X Subject, Chapter Y, Page Z"
}

Rules:
1. "visual_type" should be:
   - "phet" if the topic has a standard PhET simulator (e.g. states of matter, circuits, waves, friction, gravity, projectile).
   - "threejs" if the topic is biological/molecular (e.g. photosynthesis, dna, mitosis, water cycle, digestive system, solar system, atoms).
   - "svg" as a fallback diagram for other topics.
2. Ground your facts strictly on the provided context if present.
"""

    user_query = f"Explain the topic: '{topic}'"
    if context_corpus:
        user_query += f"\n\nHere is some reference text from the NCERT textbook to ground your answer:\n{context_corpus}"

    try:
        client = await get_groq_client_async()
        messages = [
            {"role": "system", "content": f"{system_prompt}\n{instructions}"},
            {"role": "user", "content": user_query}
        ]
        completion = await client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=1500
        )
        raw_response = completion.choices[0].message.content
        data = safe_parse_json(raw_response)
    except Exception as e:
        print(f"[LLM Error] Groq API fail: {e}. Trying Ollama...")
        local_res = await query_local_ollama_async(user_query, f"{system_prompt}\n{instructions}", format_json=True)
        if local_res:
            try:
                data = safe_parse_json(local_res)
            except Exception:
                data = get_mock_explanation(topic, grade, subject)
        else:
            data = get_mock_explanation(topic, grade, subject)
            
    # Validate fields
    required_fields = ["title", "subtitle", "spoken_text", "board_text", "hindi_text", "visual_type", "visual_name", "key_terms", "ncert_ref"]
    for field in required_fields:
        if field not in data:
            data[field] = ""
    return data

async def generate_quiz(topic: str, grade: str = "9", subject: str = "Science", context_corpus: str = "") -> list:
    """Generates a Hinglish 5-question quiz using Groq's LLaMA 3.3 asynchronously."""
    system_prompt = f"""You are Genius (वाणी गुरु), a professional, warm, and highly engaging AI teaching assistant for Indian government schools in Haryana.
Your target audience is Class {grade} students. The subject is {subject}.
"""

    instructions = """You must output a structured JSON containing a list of 5 quiz questions.
Your response MUST fit this exact JSON format:
{
  "questions": [
    {
      "q_en": "Question text in English/Hinglish (e.g. Q1. Photosynthesis process mein main energy product kya banta hai?)",
      "q_hi": "Question text in Hindi (e.g. Q1. प्रकाश संश्लेषण की प्रक्रिया में मुख्य ऊर्जा उत्पाद क्या बनता है?)",
      "options": {
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
      },
      "correct": "B"
    }
  ]
}
Each question must be multiple-choice with exactly 4 options (A, B, C, D) and specify the correct option letter.
"""

    user_query = f"Create a 5-question quiz for the topic: '{topic}'"
    if context_corpus:
        user_query += f"\n\nGround the questions on this NCERT context:\n{context_corpus}"

    try:
        client = await get_groq_client_async()
        messages = [
            {"role": "system", "content": f"{system_prompt}\n{instructions}"},
            {"role": "user", "content": user_query}
        ]
        completion = await client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.5,
            max_tokens=2000
        )
        raw_response = completion.choices[0].message.content
        data = safe_parse_json(raw_response)
        return data.get("questions", [])
    except Exception as e:
        print(f"[Quiz LLM Error] Failed to generate quiz via Groq: {e}. Returning fallback.")
        return get_mock_quiz(topic)

def get_mock_explanation(topic: str, grade: str, subject: str) -> dict:
    """Generates a high-quality offline fallback explanation when LLM services are offline."""
    t_lower = topic.lower()
    if "photo" in t_lower:
        return {
            "title": "Photosynthesis",
            "subtitle": "प्रकाश संश्लेषण · NCERT Class 9 · Ch. 6",
            "spoken_text": "Dekho class, plants apna khaana khud banate hain. Is process ko Photosynthesis yaani Prakash Sanshleshan kehte hain. Isme teen main ingredients hote hain: Suraj ki roshni yaani sunlight, paani jo roots soil se absorb karti hain, aur Carbon Dioxide (CO2) jo leaves small pores se absorb karti hain jise hum stomata bolte hain. Yeh sab milkar Chloroplast ke andar simple sugars yaani Glucose aur Oxygen banate hain. Oxygen humare saans lene ke kaam aati hai. Samajh aaya class?",
            "board_text": "• Photosynthesis (प्रकाश संश्लेषण) is food-making process in plants.\n• Key Ingredients (आवश्यक तत्व):\n  - Sunlight (सूर्य का प्रकाश)\n  - Water [H₂O] (पानी) - from soil\n  - Carbon Dioxide [CO₂] (कार्बन डाइऑक्साइड) - from air\n• Products (उत्पाद):\n  - Glucose [C₆H₁₂O₆] (भोजन/ऊर्जा)\n  - Oxygen [O₂] (ऑक्सीजन) - released into air\n• Chemical Formula:\n  6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂",
            "hindi_text": "प्रकाश संश्लेषण वह प्रक्रिया है जिसके द्वारा हरे पौधे सूर्य के प्रकाश, पानी और कार्बन डाइऑक्साइड की उपस्थिति में अपना भोजन (ग्लूकोज) तैयार करते हैं और ऑक्सीजन हवा में छोड़ते हैं। यह पूरी प्रक्रिया क्लोरोप्लास्ट में होती है।",
            "visual_type": "threejs",
            "visual_name": "photosynthesis",
            "key_terms": ["Chlorophyll", "Glucose [C₆H₁₂O₆]", "Chloroplast", "Light Reaction", "Carbon Dioxide", "ATP"],
            "ncert_ref": "Class 9 Science, Chapter 6, Page 82"
        }
    elif "atom" in t_lower:
        return {
            "title": "Atomic Structure",
            "subtitle": "परमाणु संरचना · NCERT Class 9 · Ch. 4",
            "spoken_text": "Bacho, atom yaani parmanu matter ka building block hota hai. Chalo atom ke andar dekhte hain! Iske center mein ek compact Nucleus hota hai. Nucleus mein positive charge waale Protons aur neutral Neutrons hote hain. Aur is Nucleus ke charo taraf circular orbits yaani paths mein negative charge waale Electrons ghumte hain. Niels Bohr ne bataya tha ki electrons specific discrete shells mein hi ghoom sakte hain, bina apni energy loose kiye. Samajh aaya?",
            "board_text": "• Atom Structure (परमाणु संरचना):\n• Nucleus (नाभिक) - at the center\n  - Protons [p⁺] (धनावेशित कण)\n  - Neutrons [n⁰] (उदासीन कण)\n• Orbits/Shells (कक्षाएं) - around nucleus\n  - Electrons [e⁻] (ऋणावेशित कण)\n• Bohr Orbitals Configuration:\n  - K Shell (max 2 electrons)\n  - L Shell (max 8 electrons)",
            "hindi_text": "परमाणु के केंद्र में एक नाभिक होता है जिसमें प्रोटॉन और न्यूट्रॉन होते हैं। इलेक्ट्रॉन नाभिक के चारों ओर निश्चित कक्षाओं में चक्कर लगाते हैं। रदरफोर्ड और नील बोर ने इसकी संरचना को स्पष्ट किया था।",
            "visual_type": "threejs",
            "visual_name": "atomic structure",
            "key_terms": ["Nucleus", "Electron", "Proton", "Neutron", "Bohr Model", "Orbit Shell"],
            "ncert_ref": "Class 9 Science, Chapter 4, Page 47"
        }
    else:
        return {
            "title": topic.capitalize(),
            "subtitle": f"NCERT Class {grade} · Topic Details",
            "spoken_text": f"Dekho class, aaj hum '{topic}' ke baare mein samjhenge. Yeh humare Class {grade} ke {subject} syllabus ka ek important topic hai. Chalo hum isko detail mein samjhte hain.",
            "board_text": f"• Topic: {topic.capitalize()}\n• Grade: Class {grade} ({subject})\n• Grounded in NCERT curriculum framework\n• Review the concept structure above",
            "hindi_text": f"एनसीईआरटी पाठ्यक्रम के अनुसार {topic} के बारे में आज की प्रस्तुति।",
            "visual_type": "svg",
            "visual_name": topic.lower(),
            "key_terms": [topic, "NCERT", "Classroom"],
            "ncert_ref": f"Class {grade} {subject}, Chapter 1"
        }

def get_mock_quiz(topic: str) -> list:
    """Offline fallback quiz questions."""
    t_lower = topic.lower()
    if "photo" in t_lower:
        return [
            {
                "q_en": "Q1. Photosynthesis process mein main food/energy product kya banta hai?",
                "q_hi": "Q1. प्रकाश संश्लेषण की प्रक्रिया में मुख्य भोजन/ऊर्जा उत्पाद क्या बनता है?",
                "options": {
                    "A": "Carbon Dioxide (CO₂)",
                    "B": "Glucose (C₆H₁₂O₆)",
                    "C": "Water (H₂O)",
                    "D": "Nitrogen"
                },
                "correct": "B"
            },
            {
                "q_en": "Q2. Plants solar energy ko trap karne ke liye kis green pigment ka use karte hain?",
                "q_hi": "Q2. पौधे सौर ऊर्जा को अवशोषित करने के लिए किस हरे वर्णक का उपयोग करते हैं?",
                "options": {
                    "A": "Hemoglobin",
                    "B": "Chlorophyll",
                    "C": "Melanin",
                    "D": "Carotene"
                },
                "correct": "B"
            },
            {
                "q_en": "Q3. Photosynthesis mein leaves air se kaun si gas absorb karti hain?",
                "q_hi": "Q3. प्रकाश संश्लेषण में पत्तियां हवा से कौन सी गैस अवशोषित करती हैं?",
                "options": {
                    "A": "Oxygen",
                    "B": "Nitrogen",
                    "C": "Carbon Dioxide (CO₂)",
                    "D": "Helium"
                },
                "correct": "C"
            },
            {
                "q_en": "Q4. Photosynthesis cell ke andar kis organelle mein perform hota hai?",
                "q_hi": "Q4. प्रकाश संश्लेषण कोशिका के किस अंग (organelle) में होता है?",
                "options": {
                    "A": "Mitochondria",
                    "B": "Nucleus",
                    "C": "Chloroplast",
                    "D": "Lysosome"
                },
                "correct": "C"
            },
            {
                "q_en": "Q5. Plants ko water aur minerals kis organ ke throw milte hain?",
                "q_hi": "Q5. पौधों को पानी और खनिज किस अंग के माध्यम से प्राप्त होते हैं?",
                "options": {
                    "A": "Leaves (पत्तियां)",
                    "B": "Stems (तना)",
                    "C": "Roots (जड़ें)",
                    "D": "Flowers (फूल)"
                },
                "correct": "C"
            }
        ]
    else:
        return [
            {
                "q_en": "Q1. What is the fundamental source of knowledge for this classroom?",
                "q_hi": "Q1. इस कक्षा के लिए ज्ञान का मौलिक स्रोत क्या है?",
                "options": {
                    "A": "NCERT Textbooks",
                    "B": "Random internet blogs",
                    "C": "Fictional magazines",
                    "D": "None of the above"
                },
                "correct": "A"
            },
            {
                "q_en": "Q2. How does Genius listen to the classroom queries?",
                "q_hi": "Q2. जीनियस कक्षा के प्रश्नों को कैसे सुनता है?",
                "options": {
                    "A": "Keyboard inputs only",
                    "B": "Hinglish Voice STT matching",
                    "C": "Reading thoughts",
                    "D": "Video camera analysis"
                },
                "correct": "B"
            },
            {
                "q_en": "Q3. Which font represents the board chalk headings?",
                "q_hi": "Q3. board par likhe mukhy sheershako ke liye kaun sa font hai?",
                "options": {
                    "A": "Outfit",
                    "B": "Patrick Hand",
                    "C": "Caveat",
                    "D": "Kalam"
                },
                "correct": "C"
            }
        ]
