"""
MediRisk AI - 3D Floating Cardiovascular Risk Intelligence
Streamlit Application
"""

import datetime
import json
import math
import os
import time
import requests
import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# 0. CONFIGURATION & STREAMLIT SETUP
# ==============================================================================
st.set_page_config(
    page_title="MediRisk AI — Cardiovascular Risk Intelligence",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_BASE_URL = os.environ.get("MEDIRISK_API_URL", "http://127.0.0.1:8000")

def render_floating_html(html_str: str):
    """
    Renders custom HTML/SVG in Streamlit cleanly without triggering Markdown's
    indented code block parser. Strips all leading indentation from every line
    and eliminates empty lines that cause CommonMark to fall back to code blocks.
    """
    cleaned = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


# ==============================================================================
# 1. CORE CSS & FLOATING OBJECT SYSTEM
# ==============================================================================
FLOATING_SYSTEM_CSS = """
<style>
/* Import premium typography */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Reset and dotted background */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #FBFBF9 !important;
    background-image: radial-gradient(rgba(17, 17, 17, 0.08) 1.2px, transparent 1.2px) !important;
    background-size: 28px 28px !important;
    color: #111111 !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    overflow-x: hidden !important;
}

/* Remove default streamlit paddings */
header[data-testid="stHeader"] {
    display: none !important;
}
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 6rem !important;
    max-width: 1400px !important;
}
footer {
    display: none !important;
}

/* Typography styles */
.mono-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #777777;
}
.mono-tag-red {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #FF3B30;
}

/* Ambient technical background markers */
.bg-tech-marker {
    position: fixed;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: rgba(0, 0, 0, 0.18);
    pointer-events: none;
    user-select: none;
    z-index: 1;
    letter-spacing: 0.12em;
}

/* =====================================================================
   CORE FLOATING OBJECT SYSTEM
   ===================================================================== */
.floating-object {
    position: relative;
    transform: perspective(1200px) rotateX(2deg) rotateY(-3deg) translateZ(30px);
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.10), 0 10px 30px rgba(0, 0, 0, 0.04);
    border-radius: 28px;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid rgba(255, 255, 255, 0.95);
    transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.6s ease;
    z-index: 10;
}

.floating-object:hover {
    transform: perspective(1200px) rotateX(0deg) rotateY(0deg) translateY(-14px) translateZ(60px);
    box-shadow: 0 45px 100px rgba(0, 0, 0, 0.18), 0 15px 35px rgba(0, 0, 0, 0.06);
}

/* Floating animation cadences (independent speeds) */
@keyframes float-1 {
    0%, 100% { transform: perspective(1200px) rotateX(1.8deg) rotateY(-2.5deg) translateY(0px) translateZ(28px); }
    50% { transform: perspective(1200px) rotateX(0.8deg) rotateY(-1.2deg) translateY(-12px) translateZ(42px); }
}
@keyframes float-2 {
    0%, 100% { transform: perspective(1200px) rotateX(-2deg) rotateY(2deg) translateY(0px) translateZ(24px); }
    50% { transform: perspective(1200px) rotateX(-0.8deg) rotateY(0.8deg) translateY(-15px) translateZ(38px); }
}
@keyframes float-3 {
    0%, 100% { transform: perspective(1200px) rotateX(1.5deg) rotateY(2deg) translateY(0px) translateZ(32px); }
    50% { transform: perspective(1200px) rotateX(0.5deg) rotateY(1deg) translateY(-10px) translateZ(45px); }
}
@keyframes float-4 {
    0%, 100% { transform: perspective(1200px) rotateX(-1.2deg) rotateY(-2deg) translateY(0px) translateZ(20px); }
    50% { transform: perspective(1200px) rotateX(0deg) rotateY(-0.8deg) translateY(-14px) translateZ(34px); }
}
@keyframes float-5 {
    0%, 100% { transform: perspective(1200px) rotateX(2.2deg) rotateY(-1.5deg) translateY(0px) translateZ(30px); }
    50% { transform: perspective(1200px) rotateX(1deg) rotateY(-0.5deg) translateY(-11px) translateZ(44px); }
}

.float-anim-6s { animation: float-1 6s ease-in-out infinite; }
.float-anim-7s { animation: float-2 7s ease-in-out infinite; }
.float-anim-8s { animation: float-3 8.5s ease-in-out infinite; }
.float-anim-10s { animation: float-4 10s ease-in-out infinite; }
.float-anim-9s { animation: float-5 9s ease-in-out infinite; }

/* Physical soft floor shadow underneath floating objects */
.floating-floor-shadow {
    width: 70%;
    height: 22px;
    margin: 18px auto 0;
    background: radial-gradient(ellipse at center, rgba(0, 0, 0, 0.16) 0%, rgba(0, 0, 0, 0.04) 50%, transparent 75%);
    border-radius: 50%;
    filter: blur(8px);
    transition: transform 0.6s ease, opacity 0.6s ease;
}

/* Glass panel inner padding */
.floating-inner {
    padding: 34px 38px;
}

/* Custom minimal buttons and inputs in Streamlit */
div[data-testid="stForm"] {
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
}
div[data-testid="stNumberInput"], div[data-testid="stSelectbox"], div[data-testid="stSlider"] {
    margin-bottom: 12px;
}
label[data-testid="stWidgetLabel"] p {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    color: #444444 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
}
div[data-testid="stNumberInputContainer"] {
    border-radius: 14px !important;
    background: rgba(255, 255, 255, 0.9) !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03) !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    border-radius: 14px !important;
    background: rgba(255, 255, 255, 0.9) !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
}

/* Primary floating action button */
.stButton button {
    border-radius: 100px !important;
    background: #050505 !important;
    color: #FFFFFF !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.08em !important;
    padding: 16px 40px !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    box-shadow: 0 20px 45px rgba(0, 0, 0, 0.22) !important;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
    transform: perspective(1000px) translateZ(10px) !important;
}
.stButton button:hover {
    background: #111111 !important;
    transform: perspective(1000px) translateY(-4px) translateZ(25px) !important;
    box-shadow: 0 28px 60px rgba(0, 0, 0, 0.3) !important;
    border-color: rgba(255, 59, 48, 0.4) !important;
}

/* Architecture node glowing lines */
@keyframes lineGlow {
    0% { stroke-dashoffset: 60; }
    100% { stroke-dashoffset: 0; }
}
.glow-flow-line {
    stroke-dasharray: 8 6;
    animation: lineGlow 1.8s linear infinite;
}
</style>

<!-- Floating Ambient Background Technical Markers -->
<div class="bg-tech-marker" style="top: 24px; left: 32px;">01 / MEDIRISK AI // SYS_V3.4</div>
<div class="bg-tech-marker" style="top: 24px; right: 32px;">API: 127.0.0.1:8000 // STATUS: ONLINE</div>
<div class="bg-tech-marker" style="top: 48%; left: 24px;">LAT: 37.7749° N // LON: -122.4194° W</div>
<div class="bg-tech-marker" style="top: 48%; right: 24px;">AXIS: Z+30PX // DEPTH: 1200PX</div>
<div class="bg-tech-marker" style="bottom: 24px; left: 32px;">ENCODER: STANDARD_SCALER + OHE</div>
<div class="bg-tech-marker" style="bottom: 24px; right: 32px;">CALIBRATION: SIGMOID_POSTERIOR</div>
"""

render_floating_html(FLOATING_SYSTEM_CSS)


# ==============================================================================
# 2. API CLIENT & DATA FETCHING
# ==============================================================================
def check_api_health() -> bool:
    try:
        r = requests.get(f"{API_BASE_URL}/", timeout=1.5)
        return r.status_code == 200
    except Exception:
        return False

def fetch_predictions_history():
    try:
        r = requests.get(f"{API_BASE_URL}/predictions", timeout=2.5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def call_predict_api(payload: dict):
    try:
        r = requests.post(f"{API_BASE_URL}/predict", json=payload, timeout=3.5)
        if r.status_code == 200:
            return r.json(), None
        return None, f"API Error ({r.status_code}): {r.text}"
    except Exception as e:
        return None, f"Connection failed to {API_BASE_URL}: {str(e)}"


# ==============================================================================
# 3. COMPONENT: THREE.JS 3D FLOATING SCIENTIFIC HEART (Hero Right)
# ==============================================================================
def render_3d_floating_heart():
    """
    Renders an embedded, holographic 3D wireframe scientific heart
    using Three.js in a perspective canvas with soft ambient shadow.
    """
    heart_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: transparent;
                overflow: hidden;
                width: 100%;
                height: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            #canvas-container {
                width: 100%;
                height: 480px;
                position: relative;
                cursor: grab;
            }
            #canvas-container:active { cursor: grabbing; }
            
            .heart-badge {
                position: absolute;
                top: 20px;
                right: 25px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                letter-spacing: 0.14em;
                color: #888888;
                pointer-events: none;
                z-index: 5;
                background: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(8px);
                padding: 4px 10px;
                border-radius: 20px;
                border: 1px solid rgba(0,0,0,0.06);
            }
            .pulse-dot {
                display: inline-block;
                width: 6px;
                height: 6px;
                background: #FF3B30;
                border-radius: 50%;
                margin-right: 6px;
                animation: pulse 1.2s infinite;
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.6); opacity: 0.4; }
            }
            .heart-shadow {
                position: absolute;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                width: 240px;
                height: 28px;
                background: radial-gradient(ellipse at center, rgba(0, 0, 0, 0.22) 0%, rgba(0, 0, 0, 0.06) 50%, transparent 75%);
                border-radius: 50%;
                filter: blur(10px);
                pointer-events: none;
                transition: transform 0.2s ease;
            }
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    </head>
    <body>
        <div id="canvas-container">
            <div class="heart-badge"><span class="pulse-dot"></span>SYSTOLIC RHYTHM // 72 BPM</div>
            <div id="shadow" class="heart-shadow"></div>
        </div>

        <script>
            const container = document.getElementById('canvas-container');
            const shadowEl = document.getElementById('shadow');
            const scene = new THREE.Scene();
            
            const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(0, 1.2, 5.2);

            const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            container.appendChild(renderer.domElement);

            const heartGroup = new THREE.Group();
            scene.add(heartGroup);

            const pointsArray = [];
            const uSteps = 42;
            const vSteps = 42;
            
            for (let i = 0; i <= uSteps; i++) {
                const u = (i / uSteps) * Math.PI * 2;
                for (let j = 0; j <= vSteps; j++) {
                    const v = (j / vSteps) * Math.PI;
                    
                    const sinV = Math.sin(v);
                    const cosV = Math.cos(v);
                    const sinU = Math.sin(u);
                    const cosU = Math.cos(u);
                    
                    let x = 1.3 * (16 * Math.pow(Math.sin(v), 3)) / 16;
                    let y = 1.3 * (13 * cosV - 5 * Math.cos(2*v) - 2 * Math.cos(3*v) - Math.cos(4*v)) / 16;
                    let z = 1.3 * (12 * Math.sin(v) * Math.cos(u)) / 16;
                    
                    x += 0.15 * Math.sin(u * 2);
                    y += 0.2;
                    
                    pointsArray.push(new THREE.Vector3(x, y, z));
                }
            }

            const wireframeMat = new THREE.LineBasicMaterial({
                color: 0x111111,
                transparent: true,
                opacity: 0.38,
                linewidth: 1
            });
            
            const redHighlightMat = new THREE.LineBasicMaterial({
                color: 0xFF3B30,
                transparent: true,
                opacity: 0.85,
                linewidth: 1.5
            });

            for (let i = 0; i <= uSteps; i += 2) {
                const curvePts = [];
                for (let j = 0; j <= vSteps; j++) {
                    curvePts.push(pointsArray[i * (vSteps + 1) + j]);
                }
                const geom = new THREE.BufferGeometry().setFromPoints(curvePts);
                const isCoronary = (i % 6 === 0);
                const line = new THREE.Line(geom, isCoronary ? redHighlightMat : wireframeMat);
                heartGroup.add(line);
            }

            for (let j = 2; j <= vSteps - 2; j += 2) {
                const ringPts = [];
                for (let i = 0; i <= uSteps; i++) {
                    ringPts.push(pointsArray[i * (vSteps + 1) + j]);
                }
                const geom = new THREE.BufferGeometry().setFromPoints(ringPts);
                const line = new THREE.Line(geom, wireframeMat);
                heartGroup.add(line);
            }

            const particlesGeom = new THREE.BufferGeometry();
            const particleCount = 280;
            const posArray = new Float32Array(particleCount * 3);
            const colorArray = new Float32Array(particleCount * 3);
            
            for (let i = 0; i < particleCount; i++) {
                const randPt = pointsArray[Math.floor(Math.random() * pointsArray.length)];
                posArray[i*3] = randPt.x + (Math.random() - 0.5) * 0.15;
                posArray[i*3+1] = randPt.y + (Math.random() - 0.5) * 0.15;
                posArray[i*3+2] = randPt.z + (Math.random() - 0.5) * 0.15;
                
                if (Math.random() < 0.18) {
                    colorArray[i*3] = 1.0;
                    colorArray[i*3+1] = 0.23;
                    colorArray[i*3+2] = 0.19;
                } else {
                    const shade = 0.1 + Math.random() * 0.2;
                    colorArray[i*3] = shade;
                    colorArray[i*3+1] = shade;
                    colorArray[i*3+2] = shade;
                }
            }
            particlesGeom.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
            particlesGeom.setAttribute('color', new THREE.BufferAttribute(colorArray, 3));

            const pointsMat = new THREE.PointsMaterial({
                size: 0.05,
                vertexColors: true,
                transparent: true,
                opacity: 0.85
            });
            const particlesMesh = new THREE.Points(particlesGeom, pointsMat);
            heartGroup.add(particlesMesh);

            const aortaCurve = new THREE.CatmullRomCurve3([
                new THREE.Vector3(0.0, 0.8, 0.0),
                new THREE.Vector3(0.2, 1.3, -0.1),
                new THREE.Vector3(0.1, 1.6, -0.2),
                new THREE.Vector3(-0.3, 1.45, -0.25)
            ]);
            const aortaGeom = new THREE.TubeGeometry(aortaCurve, 24, 0.12, 8, false);
            const aortaWire = new THREE.WireframeGeometry(aortaGeom);
            const aortaLine = new THREE.LineSegments(aortaWire, wireframeMat);
            heartGroup.add(aortaLine);

            const pulmCurve = new THREE.CatmullRomCurve3([
                new THREE.Vector3(-0.1, 0.75, 0.2),
                new THREE.Vector3(-0.35, 1.25, 0.1),
                new THREE.Vector3(-0.55, 1.35, -0.1)
            ]);
            const pulmGeom = new THREE.TubeGeometry(pulmCurve, 20, 0.1, 8, false);
            const pulmWire = new THREE.WireframeGeometry(pulmGeom);
            const pulmLine = new THREE.LineSegments(pulmWire, redHighlightMat);
            heartGroup.add(pulmLine);

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
            scene.add(ambientLight);
            
            const dirLight = new THREE.DirectionalLight(0xffffff, 0.5);
            dirLight.position.set(3, 8, 5);
            scene.add(dirLight);

            heartGroup.position.y = 0.1;
            heartGroup.rotation.y = -0.35;
            heartGroup.rotation.x = 0.15;

            let isDragging = false;
            let prevMouseX = 0;
            let prevMouseY = 0;

            container.addEventListener('mousedown', (e) => {
                isDragging = true;
                prevMouseX = e.clientX;
                prevMouseY = e.clientY;
            });
            window.addEventListener('mouseup', () => isDragging = false);
            window.addEventListener('mousemove', (e) => {
                if (!isDragging) return;
                const deltaX = e.clientX - prevMouseX;
                const deltaY = e.clientY - prevMouseY;
                heartGroup.rotation.y += deltaX * 0.008;
                heartGroup.rotation.x += deltaY * 0.008;
                prevMouseX = e.clientX;
                prevMouseY = e.clientY;
            });

            container.addEventListener('touchstart', (e) => {
                if (e.touches.length === 1) {
                    isDragging = true;
                    prevMouseX = e.touches[0].clientX;
                    prevMouseY = e.touches[0].clientY;
                }
            });
            window.addEventListener('touchend', () => isDragging = false);
            window.addEventListener('touchmove', (e) => {
                if (!isDragging || e.touches.length !== 1) return;
                const deltaX = e.touches[0].clientX - prevMouseX;
                const deltaY = e.touches[0].clientY - prevMouseY;
                heartGroup.rotation.y += deltaX * 0.008;
                heartGroup.rotation.x += deltaY * 0.008;
                prevMouseX = e.touches[0].clientX;
                prevMouseY = e.touches[0].clientY;
            });

            let clock = new THREE.Clock();

            function animate() {
                requestAnimationFrame(animate);
                const t = clock.getElapsedTime();

                if (!isDragging) {
                    heartGroup.rotation.y += 0.004;
                }

                const floatY = Math.sin(t * 1.1) * 0.16;
                heartGroup.position.y = 0.1 + floatY;

                const pulse = Math.pow(Math.sin(t * 3.8), 6) * 0.06;
                const currentScale = 1.0 + pulse;
                heartGroup.scale.set(currentScale, currentScale, currentScale);

                const shadowScale = (1.0 - floatY * 1.2) * (1.0 + pulse * 0.5);
                const shadowOpacity = 0.22 - floatY * 0.08;
                shadowEl.style.transform = `translateX(-50%) scale(${shadowScale})`;
                shadowEl.style.opacity = Math.max(0.08, shadowOpacity);

                renderer.render(scene, camera);
            }
            animate();

            window.addEventListener('resize', () => {
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            });
        </script>
    </body>
    </html>
    """
    components.html(heart_html, height=480, scrolling=False)


# ==============================================================================
# 4. COMPONENT: FLOATING RADAR GRAPH (Patient Input Profile)
# ==============================================================================
def render_floating_radar(input_data: dict):
    """
    Renders a 3D tilted, transparent glass radar visualization
    displaying the submitted patient input profile on 5 axes.
    """
    axes_labels = [
        ("AGE", input_data.get("age", 55.0), 20.0, 80.0, "yrs"),
        ("RESTING BP", input_data.get("trestbps", 130.0), 90.0, 200.0, "mmHg"),
        ("CHOLESTEROL", input_data.get("chol", 240.0), 120.0, 380.0, "mg/dL"),
        ("MAX HR", input_data.get("thalach", 150.0), 70.0, 210.0, "bpm"),
        ("ST DEPRESSION", input_data.get("oldpeak", 1.2), 0.0, 6.0, "mm"),
    ]

    cx, cy = 200, 190
    max_r = 120

    grid_polys = []
    for step in [0.25, 0.5, 0.75, 1.0]:
        r = max_r * step
        pts = []
        for i in range(5):
            angle = (i * 2 * math.pi / 5) - (math.pi / 2)
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            pts.append(f"{px:.1f},{py:.1f}")
        grid_polys.append(" ".join(pts))

    data_pts = []
    data_markers = []
    for i, (name, val, v_min, v_max, unit) in enumerate(axes_labels):
        norm = max(0.08, min(1.0, (val - v_min) / (v_max - v_min)))
        r = max_r * norm
        angle = (i * 2 * math.pi / 5) - (math.pi / 2)
        px = cx + r * math.cos(angle)
        py = cy + r * math.sin(angle)
        data_pts.append(f"{px:.1f},{py:.1f}")
        
        label_r = max_r + 26
        lx = cx + label_r * math.cos(angle)
        ly = cy + label_r * math.sin(angle)
        data_markers.append((name, f"{val} {unit}", lx, ly, px, py))

    data_poly_str = " ".join(data_pts)

    axis_lines = []
    for i in range(5):
        angle = (i * 2 * math.pi / 5) - (math.pi / 2)
        px = cx + max_r * math.cos(angle)
        py = cy + max_r * math.sin(angle)
        axis_lines.append(f'<line x1="{cx}" y1="{cy}" x2="{px:.1f}" y2="{py:.1f}" stroke="rgba(0,0,0,0.08)" stroke-width="1.2" stroke-dasharray="3,3" />')

    markers_svg = []
    for name, val_str, lx, ly, px, py in data_markers:
        anchor = "middle"
        if lx < cx - 15:
            anchor = "end"
        elif lx > cx + 15:
            anchor = "start"
            
        markers_svg.append(f"""
        <circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="#FF3B30" stroke="#FFFFFF" stroke-width="2" />
        <text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" font-family="'JetBrains Mono', monospace" font-size="9px" font-weight="600" fill="#222222" letter-spacing="0.06em">{name}</text>
        <text x="{lx:.1f}" y="{ly + 11:.1f}" text-anchor="{anchor}" font-family="'JetBrains Mono', monospace" font-size="8px" fill="#888888">{val_str}</text>
        """)

    radar_svg = f"""
    <div class="floating-object float-anim-7s" style="max-width: 520px; margin: 0 auto;">
        <div class="floating-inner">
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
                <div>
                    <span class="mono-tag">03 / MULTI-AXIS</span>
                    <h3 style="font-size: 1.15rem; font-weight: 700; margin: 4px 0 2px; letter-spacing: -0.01em;">PATIENT INPUT PROFILE</h3>
                    <p style="font-size: 0.78rem; color: #777777; margin: 0;">Visualization of submitted input values.</p>
                </div>
                <div class="mono-tag" style="background: rgba(0,0,0,0.04); padding: 4px 10px; border-radius: 12px;">5 PARAMETERS</div>
            </div>
            <div style="width: 100%; display: flex; justify-content: center; position: relative;">
                <svg width="400" height="380" viewBox="0 0 400 380" style="overflow: visible;">
                    {''.join([f'<polygon points="{gp}" fill="none" stroke="rgba(0,0,0,0.06)" stroke-width="1" />' for gp in grid_polys])}
                    {''.join(axis_lines)}
                    <polygon points="{data_poly_str}" fill="rgba(255, 59, 48, 0.12)" stroke="#FF3B30" stroke-width="2.2" />
                    {''.join(markers_svg)}
                </svg>
            </div>
            <div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(0,0,0,0.05); text-align: center;">
                <p style="font-size: 0.72rem; color: #999999; font-style: italic; margin: 0;">
                    IMPORTANT: Visualization of submitted input values. Does not claim medical importance.
                </p>
            </div>
        </div>
        <div class="floating-floor-shadow"></div>
    </div>
    """
    render_floating_html(radar_svg)


# ==============================================================================
# 5. COMPONENT: FLOATING PREDICTION RESULT & SCULPTURAL RISK SCORE
# ==============================================================================
def render_floating_risk_score(result: dict):
    """
    Renders the prediction result as a sculptural, floating 3D glass disc
    with smooth circular arc percentage, floating elevation status, and soft shadow.
    """
    prob = result.get("risk_probability", 0.0)
    percent_val = prob * 100.0
    is_elevated = result.get("prediction", 0) == 1

    radius = 85
    circumference = 2 * math.pi * radius
    stroke_offset = circumference * (1.0 - prob)

    status_badge = "ELEVATED RISK" if is_elevated else "LOW RISK"
    badge_color = "#FF3B30" if is_elevated else "#111111"
    sub_desc = "Significant probability of coronary artery vulnerability detected." if is_elevated else "Cardiac parameters align with low clinical vulnerability baseline."

    result_html = f"""
    <div style="padding: 20px 0;">
        <div class="floating-object float-anim-6s" style="max-width: 680px; margin: 0 auto; background: rgba(255, 255, 255, 0.88);">
            <div class="floating-inner" style="padding: 42px 48px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                    <span class="mono-tag">02 / INFERENCE RESULT</span>
                    <span class="mono-tag" style="background: rgba(0,0,0,0.05); padding: 4px 12px; border-radius: 20px;">MODEL: XGBOOST-3.4</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-around; flex-wrap: wrap; gap: 30px;">
                    <div style="position: relative; width: 220px; height: 220px; display: flex; align-items: center; justify-content: center;">
                        <svg width="220" height="220" viewBox="0 0 220 220" style="transform: rotate(-90deg);">
                            <circle cx="110" cy="110" r="{radius}" fill="none" stroke="rgba(0,0,0,0.06)" stroke-width="12" />
                            <circle cx="110" cy="110" r="{radius}" fill="none" stroke="{badge_color}" stroke-width="12"
                                stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{stroke_offset:.2f}"
                                stroke-linecap="round" style="transition: stroke-dashoffset 1.2s cubic-bezier(0.16, 1, 0.3, 1);" />
                        </svg>
                        <div style="position: absolute; text-align: center;">
                            <div style="font-size: 2.3rem; font-weight: 800; letter-spacing: -0.04em; color: #050505;">
                                {percent_val:.2f}<span style="font-size: 1.2rem; font-weight: 600; color: #888;">%</span>
                            </div>
                            <div class="mono-tag" style="font-size: 0.65rem; color: #888888; margin-top: -2px;">RISK SCORE</div>
                        </div>
                    </div>
                    <div style="flex: 1; min-width: 240px;">
                        <div style="font-size: 0.76rem; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.14em; color: {badge_color}; margin-bottom: 6px;">
                            CLASSIFICATION STATE
                        </div>
                        <h2 style="font-size: 2.4rem; font-weight: 800; letter-spacing: -0.03em; margin: 0 0 10px; color: {badge_color}; line-height: 1.05;">
                            {status_badge}
                        </h2>
                        <p style="font-size: 0.88rem; color: #555555; line-height: 1.5; margin: 0 0 18px;">
                            {sub_desc}
                        </p>
                        <div style="display: flex; gap: 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #777777;">
                            <div style="background: rgba(0,0,0,0.03); padding: 6px 12px; border-radius: 8px;">THRESHOLD: 0.5000</div>
                            <div style="background: rgba(0,0,0,0.03); padding: 6px 12px; border-radius: 8px;">SCORE: {prob:.4f}</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="floating-floor-shadow" style="width: 80%;"></div>
        </div>
    </div>
    """
    render_floating_html(result_html)


# ==============================================================================
# 6. COMPONENT: SCATTERED FLOATING METRICS (Asymmetric Editorial)
# ==============================================================================
def render_scattered_floating_metrics(history: list):
    """
    Renders 3 independent metrics scattered across space with asymmetry,
    different sizes, different vertical offsets, and different floating speeds.
    """
    total_count = len(history)
    elevated_count = sum(1 for item in history if item.get("prediction") == 1)
    avg_risk = (sum(item.get("risk_probability", 0.0) for item in history) / total_count * 100.0) if total_count > 0 else 0.0

    col1, col2, col3 = st.columns([1.1, 1.2, 1.0])

    with col1:
        metric_1 = f"""
        <div class="floating-object float-anim-6s" style="margin-top: 25px; transform: perspective(1200px) rotateX(3deg) rotateY(-4deg);">
            <div class="floating-inner" style="padding: 28px 32px;">
                <span class="mono-tag">TOTAL INFERENCES</span>
                <div style="font-size: 2.8rem; font-weight: 800; letter-spacing: -0.03em; margin: 8px 0 2px; color: #050505;">
                    {total_count}
                </div>
                <div style="font-size: 0.76rem; color: #777777;">Recorded in predictions history</div>
            </div>
            <div class="floating-floor-shadow"></div>
        </div>
        """
        render_floating_html(metric_1)

    with col2:
        metric_2 = f"""
        <div class="floating-object float-anim-8s" style="margin-top: 0px; transform: perspective(1200px) rotateX(-2deg) rotateY(2deg);">
            <div class="floating-inner" style="padding: 34px 38px;">
                <span class="mono-tag">POPULATION AVERAGE RISK</span>
                <div style="font-size: 3.4rem; font-weight: 800; letter-spacing: -0.04em; margin: 8px 0 2px; color: #050505;">
                    {avg_risk:.1f}<span style="font-size: 1.4rem; font-weight: 600; color: #888;">%</span>
                </div>
                <div style="font-size: 0.76rem; color: #777777;">Mean probability across cohort</div>
            </div>
            <div class="floating-floor-shadow" style="width: 85%;"></div>
        </div>
        """
        render_floating_html(metric_2)

    with col3:
        metric_3 = f"""
        <div class="floating-object float-anim-7s" style="margin-top: 45px; transform: perspective(1200px) rotateX(4deg) rotateY(3deg);">
            <div class="floating-inner" style="padding: 26px 30px;">
                <span class="mono-tag" style="color: #FF3B30;">ELEVATED RISK CASES</span>
                <div style="font-size: 2.8rem; font-weight: 800; letter-spacing: -0.03em; margin: 8px 0 2px; color: #FF3B30;">
                    {elevated_count}
                </div>
                <div style="font-size: 0.76rem; color: #777777;">Exceeded 50% clinical threshold</div>
            </div>
            <div class="floating-floor-shadow"></div>
        </div>
        """
        render_floating_html(metric_3)


# ==============================================================================
# 7. COMPONENT: FLOATING PREDICTION HISTORY GRAPH
# ==============================================================================
def render_floating_history_graph(history: list):
    """
    Renders prediction history as a floating glass panel with depth,
    soft shadow, bezier curve line graph, and probability coordinates.
    """
    if not history:
        return

    recent = history[-12:]
    n = len(recent)

    w, h = 820, 260
    pad_x, pad_y = 60, 45
    usable_w = w - 2 * pad_x
    usable_h = h - 2 * pad_y

    points = []
    for i, item in enumerate(recent):
        prob = item.get("risk_probability", 0.0)
        x = pad_x + (i / max(1, n - 1)) * usable_w if n > 1 else pad_x + usable_w / 2
        y = pad_y + (1.0 - prob) * usable_h
        points.append((x, y, prob, i + 1))

    if len(points) == 1:
        path_d = f"M {points[0][0]:.1f} {points[0][1]:.1f}"
        area_d = ""
    else:
        path_d = f"M {points[0][0]:.1f} {points[0][1]:.1f}"
        for i in range(len(points) - 1):
            p0 = points[i]
            p1 = points[i + 1]
            cx1 = p0[0] + (p1[0] - p0[0]) * 0.45
            cy1 = p0[1]
            cx2 = p0[0] + (p1[0] - p0[0]) * 0.55
            cy2 = p1[1]
            path_d += f" C {cx1:.1f} {cy1:.1f}, {cx2:.1f} {cy2:.1f}, {p1[0]:.1f} {p1[1]:.1f}"
            
        area_d = path_d + f" L {points[-1][0]:.1f} {h - pad_y:.1f} L {points[0][0]:.1f} {h - pad_y:.1f} Z"

    thresh_y = pad_y + 0.5 * usable_h

    svg_nodes = []
    for x, y, prob, idx in points:
        color = "#FF3B30" if prob >= 0.5 else "#111111"
        svg_nodes.append(f"""
        <circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{color}" stroke="#FFFFFF" stroke-width="2.5" />
        <text x="{x:.1f}" y="{y - 10:.1f}" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="9px" font-weight="600" fill="{color}">{prob * 100:.1f}%</text>
        <text x="{x:.1f}" y="{h - pad_y + 16:.1f}" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="8px" fill="#999999">#{idx}</text>
        """)

    graph_svg = f"""
    <div class="floating-object float-anim-9s" style="max-width: 960px; margin: 30px auto;">
        <div class="floating-inner" style="padding: 38px 44px;">
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 16px;">
                <div>
                    <span class="mono-tag">06 / LONGITUDINAL MONITORING</span>
                    <h3 style="font-size: 1.35rem; font-weight: 700; margin: 4px 0 2px; letter-spacing: -0.02em;">PREDICTION HISTORY TRAJECTORY</h3>
                    <p style="font-size: 0.8rem; color: #777777; margin: 0;">Real-time risk probability timeline from GET /predictions endpoint.</p>
                </div>
                <div style="display: flex; gap: 14px; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;">
                    <div style="display: flex; align-items: center; gap: 6px;"><span style="width: 8px; height: 8px; background: #FF3B30; border-radius: 50%;"></span> ELEVATED (&ge;50%)</div>
                    <div style="display: flex; align-items: center; gap: 6px;"><span style="width: 8px; height: 8px; background: #111111; border-radius: 50%;"></span> OPTIMAL (&lt;50%)</div>
                </div>
            </div>
            <div style="width: 100%; display: flex; justify-content: center; overflow-x: auto;">
                <svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="overflow: visible;">
                    <defs>
                        <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="rgba(255, 59, 48, 0.16)" />
                            <stop offset="100%" stop-color="rgba(255, 59, 48, 0.0)" />
                        </linearGradient>
                    </defs>
                    <line x1="{pad_x}" y1="{pad_y}" x2="{w - pad_x}" y2="{pad_y}" stroke="rgba(0,0,0,0.04)" stroke-width="1" />
                    <line x1="{pad_x}" y1="{h - pad_y}" x2="{w - pad_x}" y2="{h - pad_y}" stroke="rgba(0,0,0,0.06)" stroke-width="1.2" />
                    <line x1="{pad_x}" y1="{thresh_y:.1f}" x2="{w - pad_x}" y2="{thresh_y:.1f}" stroke="rgba(255, 59, 48, 0.35)" stroke-width="1" stroke-dasharray="4,4" />
                    <text x="{pad_x - 10}" y="{thresh_y + 3:.1f}" text-anchor="end" font-family="'JetBrains Mono', monospace" font-size="8px" fill="#FF3B30">0.50</text>
                    <text x="{pad_x - 10}" y="{pad_y + 3:.1f}" text-anchor="end" font-family="'JetBrains Mono', monospace" font-size="8px" fill="#888888">1.00</text>
                    <text x="{pad_x - 10}" y="{h - pad_y + 3:.1f}" text-anchor="end" font-family="'JetBrains Mono', monospace" font-size="8px" fill="#888888">0.00</text>
                    {f'<path d="{area_d}" fill="url(#areaGrad)" />' if area_d else ''}
                    <path d="{path_d}" fill="none" stroke="#111111" stroke-width="2.6" stroke-linecap="round" />
                    {''.join(svg_nodes)}
                </svg>
            </div>
        </div>
        <div class="floating-floor-shadow" style="width: 82%;"></div>
    </div>
    """
    render_floating_html(graph_svg)


# ==============================================================================
# 8. COMPONENT: FLOATING MODEL ARCHITECTURE NODES
# ==============================================================================
def render_floating_model_architecture():
    """
    Renders the pipeline as suspended, floating 3D glass nodes with
    subtle animated glowing connecting lines flowing from stage to stage.
    """
    arch_html = """
    <div style="padding: 40px 0; text-align: center;">
        <div style="margin-bottom: 24px;">
            <span class="mono-tag">07 / PIPELINE TOPOLOGY</span>
            <h2 style="font-size: 2rem; font-weight: 800; letter-spacing: -0.03em; margin: 6px 0 4px;">FLOATING INFERENCE TOPOLOGY</h2>
            <p style="font-size: 0.85rem; color: #777777; margin: 0;">Decoupled feature transformation through native XGBoost booster.</p>
        </div>

        <div style="display: flex; flex-direction: column; align-items: center; gap: 0px; max-width: 620px; margin: 0 auto;">
            
            <div class="floating-object float-anim-6s" style="width: 100%; transform: perspective(1000px) rotateX(3deg);">
                <div class="floating-inner" style="padding: 22px 28px; display: flex; align-items: center; justify-content: space-between;">
                    <div style="text-align: left;">
                        <span class="mono-tag" style="color: #888;">STAGE 01</span>
                        <div style="font-weight: 700; font-size: 1.05rem; margin-top: 2px;">PATIENT CLINICAL VECTOR</div>
                        <div style="font-size: 0.75rem; color: #777;">13 continuous & categorical clinical parameters</div>
                    </div>
                    <div class="mono-tag" style="background: rgba(0,0,0,0.04); padding: 6px 12px; border-radius: 8px;">INPUT</div>
                </div>
            </div>

            <svg width="40" height="42" viewBox="0 0 40 42">
                <line x1="20" y1="0" x2="20" y2="42" stroke="#FF3B30" stroke-width="2.5" class="glow-flow-line" />
            </svg>

            <div class="floating-object float-anim-8s" style="width: 100%; transform: perspective(1000px) rotateX(-2deg);">
                <div class="floating-inner" style="padding: 22px 28px; display: flex; align-items: center; justify-content: space-between;">
                    <div style="text-align: left;">
                        <span class="mono-tag" style="color: #888;">STAGE 02</span>
                        <div style="font-weight: 700; font-size: 1.05rem; margin-top: 2px;">SCIKIT-LEARN PREPROCESSOR</div>
                        <div style="font-size: 0.75rem; color: #777;">StandardScaler (numerical) + OneHotEncoder (categorical)</div>
                    </div>
                    <div class="mono-tag" style="background: rgba(0,0,0,0.04); padding: 6px 12px; border-radius: 8px;">TRANSFORM</div>
                </div>
            </div>

            <svg width="40" height="42" viewBox="0 0 40 42">
                <line x1="20" y1="0" x2="20" y2="42" stroke="#FF3B30" stroke-width="2.5" class="glow-flow-line" />
            </svg>

            <div class="floating-object float-anim-7s" style="width: 100%; transform: perspective(1000px) rotateX(2deg);">
                <div class="floating-inner" style="padding: 22px 28px; display: flex; align-items: center; justify-content: space-between;">
                    <div style="text-align: left;">
                        <span class="mono-tag" style="color: #FF3B30;">STAGE 03</span>
                        <div style="font-weight: 700; font-size: 1.05rem; margin-top: 2px;">XGBOOST CLASSIFIER</div>
                        <div style="font-size: 0.75rem; color: #777;">Gradient-boosted decision trees (v3.4.1) · DMatrix conversion</div>
                    </div>
                    <div class="mono-tag" style="background: rgba(255,59,48,0.08); color: #FF3B30; padding: 6px 12px; border-radius: 8px;">CORE ENGINE</div>
                </div>
            </div>

            <svg width="40" height="42" viewBox="0 0 40 42">
                <line x1="20" y1="0" x2="20" y2="42" stroke="#FF3B30" stroke-width="2.5" class="glow-flow-line" />
            </svg>

            <div class="floating-object float-anim-10s" style="width: 100%; transform: perspective(1000px) rotateX(-1deg);">
                <div class="floating-inner" style="padding: 22px 28px; display: flex; align-items: center; justify-content: space-between;">
                    <div style="text-align: left;">
                        <span class="mono-tag" style="color: #888;">STAGE 04</span>
                        <div style="font-weight: 700; font-size: 1.05rem; margin-top: 2px;">STRATIFIED RISK PROBABILITY</div>
                        <div style="font-size: 0.75rem; color: #777;">Continuous posterior distribution P(Y=1|X) + Decision Threshold</div>
                    </div>
                    <div class="mono-tag" style="background: rgba(0,0,0,0.04); padding: 6px 12px; border-radius: 8px;">OUTPUT</div>
                </div>
            </div>

        </div>
    </div>
    """
    render_floating_html(arch_html)


# ==============================================================================
# 9. MAIN APPLICATION CONTROLLER
# ==============================================================================
def main():
    if "patient" not in st.session_state:
        st.session_state.patient = {
            "age": 55.0,
            "sex": 1,
            "cp": 2,
            "trestbps": 135.0,
            "chol": 242.0,
            "fbs": 0,
            "restecg": 1,
            "thalach": 152.0,
            "exang": 0,
            "oldpeak": 1.2,
            "slope": 1,
            "ca": 1,
            "thal": 2
        }

    if "prediction_result" not in st.session_state:
        st.session_state.prediction_result = None

    history = fetch_predictions_history()

    # SECTION 1: HERO — ASYMMETRIC EDITORIAL WITH FLOATING 3D HEART
    hero_col_left, hero_col_right = st.columns([1.2, 1.1], gap="large")

    with hero_col_left:
        hero_left_html = """
        <div style="padding-top: 40px; padding-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 18px;">
                <span class="mono-tag-red">01 / CARDIOVASCULAR RISK INTELLIGENCE</span>
                <span style="display: inline-block; width: 4px; height: 4px; background: #FF3B30; border-radius: 50%;"></span>
                <span class="mono-tag">XGB-3.4.1</span>
            </div>
            <h1 style="font-size: 3.8rem; font-weight: 800; letter-spacing: -0.04em; line-height: 1.02; margin: 0 0 20px; color: #050505;">
                MEDIRISK AI<br>
                <span style="color: #666666; font-weight: 600;">CARDIOVASCULAR</span><br>
                RISK INTELLIGENCE
            </h1>
            <p style="font-size: 1.05rem; line-height: 1.6; color: #555555; max-width: 520px; margin-bottom: 30px;">
                An editorial-grade clinical assessment instrument. High-dimensional gradient-boosted decision trees analyze multidimensional cardiovascular biomarkers with zero spatial constraint.
            </p>
            <div style="display: flex; gap: 20px; font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; color: #888888;">
                <div><span style="color: #111; font-weight: 600;">API</span> 127.0.0.1:8000</div>
                <div><span style="color: #111; font-weight: 600;">STATUS</span> ONLINE</div>
                <div><span style="color: #111; font-weight: 600;">LATENCY</span> 3.4MS</div>
            </div>
        </div>
        """
        render_floating_html(hero_left_html)

        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            if st.button("High-Risk Case", key="preset_high", help="Load elevated risk cardiac profile"):
                st.session_state.patient = {
                    "age": 67.0, "sex": 1, "cp": 0, "trestbps": 160.0, "chol": 286.0,
                    "fbs": 0, "restecg": 0, "thalach": 108.0, "exang": 1, "oldpeak": 1.5,
                    "slope": 1, "ca": 3, "thal": 2
                }
                res, _ = call_predict_api(st.session_state.patient)
                if res:
                    st.session_state.prediction_result = res
                st.rerun()

        with p_col2:
            if st.button("Low-Risk Case", key="preset_low", help="Load optimal baseline profile"):
                st.session_state.patient = {
                    "age": 45.0, "sex": 0, "cp": 1, "trestbps": 115.0, "chol": 190.0,
                    "fbs": 0, "restecg": 0, "thalach": 172.0, "exang": 0, "oldpeak": 0.0,
                    "slope": 2, "ca": 0, "thal": 2
                }
                res, _ = call_predict_api(st.session_state.patient)
                if res:
                    st.session_state.prediction_result = res
                st.rerun()

        with p_col3:
            if st.button("Default Values", key="preset_reset"):
                st.session_state.patient = {
                    "age": 55.0, "sex": 1, "cp": 2, "trestbps": 135.0, "chol": 242.0,
                    "fbs": 0, "restecg": 1, "thalach": 152.0, "exang": 0, "oldpeak": 1.2,
                    "slope": 1, "ca": 1, "thal": 2
                }
                st.rerun()

    with hero_col_right:
        render_floating_html('<div class="floating-object float-anim-7s" style="padding: 10px; background: rgba(255, 255, 255, 0.75);">')
        render_3d_floating_heart()
        render_floating_html('</div>')

    # SECTION 2: FLOATING PREDICTION RESULT
    render_floating_html("<div style='height: 40px;'></div>")
    if st.session_state.prediction_result:
        render_floating_risk_score(st.session_state.prediction_result)

    # SECTION 3: ASYMMETRIC FLOATING RADAR + EDITORIAL INSIGHT
    render_floating_html("<div style='height: 50px;'></div>")
    r_col1, r_col2 = st.columns([1.1, 1.0], gap="large")

    with r_col1:
        render_floating_radar(st.session_state.patient)

    with r_col2:
        radar_editorial_html = """
        <div style="padding-top: 60px; max-width: 480px;">
            <span class="mono-tag">03 / MULTI-DIMENSIONAL SPACE</span>
            <h2 style="font-size: 2.4rem; font-weight: 800; letter-spacing: -0.03em; margin: 10px 0 16px; color: #050505; line-height: 1.1;">
                BIOMARKER<br>
                PROJECTION
            </h2>
            <p style="font-size: 0.95rem; color: #555555; line-height: 1.6; margin-bottom: 24px;">
                Clinical indicators are mapped in normalized Euclidean coordinates. Age, resting hemodynamics, circulating cholesterol, chronotropic peak rate, and exercise-induced ischemic ST depression form an integrated vulnerability envelope.
            </p>
            <div style="background: rgba(255,255,255,0.7); backdrop-filter: blur(10px); padding: 18px 24px; border-radius: 18px; border: 1px solid rgba(0,0,0,0.06); font-family: 'JetBrains Mono', monospace; font-size: 0.74rem;">
                <div style="color: #111; font-weight: 600; margin-bottom: 4px;">CALIBRATION METRICS</div>
                <div style="color: #777;">&bull; Feature Normalization: MinMax Projection [0.08, 1.0]</div>
                <div style="color: #777;">&bull; Coordinate System: Pentagonal Polar Array</div>
            </div>
        </div>
        """
        render_floating_html(radar_editorial_html)

    # SECTION 4: FLOATING CLINICAL INPUT DATA OBJECTS
    render_floating_html("<div style='height: 60px;'></div>")
    inputs_header_html = """
    <div style="text-align: center; margin-bottom: 35px;">
        <span class="mono-tag">04 / PATIENT CLINICAL DATA</span>
        <h2 style="font-size: 2.2rem; font-weight: 800; letter-spacing: -0.03em; margin: 6px 0 4px;">FLOATING CLINICAL PARAMETERS</h2>
        <p style="font-size: 0.88rem; color: #777777; margin: 0;">Adjust continuous biomarkers and categorical indicators independently suspended in space.</p>
    </div>
    """
    render_floating_html(inputs_header_html)

    with st.form("clinical_prediction_form"):
        c_col1, c_col2, c_col3 = st.columns([1.0, 1.1, 1.0], gap="medium")

        with c_col1:
            render_floating_html("""
            <div class="floating-object float-anim-6s" style="margin-bottom: 25px;">
                <div class="floating-inner">
                    <span class="mono-tag">PANEL A</span>
                    <h4 style="font-size: 1.1rem; font-weight: 700; margin: 4px 0 16px;">DEMOGRAPHICS & VITALS</h4>
            """)

            age = st.number_input(
                "Patient Age (Years)", min_value=1.0, max_value=120.0,
                value=float(st.session_state.patient["age"]), step=1.0
            )
            sex = st.selectbox(
                "Biological Sex", options=[0, 1],
                index=int(st.session_state.patient["sex"]),
                format_func=lambda x: "Female (0)" if x == 0 else "Male (1)"
            )
            trestbps = st.number_input(
                "Resting Blood Pressure (mmHg)", min_value=50.0, max_value=250.0,
                value=float(st.session_state.patient["trestbps"]), step=1.0
            )
            chol = st.number_input(
                "Serum Cholesterol (mg/dL)", min_value=50.0, max_value=700.0,
                value=float(st.session_state.patient["chol"]), step=1.0
            )

            render_floating_html("""
                </div>
                <div class="floating-floor-shadow"></div>
            </div>
            """)

        with c_col2:
            render_floating_html("""
            <div class="floating-object float-anim-8s" style="margin-bottom: 25px;">
                <div class="floating-inner">
                    <span class="mono-tag">PANEL B</span>
                    <h4 style="font-size: 1.1rem; font-weight: 700; margin: 4px 0 16px;">ELECTROCARDIOLOGY & ISCHEMIA</h4>
            """)

            cp = st.selectbox(
                "Chest Pain Type", options=[0, 1, 2, 3],
                index=int(st.session_state.patient["cp"]),
                format_func=lambda x: {
                    0: "Typical Angina (0)",
                    1: "Atypical Angina (1)",
                    2: "Non-anginal Pain (2)",
                    3: "Asymptomatic (3)"
                }.get(x, str(x))
            )
            restecg = st.selectbox(
                "Resting ECG", options=[0, 1, 2],
                index=int(st.session_state.patient["restecg"]),
                format_func=lambda x: {
                    0: "Normal (0)",
                    1: "ST-T Wave Abnormality (1)",
                    2: "Left Ventricular Hypertrophy (2)"
                }.get(x, str(x))
            )
            fbs = st.selectbox(
                "Fasting Blood Sugar > 120 mg/dL", options=[0, 1],
                index=int(st.session_state.patient["fbs"]),
                format_func=lambda x: "No (0)" if x == 0 else "Yes (1)"
            )
            exang = st.selectbox(
                "Exercise Induced Angina", options=[0, 1],
                index=int(st.session_state.patient["exang"]),
                format_func=lambda x: "No (0)" if x == 0 else "Yes (1)"
            )

            render_floating_html("""
                </div>
                <div class="floating-floor-shadow"></div>
            </div>
            """)

        with c_col3:
            render_floating_html("""
            <div class="floating-object float-anim-7s" style="margin-bottom: 25px;">
                <div class="floating-inner">
                    <span class="mono-tag">PANEL C</span>
                    <h4 style="font-size: 1.1rem; font-weight: 700; margin: 4px 0 16px;">STRESS & FLUOROSCOPY</h4>
            """)

            thalach = st.number_input(
                "Max Heart Rate Achieved (bpm)", min_value=50.0, max_value=250.0,
                value=float(st.session_state.patient["thalach"]), step=1.0
            )
            oldpeak = st.number_input(
                "ST Depression (Oldpeak)", min_value=0.0, max_value=10.0,
                value=float(st.session_state.patient["oldpeak"]), step=0.1
            )
            slope = st.selectbox(
                "Slope of Peak Exercise ST", options=[0, 1, 2],
                index=int(st.session_state.patient["slope"]),
                format_func=lambda x: {
                    0: "Upsloping (0)",
                    1: "Flat (1)",
                    2: "Downsloping (2)"
                }.get(x, str(x))
            )
            ca = st.selectbox(
                "Major Vessels (0-3 Colored)", options=[0, 1, 2, 3],
                index=int(st.session_state.patient["ca"])
            )
            thal = st.selectbox(
                "Thalassemia Scan", options=[0, 1, 2, 3],
                index=int(st.session_state.patient["thal"]),
                format_func=lambda x: {
                    0: "Null/Unknown (0)",
                    1: "Fixed Defect (1)",
                    2: "Normal Blood Flow (2)",
                    3: "Reversible Defect (3)"
                }.get(x, str(x))
            )

            render_floating_html("""
                </div>
                <div class="floating-floor-shadow"></div>
            </div>
            """)

        render_floating_html("<div style='height: 15px;'></div>")
        btn_center1, btn_center2, btn_center3 = st.columns([1, 1.4, 1])
        with btn_center2:
            submitted = st.form_submit_button(
                "RUN CARDIOVASCULAR INFERENCE",
                use_container_width=True
            )

        if submitted:
            payload = {
                "age": float(age),
                "sex": int(sex),
                "cp": int(cp),
                "trestbps": float(trestbps),
                "chol": float(chol),
                "fbs": int(fbs),
                "restecg": int(restecg),
                "thalach": float(thalach),
                "exang": int(exang),
                "oldpeak": float(oldpeak),
                "slope": int(slope),
                "ca": int(ca),
                "thal": int(thal)
            }
            st.session_state.patient = payload
            res, err = call_predict_api(payload)
            if res:
                st.session_state.prediction_result = res
                st.rerun()
            else:
                st.error(f"Inference Failure: {err}")

    # SECTION 5: SCATTERED FLOATING METRICS
    render_floating_html("<div style='height: 50px;'></div>")
    metrics_header_html = """
    <div style="text-align: center; margin-bottom: 20px;">
        <span class="mono-tag">05 / POPULATION METRICS</span>
        <h2 style="font-size: 2.2rem; font-weight: 800; letter-spacing: -0.03em; margin: 6px 0 4px;">FLOATING COHORT METRICS</h2>
        <p style="font-size: 0.88rem; color: #777777; margin: 0;">Aggregate distribution from accumulated clinical predictions.</p>
    </div>
    """
    render_floating_html(metrics_header_html)
    render_scattered_floating_metrics(history)

    # SECTION 6: FLOATING PREDICTION HISTORY GRAPH
    render_floating_html("<div style='height: 50px;'></div>")
    render_floating_history_graph(history)

    # SECTION 7: FLOATING MODEL ARCHITECTURE TOPOLOGY
    render_floating_html("<div style='height: 40px;'></div>")
    render_floating_model_architecture()

    # EDITORIAL FOOTNOTE
    footer_html = """
    <div style="text-align: center; padding: 60px 0 30px; border-top: 1px solid rgba(0,0,0,0.06); margin-top: 80px;">
        <div class="mono-tag" style="margin-bottom: 8px;">MEDIRISK AI // CARDIOVASCULAR RISK INTELLIGENCE</div>
        <div style="font-size: 0.76rem; color: #999999;">
            Designed as an editorial product experience. Built with Streamlit, FastAPI, and XGBoost.
        </div>
    </div>
    """
    render_floating_html(footer_html)


if __name__ == "__main__":
    main()
