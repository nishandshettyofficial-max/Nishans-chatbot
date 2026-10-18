"""
app.py
Nishan — Automatic Thought Journal & AI Experience
Apple-inspired minimalist dark theme (Black & Grey, Glassmorphism, Clean Human Copy).
Inspired by Dayflow and macOS design language.
"""

from datetime import datetime
import os
import base64
from dotenv import load_dotenv
import streamlit as st
import streamlit.components.v1 as components

# Load environment variables
load_dotenv(override=True)

from agent import AIAgent, AgentState
from intro_html import get_cinematic_intro_html
from tools import NOTES_DIR


@st.cache_data
def get_aurora_bg_base64() -> str:
    """Load and base64-encode the violet silk aurora wallpaper."""
    bg_path = os.path.join(os.path.dirname(__file__), "assets", "aurora_bg.jpg")
    if os.path.exists(bg_path):
        with open(bg_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

# ----------------- Page Configuration -----------------
st.set_page_config(
    page_title="Nishan — Journal & Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------- Session State -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "intro_active" not in st.session_state:
    st.session_state.intro_active = True

if st.query_params.get("view") == "chat":
    st.session_state.intro_active = False

os.makedirs(NOTES_DIR, exist_ok=True)


# =========================================================================
# VIEW 1: Cinematic Intro Animation
# =========================================================================
if st.session_state.intro_active:
    st.markdown(
        """
        <style>
            header, footer, [data-testid="stSidebar"], [data-testid="collapsedControl"] {
                display: none !important;
            }
            .block-container {
                padding-top: 14px !important;
                padding-bottom: 0 !important;
                padding-left: 28px !important;
                padding-right: 28px !important;
                max-width: 100vw !important;
            }
            [data-testid="stAppViewContainer"] {
                background-color: #030305 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Top Control Bar (Apple-style minimal glass bar)
    col_t1, col_t2 = st.columns([8, 2])
    with col_t1:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 12px; padding-top: 4px;">
                <div style="font-size: 17px; font-weight: 600; color: #f5f5f7; letter-spacing: -0.02em;">Nishan</div>
                <div style="font-size: 11px; color: #86868b; text-transform: uppercase; letter-spacing: 0.08em; background: rgba(255,255,255,0.06); padding: 3px 8px; border-radius: 999px;">
                    Journal & Studio
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_t2:
        if st.button("Open App →", type="primary", use_container_width=True, key="enter_chat_btn"):
            st.session_state.intro_active = False
            st.query_params["view"] = "chat"
            st.rerun()

    # Inlined Self-contained Canvas Intro
    intro_html_payload = get_cinematic_intro_html()
    components.html(intro_html_payload, height=820, scrolling=False)
    st.stop()


# =========================================================================
# VIEW 2: Apple-Inspired Minimalist Dark UI (Black & Grey Glassmorphism)
# =========================================================================

today_str = datetime.now().strftime("%A, %d %B")

# Master Apple Dark Theme Stylesheet with Silk Aurora Wallpaper
aurora_bg_b64 = get_aurora_bg_base64()

css_code = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg-canvas: #060608;
        --glass-bg: rgba(18, 18, 24, 0.68);
        --glass-bg-hover: rgba(26, 26, 36, 0.85);
        --glass-border: rgba(255, 255, 255, 0.08);
        --glass-border-strong: rgba(255, 255, 255, 0.16);
        --text-heading: #f5f5f7;
        --text-body: #d1d5db;
        --text-secondary: #86868b;
        --text-muted: #52525b;
        --accent-violet: #a78bfa;
        --accent-apple: #f5f5f7;
        --card-radius: 20px;
    }

    /* Full Canvas Background: Zeabur/Apple Dark Theme with Silk Aurora Glow */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-canvas) !important;
        background-image: 
            linear-gradient(180deg, rgba(6, 6, 9, 0.42) 0%, rgba(6, 6, 9, 0.78) 100%),
            url("data:image/jpeg;base64,__AURORA_BG_B64__") !important;
        background-size: cover !important;
        background-position: center top !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
        color: var(--text-heading) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Plus Jakarta Sans', sans-serif !important;
        -webkit-font-smoothing: antialiased !important;
    }

    /* Transparent containers so aurora glows through */
    .stMain, [data-testid="stMain"] {
        background: transparent !important;
    }

    /* Main Content Container: Full width so messages sit on the opposite ends */
    .block-container {
        padding-top: 28px !important;
        padding-bottom: 220px !important;
        padding-left: 36px !important;
        padding-right: 36px !important;
        max-width: 100% !important;
        width: 100% !important;
        margin: 0 !important;
    }

    /* Top Header */
    header[data-testid="stHeader"] {
        background: rgba(6, 6, 9, 0.65) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        border-bottom: 1px solid var(--glass-border) !important;
    }

    /* Minimal Sidebar (macOS style) */
    [data-testid="stSidebar"] {
        background-color: rgba(9, 9, 13, 0.85) !important;
        backdrop-filter: blur(28px) saturate(180%) !important;
        border-right: 1px solid var(--glass-border) !important;
    }

    /* Hero Typography & Announcement Badge */
    .hero-wrapper {
        max-width: 860px;
        margin: 0 auto;
    }

    .hero-section {
        text-align: center;
        margin-top: 20px;
        margin-bottom: 32px;
    }

    .announcement-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 999px;
        font-size: 12px;
        color: #d1d5db;
        margin-bottom: 20px;
        backdrop-filter: blur(16px);
        transition: all 0.2s ease;
    }

    .announcement-pill:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(180, 140, 255, 0.35);
    }

    .pill-badge {
        background: linear-gradient(135deg, #a78bfa 0%, #818cf8 100%);
        color: #0b0b10;
        font-weight: 700;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 2px 8px;
        border-radius: 999px;
    }

    .hero-title {
        font-size: clamp(38px, 6.5vw, 68px);
        font-weight: 700;
        letter-spacing: -0.04em;
        line-height: 1.08;
        color: #ffffff;
        margin-bottom: 14px;
    }

    .hero-gradient-text {
        background: linear-gradient(135deg, #ffffff 40%, #c4b5fd 80%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        font-size: 16px;
        font-weight: 400;
        color: var(--text-secondary);
        letter-spacing: -0.01em;
        max-width: 540px;
        margin: 0 auto;
        line-height: 1.55;
    }

    /* Capabilities Trust Bar (Matching Zeabur logo bar) */
    .capabilities-bar {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
        font-size: 12px;
        color: #71717a;
        letter-spacing: 0.02em;
        margin-top: 18px;
        margin-bottom: 32px;
    }

    .dot-sep {
        color: rgba(255, 255, 255, 0.15);
    }

    /* =======================================================
       Chat Layout: User on Far Right End, AI on Far Left End
       ======================================================= */

    /* Hide ALL avatar icons, emojis, and avatar columns completely */
    [data-testid="stChatMessage"] [data-testid*="Avatar"],
    [data-testid="stChatMessage"] [data-testid*="avatar"],
    [data-testid="stChatMessage"] [data-testid*="chatAvatarIcon"],
    [data-testid="stChatMessage"] > div:first-child:not([data-testid="stChatMessageContent"]),
    [data-testid="stChatMessage"] > div:has(svg, img, [role="img"]) {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        min-width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        visibility: hidden !important;
    }

    /* Prevent invisible markers or empty elements from rendering as empty boxes */
    .user-marker, .ai-marker {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        font-size: 0 !important;
        line-height: 0 !important;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"]:empty,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"]:has(> span.user-marker:only-child),
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"]:has(> span.ai-marker:only-child) {
        display: none !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        background: transparent !important;
    }

    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
        padding: 6px 0 !important;
        margin-bottom: 16px !important;
        gap: 0 !important;
        width: 100% !important;
    }

    /* USER MESSAGE: Sized to content, aligned to the FAR RIGHT END */
    [data-testid="stChatMessage"]:has(.user-marker) {
        display: flex !important;
        flex-direction: row-reverse !important;
        justify-content: flex-start !important;
        align-items: flex-end !important;
        width: 100% !important;
        margin-left: auto !important;
        margin-right: 0 !important;
    }

    [data-testid="stChatMessage"]:has(.user-marker) [data-testid="stChatMessageContent"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-end !important;
        width: auto !important;
        max-width: 62% !important;
        margin-left: auto !important;
        margin-right: 0 !important;
    }

    [data-testid="stChatMessage"]:has(.user-marker) [data-testid="stChatMessageContent"] > div {
        display: flex !important;
        justify-content: flex-end !important;
        width: auto !important;
    }

    [data-testid="stChatMessage"]:has(.user-marker) [data-testid="stMarkdownContainer"] {
        background: #202027 !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 20px 20px 4px 20px !important;
        padding: 12px 22px !important;
        display: inline-block !important;
        width: fit-content !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
        color: #f5f5f7 !important;
        text-align: left !important;
        word-break: break-word !important;
    }

    [data-testid="stChatMessage"]:has(.user-marker) [data-testid="stMarkdownContainer"] p {
        margin: 0 !important;
        display: inline !important;
    }

    /* AI MESSAGE: Sized to content, aligned to the FAR LEFT END */
    [data-testid="stChatMessage"]:has(.ai-marker) {
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-start !important;
        align-items: flex-start !important;
        width: 100% !important;
        margin-left: 0 !important;
        margin-right: auto !important;
    }

    [data-testid="stChatMessage"]:has(.ai-marker) [data-testid="stChatMessageContent"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        width: auto !important;
        max-width: 65% !important;
        margin-left: 0 !important;
        margin-right: auto !important;
    }

    [data-testid="stChatMessage"]:has(.ai-marker) [data-testid="stChatMessageContent"] > div {
        display: flex !important;
        justify-content: flex-start !important;
        width: auto !important;
    }

    [data-testid="stChatMessage"]:has(.ai-marker) [data-testid="stMarkdownContainer"] {
        background: rgba(18, 18, 24, 0.78) !important;
        backdrop-filter: blur(28px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px 20px 20px 4px !important;
        padding: 16px 24px !important;
        display: inline-block !important;
        width: fit-content !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45) !important;
        color: #e4e4e7 !important;
        text-align: left !important;
        word-break: break-word !important;
    }

    [data-testid="stChatMessage"]:has(.ai-marker) [data-testid="stMarkdownContainer"] p {
        margin-bottom: 8px !important;
    }
    [data-testid="stChatMessage"]:has(.ai-marker) [data-testid="stMarkdownContainer"] p:last-child {
        margin-bottom: 0 !important;
    }

    /* Modern AI Thinking / Loading Bubble (ChatGPT & Apple Style) */
    .thinking-container {
        display: flex;
        justify-content: flex-start;
        margin: 6px 0 16px 0;
        width: 100%;
    }

    .thinking-bubble {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        background: rgba(18, 18, 24, 0.78) !important;
        backdrop-filter: blur(28px) saturate(180%) !important;
        border: 1px solid rgba(180, 140, 255, 0.3) !important;
        border-radius: 20px 20px 20px 4px !important;
        padding: 13px 20px !important;
        box-shadow: 0 8px 30px rgba(120, 70, 220, 0.16) !important;
        animation: thinkingPulseGlow 2.5s infinite ease-in-out;
    }

    @keyframes thinkingPulseGlow {
        0%, 100% {
            border-color: rgba(180, 140, 255, 0.22);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        }
        50% {
            border-color: rgba(180, 140, 255, 0.55);
            box-shadow: 0 8px 32px rgba(140, 80, 240, 0.25);
        }
    }

    .thinking-dots {
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .pulse-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #c4b5fd;
        display: inline-block;
        animation: pulseWave 1.4s infinite ease-in-out both;
    }

    .pulse-dot:nth-child(1) { animation-delay: -0.32s; }
    .pulse-dot:nth-child(2) { animation-delay: -0.16s; }
    .pulse-dot:nth-child(3) { animation-delay: 0s; }

    @keyframes pulseWave {
        0%, 80%, 100% {
            transform: scale(0.65);
            opacity: 0.35;
        }
        40% {
            transform: scale(1.15);
            opacity: 1;
            background: #ffffff;
            box-shadow: 0 0 8px rgba(180, 140, 255, 0.85);
        }
    }

    .thinking-label {
        font-size: 13.5px;
        font-weight: 500;
        color: #c4b5fd;
        letter-spacing: -0.01em;
    }

    /* Note Saved Notification Pill */
    .saved-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 10px;
        font-size: 12px;
        color: #d1d5db;
        margin-top: 8px;
    }

    /* Apple File Download Card */
    .file-download-card {
        display: flex;
        align-items: center;
        gap: 14px;
        background: rgba(24, 24, 34, 0.88) !important;
        backdrop-filter: blur(28px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 16px !important;
        padding: 12px 18px !important;
        margin-top: 14px !important;
        margin-bottom: 8px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45) !important;
        max-width: 440px !important;
    }

    .file-icon-box {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        background: linear-gradient(135deg, rgba(167, 139, 250, 0.25) 0%, rgba(99, 102, 241, 0.25) 100%);
        border: 1px solid rgba(167, 139, 250, 0.35);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        flex-shrink: 0;
    }

    .file-info-col {
        display: flex;
        flex-direction: column;
        gap: 2px;
        flex-grow: 1;
        overflow: hidden;
    }

    .file-name-title {
        font-size: 14px;
        font-weight: 600;
        color: #f5f5f7;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .file-size-subtitle {
        font-size: 11.5px;
        color: #8e8e93;
    }

    /* =======================================================
       PRETTY CHAT INPUT & FROSTED BOTTOM DOCK
       Eliminates all red/orange outlines and overlap issues
       ======================================================= */

    /* Frosted Bottom Dock Bar */
    [data-testid="stBottom"] {
        background: linear-gradient(180deg, rgba(6, 6, 9, 0) 0%, rgba(6, 6, 9, 0.72) 20%, rgba(6, 6, 9, 0.95) 55%, #060609 100%) !important;
        backdrop-filter: blur(28px) saturate(180%) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding-top: 16px !important;
        padding-bottom: 22px !important;
        padding-left: 36px !important;
        padding-right: 36px !important;
        z-index: 100 !important;
    }

    [data-testid="stBottom"] > div {
        background: transparent !important;
        max-width: 100% !important;
        width: 100% !important;
        padding: 0 !important;
    }

    /* Bottom Chat Input: Single sleek pill without any hover border or double outlines */
    [data-testid="stChatInput"] {
        border-radius: 999px !important;
        background: rgba(22, 22, 30, 0.92) !important;
        backdrop-filter: blur(36px) saturate(190%) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        box-shadow: none !important;
        padding: 4px 10px 4px 20px !important;
        margin-bottom: 6px !important;
        width: 100% !important;
        max-width: 100% !important;
        outline: none !important;
    }

    /* Never add any hover border or focus border rings */
    [data-testid="stChatInput"]:hover,
    [data-testid="stChatInput"]:focus,
    [data-testid="stChatInput"]:focus-within {
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        box-shadow: none !important;
        outline: none !important;
    }

    /* Force all inner elements, divs, and textareas to NEVER show any inner or hover border */
    [data-testid="stChatInput"] div,
    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInput"] [data-baseweb],
    [data-testid="stChatInput"] *:hover,
    [data-testid="stChatInput"] *:focus,
    [data-testid="stChatInput"] *:focus-within,
    [data-testid="stChatInput"] *:active {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    /* Inner Textarea */
    [data-testid="stChatInput"] textarea {
        color: #f5f5f7 !important;
        font-size: 14.5px !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Plus Jakarta Sans', sans-serif !important;
        line-height: 1.5 !important;
        padding-top: 6px !important;
        padding-bottom: 6px !important;
        background: transparent !important;
        border: none !important;
        resize: none !important;
    }

    /* Completely hide any placeholder / hover text */
    [data-testid="stChatInput"] textarea::placeholder,
    [data-testid="stChatInput"] textarea::-webkit-input-placeholder,
    [data-testid="stChatInput"] textarea::-moz-placeholder {
        color: transparent !important;
        opacity: 0 !important;
        font-size: 0 !important;
    }

    /* Send Button inside stChatInput */
    [data-testid="stChatInput"] button {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 50% !important;
        width: 34px !important;
        height: 34px !important;
        min-height: 34px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: #d1d5db !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        padding: 0 !important;
        margin-left: 6px !important;
    }

    [data-testid="stChatInput"] button:hover {
        background: #ffffff !important;
        color: #000000 !important;
        border-color: #ffffff !important;
        transform: scale(1.06) !important;
        box-shadow: 0 0 16px rgba(255, 255, 255, 0.35) !important;
    }

    [data-testid="stChatInput"] button svg {
        fill: currentColor !important;
        stroke: currentColor !important;
        width: 15px !important;
        height: 15px !important;
    }

    /* Streamlit Buttons: Frosted Glass Cards & Apple Action Style */
    .stButton > button, .stDownloadButton > button {
        background: rgba(18, 18, 24, 0.65) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        color: #f5f5f7 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 12px 18px !important;
        text-align: left !important;
        white-space: pre-wrap !important;
        line-height: 1.45 !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        background: rgba(28, 28, 38, 0.85) !important;
        border-color: rgba(180, 140, 255, 0.35) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 32px rgba(100, 60, 200, 0.18) !important;
        color: #ffffff !important;
    }

    .stButton > button[kind="primary"] {
        background: #f5f5f7 !important;
        color: #000000 !important;
        font-weight: 600 !important;
        border-radius: 999px !important;
        padding: 8px 18px !important;
        text-align: center !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.25) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: #ffffff !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 24px rgba(255, 255, 255, 0.4) !important;
    }

    /* Sidebar buttons specifically */
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] .stDownloadButton > button {
        border-radius: 10px !important;
        padding: 8px 14px !important;
        font-size: 12px !important;
        text-align: center !important;
    }
</style>
"""

st.markdown(
    css_code.replace("__AURORA_BG_B64__", aurora_bg_b64),
    unsafe_allow_html=True,
)


# ----------------- Minimal Sidebar (macOS style) -----------------
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 24px; padding-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,0.06);">
            <div style="width: 28px; height: 28px; border-radius: 7px; background: #ffffff; color: #000; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px;">
                N
            </div>
            <div>
                <div style="font-weight: 600; font-size: 14px; color: #f5f5f7;">Nishan</div>
                <div style="font-size: 11px; color: #86868b;">Personal Assistant</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("✨ Replay Intro", use_container_width=True):
        st.session_state.intro_active = True
        st.query_params.clear()
        st.rerun()

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_action = None
        st.session_state.continuation_context = None
        st.rerun()

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    with st.expander("📁 Notes & Files"):
        saved_files = [f for f in os.listdir(NOTES_DIR) if not f.startswith(".")]
        if not saved_files:
            st.caption("No notes saved yet. Tell the assistant to take a note or create a document!")
        else:
            for fname in sorted(saved_files):
                fpath = os.path.join(NOTES_DIR, fname)
                is_docx = fname.endswith(".docx")
                st.caption(f"**{'📘 ' if is_docx else '📄 '}{fname}**")
                try:
                    with open(fpath, "rb") as f:
                        file_data = f.read()
                    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if is_docx else "text/plain"
                    st.download_button(
                        label=f"Download {fname}",
                        data=file_data,
                        file_name=fname,
                        mime=mime,
                        key=f"sb_dl_{fname}",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.caption(f"Error reading {fname}: {e}")

    with st.expander("⚙️ Settings"):
        effective_api_key = os.getenv("GEMINI_API_KEY", "")
        model_choice = st.selectbox(
            "Model",
            options=["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"],
            index=0,
            key="selected_model",
        )
        st.caption("Auto-execution enabled. Actions run immediately.")


# ----------------- Chat Input & Action Handling -----------------
active_input = None
if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
    active_input = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

# Empty placeholder so no hover or placeholder text appears in the search bar
user_input = st.chat_input("")
if not user_input and active_input:
    user_input = active_input

# Check if there is an active conversation or pending input
has_conversation = bool(st.session_state.messages) or bool(user_input)

# ----------------- View A: Hero & Prompt Starters (Only when conversation is empty) -----------------
if not has_conversation:
    col_pad1, col_center, col_pad2 = st.columns([1, 6, 1])
    with col_center:
        st.markdown(
            """
            <div class="hero-section">
                <div class="announcement-pill">
                    <span class="pill-badge">New</span>
                    <span>Autonomous Workspace & Thinking Canvas</span>
                    <span style="opacity: 0.5;">→</span>
                </div>
                <h1 class="hero-title">Think Clearly.<br/><span class="hero-gradient-text">Create Infinitely.</span></h1>
                <p class="hero-subtitle">Your private space to capture thoughts, synthesize ideas, and turn notes into action.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 4 Clean, Functional Prompt Starter Cards
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("📄  Create a Word Doc\n\nGenerate and download a full Word document on Home", key="btn_card_1", use_container_width=True):
                st.session_state.pending_prompt = "Can you make a Word doc for the topic Home with structured sections?"
                st.rerun()

            if st.button("📝  Capture a Note\n\nSave my thoughts and today's key priorities", key="btn_card_2", use_container_width=True):
                st.session_state.pending_prompt = "Save a note: Today's priority is completing the project deployment and refining the user interface."
                st.rerun()

        with col_c2:
            if st.button("💡  Brainstorm Ideas\n\nExplore creative architecture and product concepts", key="btn_card_3", use_container_width=True):
                st.session_state.pending_prompt = "Brainstorm 3 innovative, high-impact features for expanding this AI workspace."
                st.rerun()

            if st.button("📁  Review Workspace Notes\n\nInspect and summarize all notes saved on disk", key="btn_card_4", use_container_width=True):
                st.session_state.pending_prompt = "What notes do I currently have saved in my workspace? Please summarize them."
                st.rerun()

        st.markdown(
            """
            <div class="capabilities-bar">
                <span>✦ Instant Recall</span>
                <span class="dot-sep">•</span>
                <span>⚡ Gemini 3.5 Engine</span>
                <span class="dot-sep">•</span>
                <span>📁 Word Docs (.docx)</span>
                <span class="dot-sep">•</span>
                <span>🔒 Local-First Privacy</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ----------------- View B: Active Chat Conversation -----------------
else:
    # Render all historical messages
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(f'<span class="user-marker"></span>{msg["content"]}', unsafe_allow_html=True)
        else:
            with st.chat_message("assistant"):
                st.markdown(f'<span class="ai-marker"></span>{msg["content"]}', unsafe_allow_html=True)
                file_path = msg.get("file_path")
                if file_path and os.path.exists(file_path):
                    fname = msg.get("filename", os.path.basename(file_path))
                    is_docx = fname.endswith(".docx")
                    file_size_kb = round(os.path.getsize(file_path) / 1024, 1)
                    type_label = "Microsoft Word Document (.docx)" if is_docx else "Markdown Document"
                    icon_emoji = "📘" if is_docx else "📄"

                    st.markdown(
                        f"""
                        <div class="file-download-card">
                            <div class="file-icon-box">{icon_emoji}</div>
                            <div class="file-info-col">
                                <div class="file-name-title">{fname}</div>
                                <div class="file-size-subtitle">{type_label} • {file_size_kb} KB</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if is_docx else "text/markdown"
                    st.download_button(
                        label=f"📥 Download {fname}",
                        data=file_bytes,
                        file_name=fname,
                        mime=mime,
                        key=f"dl_msg_{i}_{fname}",
                    )
                elif "saved_note" in msg and msg["saved_note"]:
                    st.markdown(
                        f"""
                        <div class="saved-pill">
                            <span>✓</span>
                            <span>{msg['saved_note']}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # Execution on New User Input
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(f'<span class="user-marker"></span>{user_input}', unsafe_allow_html=True)

        # Modern Animated Thinking Bubble (ChatGPT & Apple Style)
        thinking_slot = st.empty()
        thinking_slot.markdown(
            """
            <div class="thinking-container">
                <span class="ai-marker" style="display:none;"></span>
                <div class="thinking-bubble">
                    <div class="thinking-dots">
                        <span class="pulse-dot"></span>
                        <span class="pulse-dot"></span>
                        <span class="pulse-dot"></span>
                    </div>
                    <span class="thinking-label">Thinking...</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        try:
            effective_api_key = os.getenv("GEMINI_API_KEY", "")
            chosen_model = st.session_state.get("selected_model", "gemini-3.5-flash-lite")
            agent = AIAgent(
                api_key=effective_api_key,
                model_name=chosen_model,
                require_approval=False,  # Auto-allow without permission prompts
            )
            history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]
            ]
            result = agent.run(user_input, conversation_history=history)

            # Clear the thinking bubble before rendering response
            thinking_slot.empty()

            # Check if a file was created
            file_info = getattr(result, "file_info", None)
            file_path = file_info.get("file_path") if file_info else None
            filename = file_info.get("filename") if file_info else None
            doc_type = file_info.get("doc_type") if file_info else None

            saved_label = None
            for step in result.explanation_trail:
                if "Verified file created on disk" in step or "Output verified" in step:
                    saved_label = "File saved to disk"

            with st.chat_message("assistant"):
                st.markdown(f'<span class="ai-marker"></span>{result.response_text}', unsafe_allow_html=True)
                if file_path and os.path.exists(file_path):
                    is_docx = filename.endswith(".docx")
                    file_size_kb = round(os.path.getsize(file_path) / 1024, 1)
                    type_label = "Microsoft Word Document (.docx)" if is_docx else "Document File"
                    icon_emoji = "📘" if is_docx else "📄"

                    st.markdown(
                        f"""
                        <div class="file-download-card">
                            <div class="file-icon-box">{icon_emoji}</div>
                            <div class="file-info-col">
                                <div class="file-name-title">{filename}</div>
                                <div class="file-size-subtitle">{type_label} • {file_size_kb} KB</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    with open(file_path, "rb") as f:
                        file_bytes = f.read()

                    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if is_docx else "text/markdown"
                    st.download_button(
                        label=f"📥 Download {filename}",
                        data=file_bytes,
                        file_name=filename,
                        mime=mime,
                        key=f"dl_live_{filename}",
                    )
                elif saved_label:
                    st.markdown(
                        """
                        <div class="saved-pill">
                            <span>✓</span>
                            <span>Saved to Notes</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.session_state.messages.append({
                "role": "assistant",
                "content": result.response_text,
                "saved_note": saved_label,
                "file_path": file_path,
                "filename": filename,
                "doc_type": doc_type,
            })

        except Exception as e:
            thinking_slot.empty()
            err_msg = f"Something went wrong: {str(e)}"
            with st.chat_message("assistant"):
                st.markdown(f'<span class="ai-marker"></span>{err_msg}', unsafe_allow_html=True)
            st.session_state.messages.append({
                "role": "assistant",
                "content": err_msg,
            })

