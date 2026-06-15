# Self-contained HTML/JS Three.js 3D scenes for NCERT science topics

SCENE_BASE_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #14260b; color: #f5f2e8; font-family: sans-serif; }}
        canvas {{ display: block; }}
        #info {{ position: absolute; top: 10px; width: 100%; text-align: center; font-size: 1.1em; text-shadow: 1px 1px 2px black; pointer-events: none; }}
    </style>
    <!-- Include Three.js and OrbitControls -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="info">{title}</div>
    <script>
        {scene_code}
    </script>
</body>
</html>
"""

# 1. DNA Double Helix Scene Code
DNA_CODE = """
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Lights
const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
scene.add(ambientLight);
const pointLight = new THREE.PointLight(0xfff3a0, 1.2);
pointLight.position.set(10, 20, 15);
scene.add(pointLight);

// DNA Parameters
const numPoints = 35;
const r = 4;
const twist = 0.5;
const verticalSpacing = 0.45;

const group = new THREE.Group();

// Colors for Base Pairs (Adenine, Thymine, Guanine, Cytosine)
const colors = [0xff5050, 0x50ff50, 0x5050ff, 0xffff50]; 

// Create nucleotides (spheres) and backbone connections
const spheres = [];
for (let i = 0; i < numPoints; i++) {
    const angle = i * twist;
    const y = (i - numPoints/2) * verticalSpacing;
    
    // Strand 1
    const x1 = Math.cos(angle) * r;
    const z1 = Math.sin(angle) * r;
    
    // Strand 2 (180 degrees offset)
    const x2 = Math.cos(angle + Math.PI) * r;
    const z2 = Math.sin(angle + Math.PI) * r;
    
    // Backbone spheres
    const s1Geo = new THREE.SphereGeometry(0.3, 16, 16);
    const s1Mat = new THREE.MeshPhongMaterial({ color: 0xffffff, emissive: 0x222222 });
    const s1 = new THREE.Mesh(s1Geo, s1Mat);
    s1.position.set(x1, y, z1);
    group.add(s1);
    
    const s2 = new THREE.Mesh(s1Geo, s1Mat);
    s2.position.set(x2, y, z2);
    group.add(s2);
    
    // Rungs (horizontal base connections)
    const colorIndex = i % 4;
    const rungGeo = new THREE.CylinderGeometry(0.08, 0.08, r * 2, 8);
    // Cylinder is default centered on origin, rotate it and position
    const rungMat = new THREE.MeshPhongMaterial({ color: colors[colorIndex] });
    const rung = new THREE.Mesh(rungGeo, rungMat);
    rung.position.set(0, y, 0);
    rung.rotation.z = angle + Math.PI/2;
    group.add(rung);
}

scene.add(group);
camera.position.z = 15;

// Animation Loop
function animate() {
    requestAnimationFrame(animate);
    group.rotation.y += 0.012;
    group.rotation.x = Math.sin(Date.now() * 0.0005) * 0.2;
    renderer.render(scene, camera);
}

window.addEventListener('resize', onWindowResize, false);
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

animate();
"""

# 2. Photosynthesis Conversion Scene Code
PHOTOSYNTHESIS_CODE = """
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Ambient and directional lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
scene.add(ambientLight);
const sunLight = new THREE.PointLight(0xffd700, 1.8, 100);
sunLight.position.set(15, 20, 10);
scene.add(sunLight);

// Chloroplast (central factory)
const factoryGeo = new THREE.TorusGeometry(3.5, 1.2, 16, 100);
const factoryMat = new THREE.MeshPhongMaterial({ color: 0x4caf50, wireframe: true });
const chloroplast = new THREE.Mesh(factoryGeo, factoryMat);
scene.add(chloroplast);

