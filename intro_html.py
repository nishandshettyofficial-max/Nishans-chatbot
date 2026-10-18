"""
intro_html.py
Generates the self-contained HTML for the cinematic particle intro.
100% self-contained with inlined compact particles data, zero external file dependencies.
"""

import json
import os

COMPACT_JSON_PATH = os.path.join(
    os.path.dirname(__file__), "components", "cinematic_intro", "compact_particles.json"
)

# Load compact particles once
if os.path.exists(COMPACT_JSON_PATH):
    with open(COMPACT_JSON_PATH, "r", encoding="utf-8") as f:
        PARTICLES_JSON = f.read().strip()
else:
    PARTICLES_JSON = "[]"


def get_cinematic_intro_html() -> str:
    """Returns the standalone HTML string for the cinematic particle intro."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nishans Chatbot — Cinematic AI Experience</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Playfair+Display:ital,wght@1,400;1,600;1,700&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
  
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
      -webkit-user-select: none;
    }}

    html, body {{
      width: 100%;
      height: 100%;
      overflow: hidden;
      background-color: #030305;
      color: #ededed;
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    #stage {{
      position: relative;
      width: 100vw;
      height: 100vh;
      min-height: 720px;
      background: radial-gradient(circle at 50% 45%, #08080d 0%, #030305 85%);
      overflow: hidden;
    }}

    canvas {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 2;
      display: block;
    }}

    /* Subtle Film Grain / Vignette */
    .vignette {{
      position: absolute;
      inset: 0;
      pointer-events: none;
      background: radial-gradient(circle at 50% 50%, transparent 45%, rgba(2, 2, 4, 0.85) 100%);
      z-index: 4;
    }}

    /* Top Metadata Header (matching Vadim Carazan reference) */
    .header-bar {{
      position: absolute;
      top: 24px;
      left: 36px;
      right: 36px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      z-index: 10;
      font-size: 11px;
      letter-spacing: 0.04em;
      color: rgba(230, 230, 235, 0.7);
      pointer-events: auto;
    }}

    .brand-logo {{
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: #ffffff;
    }}

    .logo-glyph {{
      width: 32px;
      height: 32px;
      border: 1px solid rgba(255, 255, 255, 0.22);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Cinzel', serif;
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 1px;
      background: rgba(255, 255, 255, 0.04);
      backdrop-filter: blur(8px);
    }}

    .meta-group {{
      line-height: 1.5;
    }}

    .meta-label {{
      color: rgba(255, 255, 255, 0.35);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}

    .meta-val {{
      color: rgba(240, 240, 245, 0.85);
      font-weight: 400;
    }}

    .live-dot {{
      display: inline-block;
      width: 6px;
      height: 6px;
      background-color: #38bdf8;
      border-radius: 50%;
      margin-right: 6px;
      box-shadow: 0 0 8px #38bdf8;
      animation: pulseGlow 2s infinite ease-in-out;
    }}

    @keyframes pulseGlow {{
      0%, 100% {{ opacity: 0.5; transform: scale(0.9); }}
      50% {{ opacity: 1; transform: scale(1.15); }}
    }}

    /* Oversized Background Typography (Vadim Carazan style) */
    .bg-title-container {{
      position: absolute;
      bottom: 70px;
      left: 0;
      width: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
      pointer-events: none;
      z-index: 1;
      opacity: 0;
      transform: translateY(20px);
      transition: opacity 1.8s ease 1.2s, transform 1.8s cubic-bezier(0.16, 1, 0.3, 1) 1.2s;
    }}

    .bg-title {{
      font-family: 'Playfair Display', serif;
      font-style: italic;
      font-size: clamp(64px, 12vw, 160px);
      font-weight: 600;
      color: rgba(255, 255, 255, 0.85);
      letter-spacing: -0.02em;
      line-height: 0.9;
      white-space: nowrap;
      text-shadow: 0 10px 40px rgba(0, 0, 0, 0.9);
    }}

    /* Bottom Info & Enter Button */
    .footer-bar {{
      position: absolute;
      bottom: 28px;
      left: 36px;
      right: 36px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      z-index: 10;
      pointer-events: auto;
    }}

    .footer-desc {{
      max-width: 320px;
      font-size: 11px;
      line-height: 1.6;
      color: rgba(220, 220, 230, 0.55);
      letter-spacing: 0.02em;
    }}

    .enter-btn {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 12px 28px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.22);
      color: #ffffff;
      font-size: 12px;
      font-weight: 500;
      letter-spacing: 0.04em;
      cursor: pointer;
      backdrop-filter: blur(12px);
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }}

    .enter-btn:hover {{
      background: rgba(255, 255, 255, 0.14);
      border-color: rgba(255, 255, 255, 0.55);
      transform: translateY(-2px);
      box-shadow: 0 8px 30px rgba(99, 102, 241, 0.3);
    }}

    .enter-btn .arrow-icon {{
      display: inline-block;
      width: 14px;
      height: 14px;
      transition: transform 0.3s ease;
    }}

    .enter-btn:hover .arrow-icon {{
      transform: translateX(4px);
    }}

    .shortcut-badge {{
      font-size: 10px;
      padding: 3px 6px;
      border-radius: 4px;
      background: rgba(255, 255, 255, 0.08);
      color: rgba(255, 255, 255, 0.5);
      letter-spacing: 0.05em;
    }}

    /* Signature Curve SVG */
    .signature-svg {{
      position: absolute;
      top: 15%;
      left: 8%;
      width: 84%;
      height: 70%;
      pointer-events: none;
      z-index: 1;
      opacity: 0.26;
    }}

    .sig-path {{
      stroke: #ffffff;
      stroke-width: 1.2;
      stroke-dasharray: 2000;
      stroke-dashoffset: 2000;
      transition: stroke-dashoffset 3.5s cubic-bezier(0.16, 1, 0.3, 1) 0.5s;
    }}

    /* Transition Fade Out State */
    .exit-animation {{
      transition: all 0.9s cubic-bezier(0.16, 1, 0.3, 1);
      opacity: 0 !important;
      transform: scale(1.04);
      filter: blur(10px);
    }}
  </style>
</head>
<body>
  <div id="stage">
    <canvas id="particleCanvas"></canvas>

    <svg class="signature-svg" viewBox="0 0 1000 700" fill="none">
      <path class="sig-path" id="sigPath" d="M 50 350 Q 200 80, 480 320 T 750 200 Q 920 120, 980 280 M 220 160 L 210 520 M 180 360 C 280 280, 360 480, 420 380" />
    </svg>

    <div class="header-bar">
      <div class="brand-logo">
        <div class="logo-glyph">NC</div>
      </div>

      <div class="meta-group">
        <div class="meta-label">Workspace</div>
        <div class="meta-val">Journal & Studio</div>
      </div>

      <div class="meta-group" style="text-align: center;">
        <div class="meta-label">Status</div>
        <div class="meta-val"><span class="live-dot"></span>Online • Gemini 3.5</div>
      </div>

      <div class="meta-group" style="text-align: right;">
        <div class="meta-label">Navigation</div>
        <div class="meta-val">Chat • Journal • Notes</div>
      </div>
    </div>

    <div class="bg-title-container" id="bgTitle">
      <h1 class="bg-title">Nishan Shetty</h1>
    </div>

    <div class="footer-bar">
      <div class="footer-desc">
        Designed for creative clarity, deep focus, and seamless productivity. Built for macOS.
      </div>

      <div>
        <button class="enter-btn" id="enterBtn">
          <span>Get Started</span>
          <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
          <span class="shortcut-badge">↵</span>
        </button>
      </div>

    </div>

    <div class="vignette"></div>
  </div>

  <script>
    const RAW_PARTICLES = {PARTICLES_JSON};

    (function() {{
      const canvas = document.getElementById('particleCanvas');
      const ctx = canvas.getContext('2d');
      const bgTitle = document.getElementById('bgTitle');
      const sigPath = document.getElementById('sigPath');
      const enterBtn = document.getElementById('enterBtn');
      const stage = document.getElementById('stage');

      let width = window.innerWidth;
      let height = window.innerHeight;
      let dpr = Math.min(window.devicePixelRatio || 1, 2);

      function resize() {{
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        ctx.scale(dpr, dpr);
        updateTargets();
      }}

      // Particle representation
      class Particle {{
        constructor(arr, i) {{
          this.i = i;
          this.normX = arr[0];
          this.normY = arr[1];
          this.r = arr[2];
          this.g = arr[3];
          this.b = arr[4];
          this.size = arr[5] || 2.0;
          this.isSquare = arr[6] === 1;

          // Dispersed spawn
          const ang = Math.random() * Math.PI * 2;
          const rad = Math.random() * Math.max(width, height) * 0.8 + 100;
          this.x = width / 2 + Math.cos(ang) * rad;
          this.y = height / 2 + Math.sin(ang) * rad;

          this.vx = (Math.random() - 0.5) * 1.6;
          this.vy = (Math.random() - 0.5) * 1.6;

          this.targetX = width / 2;
          this.targetY = height / 2;

          this.delay = 0.4 + Math.random() * 1.2;
          this.spring = 0.042 + Math.random() * 0.024;
          this.friction = 0.87 + Math.random() * 0.04;
          this.alpha = 0.0;
          this.driftPhase = Math.random() * Math.PI * 2;
        }}

        setTarget(scale, centerY) {{
          this.targetX = (width / 2) + (this.normX * scale);
          this.targetY = centerY + (this.normY * scale);
        }}

        update(elapsed, mx, my, isExiting) {{
          if (isExiting) {{
            const dx = this.x - width / 2;
            const dy = this.y - height / 2;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            this.vx += (dx / dist) * 3.5;
            this.vy += (dy / dist) * 3.5;
            this.alpha *= 0.92;
            this.x += this.vx;
            this.y += this.vy;
            return;
          }}

          if (elapsed < this.delay) {{
            this.x += this.vx;
            this.y += this.vy;
            this.alpha = Math.min(0.65, this.alpha + 0.03);
            return;
          }}

          const dx = this.targetX - this.x;
          const dy = this.targetY - this.y;
          this.vx += dx * this.spring;
          this.vy += dy * this.spring;
          this.vx *= this.friction;
          this.vy *= this.friction;

          // Interactive mouse repulsion
          if (mx !== null && my !== null) {{
            const mdx = this.x - mx;
            const mdy = this.y - my;
            const mdist = Math.sqrt(mdx * mdx + mdy * mdy);
            if (mdist < 90) {{
              const force = (1 - mdist / 90) * 4.0;
              this.vx += (mdx / mdist) * force;
              this.vy += (mdy / mdist) * force;
            }}
          }}

          if (elapsed > 3.5) {{
            this.driftPhase += 0.03;
            this.x += Math.sin(this.driftPhase) * 0.16;
            this.y += Math.cos(this.driftPhase) * 0.16;
          }}

          this.x += this.vx;
          this.y += this.vy;
          if (this.alpha < 0.95) this.alpha += 0.035;
        }}

        draw(ctx) {{
          if (this.alpha <= 0.02) return;
          ctx.fillStyle = `rgba(${{this.r}}, ${{this.g}}, ${{this.b}}, ${{this.alpha}})`;
          if (this.isSquare) {{
            ctx.fillRect(this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
          }} else {{
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size / 2, 0, Math.PI * 2);
            ctx.fill();
          }}
        }}
      }}

      // Ambient Stars
      const stars = [];
      for (let i = 0; i < 110; i++) {{
        stars.push({{
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.25,
          vy: (Math.random() - 0.5) * 0.25,
          size: Math.random() * 1.5 + 0.5,
          alpha: Math.random() * 0.5 + 0.2,
          pulse: Math.random() * Math.PI,
        }});
      }}

      const particles = RAW_PARTICLES.map((p, i) => new Particle(p, i));

      function updateTargets() {{
        const minDim = Math.min(width, height);
        const scale = minDim * 0.44;
        const centerY = height * 0.43;
        for (let p of particles) {{
          p.setTarget(scale, centerY);
        }}
      }}

      window.addEventListener('resize', resize);
      resize();

      let mouseX = null;
      let mouseY = null;
      window.addEventListener('mousemove', (e) => {{
        mouseX = e.clientX;
        mouseY = e.clientY;
      }});
      window.addEventListener('mouseleave', () => {{
        mouseX = null;
        mouseY = null;
      }});

      let startTime = null;
      let isExiting = false;

      function loop(timestamp) {{
        if (!startTime) startTime = timestamp;
        const elapsed = (timestamp - startTime) / 1000;

        ctx.fillStyle = 'rgba(3, 3, 5, 0.45)';
        ctx.fillRect(0, 0, width, height);

        // Draw ambient stars
        for (let s of stars) {{
          if (!isExiting) {{
            s.x += s.vx;
            s.y += s.vy;
            if (s.x < 0) s.x = width;
            if (s.x > width) s.x = 0;
            if (s.y < 0) s.y = height;
            if (s.y > height) s.y = 0;
            s.pulse += 0.02;
          }}
          const a = s.alpha * ((Math.sin(s.pulse) + 1) * 0.35 + 0.4);
          ctx.fillStyle = `rgba(240, 245, 255, ${{a}})`;
          ctx.beginPath();
          ctx.arc(s.x, s.y, s.size, 0, Math.PI * 2);
          ctx.fill();
        }}

        // Draw particles
        for (let p of particles) {{
          p.update(elapsed, mouseX, mouseY, isExiting);
          p.draw(ctx);
        }}

        if (elapsed > 1.5 && sigPath) {{
          sigPath.style.strokeDashoffset = '0';
        }}
        if (elapsed > 2.2 && bgTitle) {{
          bgTitle.style.opacity = '1';
          bgTitle.style.transform = 'translateY(0px)';
        }}

        requestAnimationFrame(loop);
      }}

      requestAnimationFrame(loop);

      function enterChat() {{
        if (isExiting) return;
        isExiting = true;
        stage.classList.add('exit-animation');

        setTimeout(() => {{
          try {{
            // Direct parent navigation: switch query param to enter chat
            window.parent.location.search = '?view=chat';
          }} catch(e) {{
            console.log('Parent navigation restricted, trying fallback', e);
          }}
        }}, 600);
      }}

      enterBtn.addEventListener('click', enterChat);
      window.addEventListener('keydown', (e) => {{
        if (e.key === 'Enter' || e.key === ' ') {{
          enterChat();
        }}
      }});
    }})();
  </script>
</body>
</html>"""
