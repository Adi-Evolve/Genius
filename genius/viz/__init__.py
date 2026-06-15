# Genius Visualization Engine
from genius.viz.phet_mapper import get_phet_url
from genius.viz.threejs_scenes import get_prebuilt_scene
from genius.viz.threejs_generator import generate_threejs_scene
from genius.viz.diagram_builder import generate_svg_diagram

def get_visualization_html(topic: str, spec_type: str = None) -> tuple[str, str]:
    """Resolves and returns the HTML container and type of visualization for the given topic.
    
    Tries PhET -> Prebuilt Three.js -> Dynamic Three.js -> SVG Fallback.
    Returns:
        tuple: (html_content_string, resolved_type)
    """
    topic_clean = topic.lower().strip()
    
    # 1. Force PhET if specified or has matching URL
    phet_url = get_phet_url(topic_clean)
    if spec_type == "phet" or (spec_type is None and phet_url):
        if phet_url:
            iframe_html = f'<iframe src="{phet_url}" width="100%" height="380px" style="border:none; background:#14260b; border-radius:8px;"></iframe>'
            return iframe_html, "phet"
            
    # 2. Try Prebuilt Three.js Scene
    prebuilt_html = get_prebuilt_scene(topic_clean)
    if spec_type == "threejs" or (spec_type is None and prebuilt_html):
        if prebuilt_html:
            iframe_html = f'<iframe srcdoc="{prebuilt_html.replace('"', '&quot;')}" width="100%" height="380px" style="border:none; background:#14260b; border-radius:8px;"></iframe>'
            return iframe_html, "threejs"
            
    # 3. Try Dynamic Three.js Generation
    try:
        generated_html = generate_threejs_scene(topic_clean)
        if generated_html:
            iframe_html = f'<iframe srcdoc="{generated_html.replace('"', '&quot;')}" width="100%" height="380px" style="border:none; background:#14260b; border-radius:8px;"></iframe>'
            return iframe_html, "threejs_dynamic"
    except Exception as e:
        print(f"[Viz Init Warning] Dynamic Three.js generation failed: {e}")
        
    # 4. Fallback to 2D SVG Diagram
    svg_html = generate_svg_diagram(topic_clean)
    return svg_html, "svg"
