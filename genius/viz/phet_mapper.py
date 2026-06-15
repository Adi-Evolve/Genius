# Mappings of Science/Math concepts to official HTML5 PhET simulations

PHET_MAP = {
    "states of matter": "https://phet.colorado.edu/sims/html/states-of-matter/latest/states-of-matter_all.html",
    "solid liquid gas": "https://phet.colorado.edu/sims/html/states-of-matter/latest/states-of-matter_all.html",
    "atomic structure": "https://phet.colorado.edu/sims/html/build-an-atom/latest/build-an-atom_all.html",
    "atom builder": "https://phet.colorado.edu/sims/html/build-an-atom/latest/build-an-atom_all.html",
    "circuits": "https://phet.colorado.edu/sims/html/circuit-construction-kit-dc/latest/circuit-construction-kit-dc_all.html",
    "electricity": "https://phet.colorado.edu/sims/html/circuit-construction-kit-dc/latest/circuit-construction-kit-dc_all.html",
    "current electricity": "https://phet.colorado.edu/sims/html/circuit-construction-kit-dc/latest/circuit-construction-kit-dc_all.html",
    "wave": "https://phet.colorado.edu/sims/html/wave-interference/latest/wave-interference_all.html",
    "waves": "https://phet.colorado.edu/sims/html/wave-interference/latest/wave-interference_all.html",
    "wave interference": "https://phet.colorado.edu/sims/html/wave-interference/latest/wave-interference_all.html",
    "acid base": "https://phet.colorado.edu/sims/html/acid-base-solutions/latest/acid-base-solutions_all.html",
    "acids and bases": "https://phet.colorado.edu/sims/html/acid-base-solutions/latest/acid-base-solutions_all.html",
    "projectile motion": "https://phet.colorado.edu/sims/html/projectile-motion/latest/projectile-motion_all.html",
    "gravity": "https://phet.colorado.edu/sims/html/gravity-force-lab-basics/latest/gravity-force-lab-basics_all.html",
    "gravitation": "https://phet.colorado.edu/sims/html/gravity-force-lab-basics/latest/gravity-force-lab-basics_all.html",
    "friction": "https://phet.colorado.edu/sims/html/friction/latest/friction_all.html",
    "forces and motion": "https://phet.colorado.edu/sims/html/forces-and-motion-basics/latest/forces-and-motion-basics_all.html",
    "force": "https://phet.colorado.edu/sims/html/forces-and-motion-basics/latest/forces-and-motion-basics_all.html",
    "pendulum": "https://phet.colorado.edu/sims/html/pendulum-lab/latest/pendulum-lab_all.html",
    "greenhouse effect": "https://phet.colorado.edu/sims/html/greenhouse-effect/latest/greenhouse-effect_all.html",
    "ohms law": "https://phet.colorado.edu/sims/html/ohms-law/latest/ohms-law_all.html",
    "ohm's law": "https://phet.colorado.edu/sims/html/ohms-law/latest/ohms-law_all.html"
}

def get_phet_url(topic: str) -> str:
    """Finds a matching PhET simulator URL for the given query topic.
    
    Returns None if no match is found.
    """
    topic_clean = topic.lower().strip()
    
    # Direct match check
    if topic_clean in PHET_MAP:
        return PHET_MAP[topic_clean]
        
    # Keyword/substring match check
    for keyword, url in PHET_MAP.items():
        if keyword in topic_clean:
            return url
            
    return None
