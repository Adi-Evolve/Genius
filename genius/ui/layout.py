import streamlit as st
import streamlit.components.v1 as components
import os

def render_layout():
    """Renders the self-contained Genius Single Page HTML App inside Streamlit."""
    
    # Load index.html
    ui_dir = os.path.dirname(__file__)
    html_path = os.path.join(ui_dir, "index.html")
    
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    # Inject styling in the parent Streamlit container to make the iframe completely full-viewport
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            header, [data-testid="stHeader"] {
                visibility: hidden !important;
                display: none !important;
                height: 0px !important;
                min-height: 0px !important;
                margin: 0px !important;
                padding: 0px !important;
            }
            footer {visibility: hidden;}
            div[data-testid="stDecoration"] {display: none;}
            [data-testid="collapsedControl"] {display: none !important;}
            
            /* Reset all margins and paddings globally in Streamlit parent */
            html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"], .main, .block-container, [data-testid="stVerticalBlock"], [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stHtml"] {
                margin: 0 !important;
                padding: 0 !important;
                top: 0 !important;
                gap: 0 !important;
            }
            
            iframe[title="streamlit_html_container"] {
                width: 100vw !important;
                height: 100vh !important;
                border: none !important;
                display: block !important;
                margin: 0 !important;
                padding: 0 !important;
            }
        </style>
        <script>
            function patchIframes() {
                const iframes = document.getElementsByTagName('iframe');
                for (let i = 0; i < iframes.length; i++) {
                    const iframe = iframes[i];
                    if (!iframe.getAttribute('allow') || !iframe.getAttribute('allow').includes('microphone')) {
                        iframe.setAttribute('allow', 'microphone');
                        console.log("[Genius Parent] Patched iframe microphone permission.");
                    }
                }
            }
            patchIframes();
            // Periodically check in case Streamlit redraws the components
            setInterval(patchIframes, 1000);
        </script>
    """, unsafe_allow_html=True)

    
    # Display the HTML app inside a large iframe
    components.html(html_content, height=1000, scrolling=True)