// Internal chloroplast coin (thylakoid stacking)
const coinGeo = new THREE.CylinderGeometry(1.5, 1.5, 0.4, 32);
const coinMat = new THREE.MeshPhongMaterial({ color: 0x1b5e20 });
const coins = new THREE.Group();
for (let i = 0; i < 4; i++) {
    const coin = new THREE.Mesh(coinGeo, coinMat);
    coin.position.y = (i - 1.5) * 0.5;
    coins.add(coin);
}
scene.add(coins);

// Floating particles
const particles = [];
const particleCount = 40;

// Helper to spawn inputs (Water = Blue, CO2 = Grey) and outputs (Oxygen = Red, Glucose = Gold)
for (let i = 0; i < particleCount; i++) {
    const isInput = i < particleCount / 2;
    const type = Math.random() > 0.5 ? 'A' : 'B'; // H2O/CO2 or O2/C6H12O6
    
    let color = 0x00aaff; // Blue (H2O)
    if (isInput && type === 'B') color = 0x888888; // Grey (CO2)
    if (!isInput && type === 'A') color = 0xff3333; // Red (Oxygen)
    if (!isInput && type === 'B') color = 0xffd700; // Gold (Glucose)
    
    const size = isInput ? 0.15 : 0.25;
    const geo = new THREE.SphereGeometry(size, 8, 8);
    const mat = new THREE.MeshPhongMaterial({ color: color, emissive: color, emissiveIntensity: 0.5 });
    const mesh = new THREE.Mesh(geo, mat);
    
    // Initial random positions
    resetParticle(mesh, isInput);
    scene.add(mesh);
    
    particles.push({
        mesh: mesh,
        isInput: isInput,
        speed: 0.02 + Math.random() * 0.03,
        type: type
    });
}

function resetParticle(mesh, isInput) {
    const theta = Math.random() * Math.PI * 2;
    const r = 8 + Math.random() * 4;
    
    if (isInput) {
        // start far, move in
        mesh.position.set(Math.cos(theta) * r, (Math.random() - 0.5) * 5, Math.sin(theta) * r);
    } else {
        // start at chloroplast, move out
        mesh.position.set((Math.random() - 0.5) * 2, (Math.random() - 0.5) * 2, (Math.random() - 0.5) * 2);
    }
}

camera.position.z = 12;

function animate() {
    requestAnimationFrame(animate);
    
    chloroplast.rotation.z += 0.005;
    chloroplast.rotation.y += 0.003;
    coins.rotation.y -= 0.01;
    
    // Animate particles
    particles.forEach(p => {
        if (p.isInput) {
            // Move toward center
            const dir = new THREE.Vector3(0, p.mesh.position.y, 0).sub(p.mesh.position).normalize();
            p.mesh.position.addScaledVector(dir, p.speed);
            
            // If close to center, reset
            if (p.mesh.position.length() < 2) {
                resetParticle(p.mesh, true);
            }
        } else {
            // Move outward
            const dir = new THREE.Vector3(p.mesh.position.x, p.mesh.position.y, p.mesh.position.z).normalize();
            // If zero vector, offset
            if (dir.length() === 0) dir.x = 1;
            p.mesh.position.addScaledVector(dir, p.speed);
            
            // If far, reset
            if (p.mesh.position.length() > 12) {
                resetParticle(p.mesh, false);
            }
        }
    });
    
    renderer.render(scene, camera);
}

window.addEventListener('resize', onWindowResize, false);
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

animate();
"""

# 3. Bohr Atomic Bohr Model Scene Code
ATOM_CODE = """
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Lights
const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
scene.add(ambientLight);
const light = new THREE.PointLight(0xffffff, 1.5);
light.position.set(5, 10, 10);
scene.add(light);

// Nucleus (protons = red, neutrons = blue)
const nucleusGroup = new THREE.Group();
const particleGeo = new THREE.SphereGeometry(0.4, 16, 16);
const protonMat = new THREE.MeshPhongMaterial({ color: 0xff3333 });
const neutronMat = new THREE.MeshPhongMaterial({ color: 0x3333ff });

