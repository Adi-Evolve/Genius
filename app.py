import sys
import os
import asyncio

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import streamlit as st
from genius.state import init_state
from genius.ui.landing import render_landing
from genius.ui.layout import render_layout

# Page configuration
st.set_page_config(
    page_title="Genius — Voice AI Teaching Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize application state
init_state()

def inject_global_styles():
    """Utility to inject basic CSS variables and layout configurations on page load."""
    css_files = [
        "static/css/tokens.css",
        "static/css/fonts.css",
        "static/css/layout.css",
        "static/css/animations.css"
    ]
    combined_css = ""
    for path in css_files:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    combined_css += f.read()
            except Exception as e:
                print(f"Error loading CSS in root: {e}")
    st.markdown(f"<style>{combined_css}</style>", unsafe_allow_html=True)

# Inject base styles
inject_global_styles()

# Routing logic based on application mode
if st.session_state.current_mode == "idle":
    render_landing()
else:
    render_layout()
