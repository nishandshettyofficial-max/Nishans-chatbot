# 🌌 Nishans Chatbot — Cinematic Dark AI Experience

A bespoke, digital art-inspired AI Agent and Chatbot experience on macOS (MacBook Air M4) powered by Python, Streamlit, HTML5 Canvas particle physics, and Google's Gemini API (`gemini-3.5-flash`).

Inspired by the award-winning design aesthetic of **Vadim Carazan**'s digital portfolio.

---

## 🌟 Visual & Cinematic Highlights

1. **Full-Screen Cinematic Intro Animation:**
   - **Phase 1: Darkness & Emergence:** Begins in an obsidian void (`#030304`) with floating ambient stars and micro-dust.
   - **Phase 2: Dynamic Convergence:** Over 4,500 luminous particles coalesce into a high-fidelity portrait of Nishan (sunglasses with glossy glare, styled hair, patterned collar).
   - **Phase 3: Background Typography & Line Art:** Oversized elegant serif typography (*"Nishan Shetty"*) and a dynamic hand-drawn signature curve fade into the background with subtle parallax depth.
   - **Phase 4: Transition & Reveal:** Click **"Enter Chatbot"** or press `Enter` to smoothly disperse the particles and fade into the luxury dark chat interface.
   - **Replayability:** A **"✨ Replay Cinematic Intro"** button in the sidebar lets you re-trigger the experience anytime.

2. **Complete Luxury Dark Identity:**
   - Background: `#050507`
   - Surfaces: Layered charcoal and obsidian graphite (`#0d0d12`, `#13131a`)
   - Accents: Electric violet (`#6366f1`), cyan/blue (`#38bdf8`), and silver
   - Typography: *Playfair Display* italic serif for branding and *Plus Jakarta Sans* for clean, readable conversations.

3. **Autonomous Agentic Capabilities:**
   - Powered by **Google Gemini 3.5 Flash** using the official `google-genai` SDK.
   - **Tool Access:** `save_note` with strict input/output validation and directory traversal defenses.
   - **Human-in-the-Loop (HITL):** Pauses and requires your approval (`[✅ Approve & Save]` / `[❌ Reject & Cancel]`) before writing any file to disk.
   - **Loop Guardrails:** Enforces a maximum limit of 5 tool calls per task.
   - **Transparent Reasoning:** Expandable step-by-step thought trail for full interpretability.

---

## 📂 Project Architecture

```text
project1/
├── app.py                      # Main Streamlit application with luxury dark CSS & routing
├── intro_component.py          # Custom component wrapper for the cinematic intro
├── components/
│   └── cinematic_intro/
│       ├── index.html          # High-performance HTML5 Canvas particle physics engine
│       ├── particles_data.js   # Pre-processed coordinate & color points of Nishan's portrait
│       └── particles.json      # Raw JSON dataset (4,534 optimized particles)
├── agent.py                    # Autonomous AI Agent core (reasoning, tool calls, approval, guardrails)
├── tools.py                    # External tool definition (save_note) with validation
├── test_agent.py               # Automated unit test suite (13/13 passing)
├── assets/                     # Source images (nishan.jpg, cropped portrait)
├── requirements.txt            # Python dependencies
├── .env                        # Local secrets (GEMINI_API_KEY)
└── README.md                   # Project documentation
```

---

## 🚀 How to Run on macOS

```bash
cd /Users/nishandshetty/Downloads/Antigravity/project1
source .venv/bin/activate
streamlit run app.py
```

Open **[http://localhost:8501](http://localhost:8501)** in your browser to experience the intro animation and chatbot.

---

## 🧪 Running Automated Tests

```bash
source .venv/bin/activate
python -m unittest test_agent.py -v
```
All 13 unit tests verify validation, path traversal security, tool decisions, human approval flows, and loop limits.
