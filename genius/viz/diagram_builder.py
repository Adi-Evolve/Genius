# 2D SVG fallback diagrams for Genius classrooms (Science/Mathematics)

def generate_svg_diagram(topic: str) -> str:
    """Generates an inline SVG diagram based on the topic.
    
    Serves as the Tier 3 lightweight visual fallback.
    """
    topic_clean = topic.lower().strip()
    
    if any(keyword in topic_clean for keyword in ["triangle", "right triangle", "trigonometry"]):
        return get_right_triangle_svg()
    elif any(keyword in topic_clean for keyword in ["circle", "radius", "diameter", "circumference"]):
        return get_circle_geometry_svg()
    elif any(keyword in topic_clean for keyword in ["graph", "coordinate", "x axis", "y axis", "cartesian"]):
        return get_coordinate_plane_svg()
    else:
        return get_concept_block_svg(topic)

def get_right_triangle_svg() -> str:
    return """
    <div style="text-align: center; background: rgba(0, 0, 0, 0.2); padding: 20px; border-radius: 8px;">
        <svg width="300" height="240" viewBox="0 0 300 240" xmlns="http://www.w3.org/2000/svg" style="color: #f5f2e8;">
            <!-- Triangle path -->
            <path d="M 50,50 L 50,200 L 250,200 Z" fill="none" stroke="var(--color-chalk-white)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <!-- Right angle indicator -->
            <path d="M 50,185 L 65,185 L 65,200" fill="none" stroke="var(--color-chalk-yellow)" stroke-width="2"/>
            <!-- Labels -->
            <text x="35" y="125" fill="var(--color-chalk-white)" font-family="cursive" font-size="18">Perpendicular (p)</text>
            <text x="135" y="220" fill="var(--color-chalk-white)" font-family="cursive" font-size="18">Base (b)</text>
            <text x="160" y="110" fill="var(--color-chalk-yellow)" font-family="cursive" font-size="18">Hypotenuse (h)</text>
            <text x="35" y="210" fill="var(--color-chalk-white)" font-family="sans-serif" font-size="14">A</text>
            <text x="35" y="45" fill="var(--color-chalk-white)" font-family="sans-serif" font-size="14">B</text>
            <text x="255" y="210" fill="var(--color-chalk-white)" font-family="sans-serif" font-size="14">C</text>
        </svg>
        <div style="font-family: var(--font-ui-label); color: var(--color-chalk-yellow); margin-top: 10px; font-size: 1.2rem;">
            Pythagoras Theorem: h² = p² + b²
        </div>
    </div>
    """

def get_circle_geometry_svg() -> str:
    return """
    <div style="text-align: center; background: rgba(0, 0, 0, 0.2); padding: 20px; border-radius: 8px;">
        <svg width="300" height="240" viewBox="0 0 300 240" xmlns="http://www.w3.org/2000/svg" style="color: #f5f2e8;">
            <!-- Outer Circle -->
            <circle cx="150" cy="120" r="80" fill="none" stroke="var(--color-chalk-white)" stroke-width="3"/>
            <!-- Center point -->
            <circle cx="150" cy="120" r="4" fill="var(--color-chalk-yellow)"/>
            <!-- Radius line -->
            <line x1="150" y1="120" x2="230" y2="120" stroke="var(--color-chalk-yellow)" stroke-width="2" stroke-linecap="round"/>
            <!-- Diameter line -->
            <line x1="70" y1="120" x2="150" y2="120" stroke="var(--color-chalk-blue)" stroke-width="2" stroke-dasharray="4 4"/>
            <!-- Labels -->
            <text x="180" y="110" fill="var(--color-chalk-yellow)" font-family="cursive" font-size="16">Radius (r)</text>
            <text x="80" y="140" fill="var(--color-chalk-blue)" font-family="cursive" font-size="14">Diameter (d = 2r)</text>
            <text x="145" y="140" fill="var(--color-chalk-yellow)" font-family="sans-serif" font-size="14">O</text>
        </svg>
        <div style="font-family: var(--font-ui-label); color: var(--color-chalk-yellow); margin-top: 10px; font-size: 1.2rem;">
            Area = πr² | Circumference = 2πr
        </div>
    </div>
    """

