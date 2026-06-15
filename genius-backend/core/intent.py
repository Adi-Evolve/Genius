def classify_intent(text: str) -> tuple[str, str]:
    """Classifies transcription text into intents and extracts the topic if applicable.
    
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
