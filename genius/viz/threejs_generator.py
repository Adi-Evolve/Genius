import os
import re
from pathlib import Path
from genius.ai.llm import get_groq_client

PROJECT_ROOT = Path(__file__).parent.parent.parent
CACHE_DIR = PROJECT_ROOT / "data" / "threejs_cache"

def slugify(text: str) -> str:
    """Converts text into a filename-safe format."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '_', text)
    return text

def generate_threejs_scene(topic: str) -> str:
    """Dynamically generates a Three.js scene using LLM, with file-caching.
    
    Acts as the self-learning mechanism where the 3D visual library grows.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_filename = f"{slugify(topic)}.html"
    cache_path = CACHE_DIR / cache_filename
    
    # 1. Check local cache
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                print(f"[ThreeJS Generator] Loading cached scene for '{topic}'")
                return f.read()
        except Exception as e:
            print(f"[ThreeJS Generator Cache Warning] Failed to read cache: {e}")

    # 2. Compile system guidelines for Three.js coding
    prompt = f"""Write a complete, single-file, self-contained HTML page that uses Three.js (r128) to visualize the Science/Mathematics topic: '{topic}'.
Include Three.js via CDN (https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js).
Set page background to transparent or deep blackboard green (#14260b).
Include simple, beautiful 3D animations representing the concept. Add a text label showing the title '{topic}'.

Rules for generation:
1. Output ONLY valid, clean HTML code containing standard tags, CSS styles, and a script tag.
2. DO NOT include any markdown formatting (like ```html or ```) in your output. Just start with <!DOCTYPE html> and end with </html>.
3. Keep geometries simple (cubes, spheres, cylinders, torus) with vibrant emissive phong/lambert colors.
4. Ensure the renderer automatically handles window resizing.
"""

    try:
        # Request completion from Groq LLM
        client = get_groq_client()
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert WebGL and Three.js developer. You write clean, valid, single-file HTML visualizations."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=2000
        )
        
        scene_html = completion.choices[0].message.content.strip()
        
        # Clean any accidental markdown wraps
        if scene_html.startswith("```html"):
            scene_html = scene_html[7:]
        if scene_html.endswith("```"):
            scene_html = scene_html[:-3]
        scene_html = scene_html.strip()
        
        # Verify it looks like HTML
        if not scene_html.lower().startswith("<!doctype html>") and "html" not in scene_html:
            raise ValueError("Generated code does not appear to be valid HTML.")
            
        # 3. Cache the result to grow the library
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(scene_html)
            
        print(f"[ThreeJS Generator] Cached new 3D scene for '{topic}'")
        return scene_html
        
    except Exception as e:
        print(f"[ThreeJS Generator Warning] Generation failed: {e}. Falling back to default geometric scene.")
        return get_default_geometric_scene(topic)

def get_default_geometric_scene(topic: str) -> str:
    """Generates a default rotating geometric grid fallback if LLM code generation fails."""
    fallback_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #14260b; color: #f5f2e8; font-family: sans-serif; }}
        canvas {{ display: block; }}
        #info {{ position: absolute; top: 10px; width: 100%; text-align: center; font-size: 1.1em; pointer-events: none; text-shadow: 1px 1px 2px black; }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="info">3D Model: {topic} (Geometric Fallback)</div>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        const light = new THREE.DirectionalLight(0xffffff, 1.5);
        light.position.set(5, 5, 5).normalize();
        scene.add(light);
        scene.add(new THREE.AmbientLight(0x404040));

        // Create a central sphere with rotating orbital rings
        const geometry = new THREE.SphereGeometry(2, 32, 32);
        const material = new THREE.MeshPhongMaterial({{ color: 0x4caf50, wireframe: true }});
        const sphere = new THREE.Mesh(geometry, material);
        scene.add(sphere);

        const torusGeo = new THREE.TorusGeometry(3.5, 0.15, 8, 64);
        const torusMat = new THREE.MeshPhongMaterial({{ color: 0xffd700, emissive: 0x554400 }});
        const ring1 = new THREE.Mesh(torusGeo, torusMat);
        const ring2 = new THREE.Mesh(torusGeo, torusMat);
        ring2.rotation.x = Math.PI / 3;
        scene.add(ring1);
        scene.add(ring2);

        camera.position.z = 8;

        function animate() {{
            requestAnimationFrame(animate);
            sphere.rotation.y += 0.01;
            sphere.rotation.x += 0.005;
            ring1.rotation.z += 0.015;
            ring2.rotation.y -= 0.01;
            renderer.render(scene, camera);
        }}

        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});

        animate();
    </script>
</body>
</html>
"""
    return fallback_html