def get_coordinate_plane_svg() -> str:
    return """
    <div style="text-align: center; background: rgba(0, 0, 0, 0.2); padding: 20px; border-radius: 8px;">
        <svg width="320" height="240" viewBox="0 0 320 240" xmlns="http://www.w3.org/2000/svg" style="color: #f5f2e8;">
            <!-- Grid Lines -->
            <line x1="0" y1="120" x2="320" y2="120" stroke="rgba(245,242,232,0.4)" stroke-width="2"/>
            <line x1="160" y1="0" x2="160" y2="240" stroke="rgba(245,242,232,0.4)" stroke-width="2"/>
            <!-- Arrowheads -->
            <path d="M 315,115 L 320,120 L 315,125" fill="none" stroke="rgba(245,242,232,0.6)" stroke-width="2"/>
            <path d="M 155,5 L 160,0 L 165,5" fill="none" stroke="rgba(245,242,232,0.6)" stroke-width="2"/>
            <!-- Linear graph plot: y = x + 20 -->
            <line x1="40" y1="200" x2="280" y2="40" stroke="var(--color-chalk-yellow)" stroke-width="3" stroke-linecap="round"/>
            <!-- Text markings -->
            <text x="305" y="140" fill="var(--color-chalk-white)" font-family="sans-serif" font-size="14">X</text>
            <text x="170" y="15" fill="var(--color-chalk-white)" font-family="sans-serif" font-size="14">Y</text>
            <text x="145" y="135" fill="var(--color-chalk-white)" font-family="sans-serif" font-size="12">0</text>
            <!-- Plotted equation text -->
            <text x="190" y="70" fill="var(--color-chalk-yellow)" font-family="cursive" font-size="16">y = mx + c</text>
        </svg>
    </div>
    """

def get_concept_block_svg(topic: str) -> str:
    return f"""
    <div style="text-align: center; background: rgba(0, 0, 0, 0.2); padding: 30px; border-radius: 8px;">
        <svg width="400" height="200" viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg" style="color: #f5f2e8;">
            <!-- Three blocks representing a process flow -->
            <rect x="20" y="60" width="100" height="80" rx="4" fill="none" stroke="var(--color-chalk-white)" stroke-width="2"/>
            <rect x="150" y="60" width="100" height="80" rx="4" fill="none" stroke="var(--color-chalk-yellow)" stroke-width="2"/>
            <rect x="280" y="60" width="100" height="80" rx="4" fill="none" stroke="var(--color-chalk-white)" stroke-width="2"/>
            <!-- Connecting Arrows -->
            <path d="M 125,100 L 145,100 M 140,95 L 145,100 L 140,105" fill="none" stroke="var(--color-chalk-white)" stroke-width="2"/>
            <path d="M 255,100 L 275,100 M 270,95 L 275,100 L 270,105" fill="none" stroke="var(--color-chalk-white)" stroke-width="2"/>
            <!-- Text inside blocks -->
            <text x="70" y="105" text-anchor="middle" fill="var(--color-chalk-white)" font-family="sans-serif" font-size="14">Input</text>
            <text x="200" y="100" text-anchor="middle" fill="var(--color-chalk-yellow)" font-family="sans-serif" font-size="14">Process</text>
            <text x="200" y="120" text-anchor="middle" fill="var(--color-chalk-yellow)" font-family="sans-serif" font-size="11">({topic[:10]})</text>
            <text x="330" y="105" text-anchor="middle" fill="var(--color-chalk-white)" font-family="sans-serif" font-size="14">Output</text>
        </svg>
    </div>
    """
