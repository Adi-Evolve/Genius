import os
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
LOGS_DIR = PROJECT_ROOT / "data" / "session_logs"

def get_log_filepath(grade: str, subject: str) -> Path:
    """Gets the file path for saving class adaptive profiles."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    filename = f"class_{grade}_{subject.lower().replace(' ', '_')}_profile.json"
    return LOGS_DIR / filename

def load_adaptive_profile(grade: str, subject: str) -> dict:
    """Loads the class adaptive profile from disk, creating a default profile if it doesn't exist."""
    path = get_log_filepath(grade, subject)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Adaptive Log Warning] Failed to load profile: {e}")
            
    # Default Profile Structure
    return {
        "grade": grade,
        "subject": subject,
        "history": [], # list of {topic, date, score_pct, style_used}
        "preferred_style": "story-first", # story-first | diagram-first | formula-first
        "style_performances": {
            "story-first": [],
            "diagram-first": [],
            "formula-first": []
        }
    }

def save_adaptive_profile(profile: dict, grade: str, subject: str):
    """Saves the class adaptive profile to disk."""
    path = get_log_filepath(grade, subject)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2)
    except Exception as e:
        print(f"[Adaptive Log Error] Failed to write profile: {e}")

def record_session_performance(grade: str, subject: str, topic: str, score_pct: float, style_used: str):
    """Records a single topic performance and recalculates the class preferred explanation style."""
    profile = load_adaptive_profile(grade, subject)
    
    # 1. Append to history
    profile["history"].append({
        "topic": topic,
        "score_pct": score_pct,
        "style_used": style_used
    })
    
    # 2. Append score to style tracker
    if style_used in profile["style_performances"]:
        profile["style_performances"][style_used].append(score_pct)
        
    # 3. Recalculate preferred style (Contextual bandit approach: choose style with highest average score)
    best_style = "story-first"
    best_avg = -1.0
    
    for style, scores in profile["style_performances"].items():
        if scores:
            avg = sum(scores) / len(scores)
            if avg > best_avg:
                best_avg = avg
                best_style = style
                
    profile["preferred_style"] = best_style
    save_adaptive_profile(profile, grade, subject)
    print(f"[Adaptive Engine] Updated profile. Recommended style is now: '{best_style}'")
    return best_style
