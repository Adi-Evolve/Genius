import streamlit as st

def init_state():
    """Initializes session state defaults for the Genius app."""
    defaults = {
        "current_mode": "idle",          # idle | explaining | quizzing | dictating | activity | summary | settings
        "session_topic": None,           # current topic being taught
        "class_grade": "9",              # current grade level (6-12)
        "subject": "Science",            # Science | Mathematics | English | etc.
        "language": "Hinglish",          # Hinglish | Hindi | English
        "quiz_scores": [],               # list of scores from quizzes taken
        "transcript": [],                # list of spoken transcript dialogues {role, text}
        "audio_ready": False,            # whether output voice audio is ready to play
        "tts_cache": {},                 # text -> base64 audio cache
        "viz_cache": {},                 # topic -> visualization html cache
        "board_html": None,              # HTML string of content on the board
        "current_explanation": None,     # dict containing LLM output (board_text, spoken_text, visual_spec, key_terms, etc.)
        "quiz_questions": [],            # list of questions generated for the current topic
        "current_question_idx": 0,       # current index of the active quiz question
        "quiz_responses": {},            # user/class answers for each question idx
        "adaptive_profile": {            # class section history bandit profile
            "style_preference": "story-first",
            "weak_topics": [],
            "strong_topics": [],
            "performance_logs": []
        },
        "student_count": 30,             # default number of students
        "school_name": "Govt High School, Haryana", # default school name
        "voice_speaking": False,         # TTS playback status
        "voice_recording": False,        # STT recording status
        "user_input_text": "",           # text backup input
        "stt_transcription": "",         # result from STT
        "history": [],                   # history of topics taught in this session
        "sidebar_collapsed": False       # UI state helper
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_session_state():
    """Resets key learning-specific states while keeping settings/profile."""
    keys_to_reset = [
        "current_mode", "session_topic", "audio_ready", "board_html", 
        "current_explanation", "quiz_questions", "current_question_idx", 
        "quiz_responses", "voice_speaking", "voice_recording", 
        "user_input_text", "stt_transcription"
    ]
    for key in keys_to_reset:
        st.session_state[key] = None
    
    st.session_state.current_mode = "idle"
    st.session_state.quiz_questions = []
    st.session_state.quiz_responses = {}
    st.session_state.quiz_scores = []
    st.session_state.transcript = []