// Create clustered spheres
for (let i = 0; i < 14; i++) {
    const mat = i % 2 === 0 ? protonMat : neutronMat;
    const sphere = new THREE.Mesh(particleGeo, mat);
    // Random tight offset
    const r = 0.5 + Math.random() * 0.4;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos((Math.random() * 2) - 1);
    
    sphere.position.set(
        Math.sin(phi) * Math.cos(theta) * r,
        Math.sin(phi) * Math.sin(theta) * r,
        Math.cos(phi) * r
    );
    nucleusGroup.add(sphere);
}
scene.add(nucleusGroup);

// Electrons in orbits
const orbits = [
    { radius: 3, speed: 0.04, color: 0xffff33, count: 2 },
    { radius: 5.5, speed: 0.025, color: 0xffff33, count: 4 }
];

const electrons = [];
const orbitLines = new THREE.Group();

orbits.forEach(o => {
    // Draw orbital path line (dashed ring)
    const ringGeo = new THREE.RingGeometry(o.radius - 0.02, o.radius + 0.02, 64);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0xaaaaaa, side: THREE.DoubleSide, opacity: 0.4, transparent: true });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = Math.PI / 2; // Flat on XZ plane
    orbitLines.add(ring);
    
    // Add electrons (yellow spheres)
    const eGeo = new THREE.SphereGeometry(0.2, 16, 16);
    const eMat = new THREE.MeshPhongMaterial({ color: o.color, emissive: o.color, emissiveIntensity: 0.5 });
    
    for (let c = 0; c < o.count; c++) {
        const e = new THREE.Mesh(eGeo, eMat);
        const offset = (Math.PI * 2 / o.count) * c;
        scene.add(e);
        electrons.push({
            mesh: e,
            radius: o.radius,
            speed: o.speed,
            offset: offset,
            angle: 0
        });
    }
});

scene.add(orbitLines);
camera.position.set(0, 6, 10);
camera.lookAt(0, 0, 0);

function animate() {
    requestAnimationFrame(animate);
    
    // Rotate nucleus slightly
    nucleusGroup.rotation.y += 0.005;
    nucleusGroup.rotation.x += 0.003;
    
    // Animate electrons along orbital radii
    const time = Date.now() * 0.001;
    electrons.forEach((e, idx) => {
        e.angle = time * e.speed + e.offset;
        
        // Inclined orbits look cooler
        const tiltX = idx % 2 === 0 ? 0.2 : -0.2;
        const tiltZ = idx % 2 === 0 ? -0.1 : 0.1;
        
        const x = Math.cos(e.angle) * e.radius;
        const z = Math.sin(e.angle) * e.radius;
        
        e.mesh.position.set(x, x * tiltX + z * tiltZ, z);
    });
    
    renderer.render(scene, camera);
}

window.addEventListener('resize', onWindowResize, false);
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

animate();
"""

PREBUILT_SCENES = {
    "dna": {
        "title": "3D DNA Double Helix (गुणसूत्र/डीएनए)",
        "code": DNA_CODE
    },
    "photosynthesis": {
        "title": "Chloroplast Photosynthesis Process (प्रकाश संश्लेषण)",
        "code": PHOTOSYNTHESIS_CODE
    },
    "atomic structure": {
        "title": "Carbon Bohr Atom Model (परमाणु संरचना)",
        "code": ATOM_CODE
    },
    "atom": {
        "title": "Carbon Bohr Atom Model (परमाणु संरचना)",
        "code": ATOM_CODE
    }
}

def get_prebuilt_scene(name: str) -> str:
    """Retrieves the full HTML string for a prebuilt Three.js scene by name.
    
    Returns None if the scene is not found in the dictionary.
    """
    clean_name = name.lower().strip()
    
    # Substring checks
    matched_key = None
    for key in PREBUILT_SCENES.keys():
        if key in clean_name:
            matched_key = key
            break
            
    if matched_key:
        scene_data = PREBUILT_SCENES[matched_key]
        return SCENE_BASE_TEMPLATE.format(
            title=scene_data["title"],
            scene_code=scene_data["code"]
        )
    return None
