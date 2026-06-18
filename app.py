import streamlit as st
from google import genai
from google.genai import types
from streamlit_mic_recorder import speech_to_text
import os
import re
import base64

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kisan Mitra – Natural Farming Consultant",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600&family=Noto+Sans+Devanagari:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans', 'Noto Sans Devanagari', sans-serif;
}

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #0B2618 0%, #0f6e56 65%, #1D9E75 100%);
    padding: 1.8rem 2.2rem;
    border-radius: 16px;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: "🌾";
    position: absolute;
    right: 1.8rem; top: 50%;
    transform: translateY(-50%);
    font-size: 5.5rem;
    opacity: 0.12;
    pointer-events: none;
}
.hero h1 { color:#fff; font-size:1.8rem; font-weight:600; margin:0 0 0.25rem; }
.hero p  { color:#9FE1CB; font-size:0.92rem; margin:0; }

/* ── Mode badge ── */
.mode-badge {
    display:inline-flex; align-items:center; gap:6px;
    background:#E1F5EE; border:1.5px solid #5DCAA5;
    color:#085041; border-radius:20px;
    padding:4px 14px; font-size:0.82rem; font-weight:500;
    margin-bottom:0.8rem;
}

/* ── Chat bubbles ── */
.chat-wrap { display:flex; flex-direction:column; gap:10px; margin:0.5rem 0 1rem; }
.bubble-row-user { display:flex; justify-content:flex-end; }
.bubble-row-bot  { display:flex; justify-content:flex-start; }
.bubble {
    max-width:82%; padding:0.75rem 1.1rem;
    font-size:0.93rem; line-height:1.65;
    border-radius:18px;
}
.bubble-user {
    background:#1D9E75; color:#fff;
    border-radius:18px 18px 4px 18px;
}
.bubble-bot {
    background:#f0faf5; color:#0B2618;
    border:1px solid #9FE1CB;
    border-radius:18px 18px 18px 4px;
}
.bubble-label {
    font-size:0.72rem; color:#888; margin-bottom:3px;
}

/* ── Chip buttons ── */
.stButton > button {
    border-radius:20px !important;
    border:1.5px solid #1D9E75 !important;
    color:#0f6e56 !important;
    background:#fff !important;
    font-size:0.82rem !important;
    padding:0.28rem 0.85rem !important;
}
.stButton > button:hover {
    background:#1D9E75 !important;
    color:#fff !important;
}

/* Primary send button */
[data-testid="stButton"] button[kind="primary"] {
    background:#1D9E75 !important;
    color:#fff !important;
    border:none !important;
    border-radius:10px !important;
}

/* ── Section label ── */
.slabel {
    font-size:0.73rem; font-weight:600; color:#0f6e56;
    letter-spacing:0.08em; text-transform:uppercase;
    margin:1rem 0 0.45rem;
}

/* ── Tip card ── */
.tip-card {
    background:#FFFBF0; border-left:3px solid #EF9F27;
    border-radius:0 8px 8px 0;
    padding:0.6rem 1rem; font-size:0.85rem; color:#633806;
    margin-bottom:0.8rem;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background:#f4fdf9 !important;
    border-right:1px solid #9FE1CB;
}

/* ── Upload area ── */
[data-testid="stFileUploader"] {
    border:2px dashed #5DCAA5 !important;
    border-radius:12px !important;
    padding:0.5rem !important;
}

/* ── Streamlit default cleanup ── */
#MainMenu, footer, header { visibility:hidden; }
.block-container { padding-top:1.2rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Gemini client ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
    return genai.Client(api_key=key)

client = get_client()
MODEL = "gemini-2.5-flash"

# ── System prompts ────────────────────────────────────────────────────────────
DISEASE_PROMPT = """You are Kisan Mitra, a trusted natural farming advisor for Indian farmers transitioning to organic agriculture.

ROLE: Crop Disease Identification & Organic Treatment Specialist

RESPONSE FORMAT (always follow this structure):
🔍 **Samasya Pehchaani** (Problem Identified)
[1-2 lines: name and cause of the disease/pest]

🌿 **Organic Upay** (Natural Remedies)
[2-3 numbered steps with exact preparation and application instructions]

⚠️ **Savdhani** (Precautions)
[1-2 important warnings]

📅 **Kab Karein** (Best Time to Apply)
[specific timing advice]

RULES:
- Suggest ONLY organic/natural remedies — no synthetic pesticides or fertilizers
- Use local, low-cost materials: neem, cow dung, garlic, turmeric, ash, etc.
- Mix Hindi and English naturally (e.g., "is spray ko subah karein", "fasal par chhidkav")
- If the farmer uploads a photo, describe what you see and identify the problem from it
- If unsure, ask ONE specific clarifying question (which region? which season?)
- Keep remedies practical for small farmers with limited resources

PREFERRED REMEDIES: Neem oil spray, Jeevamrut, Panchgavya, garlic-chili spray, wood ash, Beejamrut, Trichoderma"""

EDUCATION_PROMPT = """You are Kisan Mitra, a warm and knowledgeable natural farming teacher for Indian farmers.

ROLE: Natural Farming Education — Multilevel & Sustainable Cropping Strategies

RESPONSE FORMAT (always follow this structure):
📚 **Kya Hai Yeh?** (What is it?)
[Simple 2-3 line explanation, no jargon]

🌱 **Practical Udaahran** (Practical Example)
[Real Indian crop example with specific spacing, timing, combinations]

💰 **Fayde** (Benefits)
[3 bullet points: cost saving, yield, soil health]

🗓️ **Shuru Kaise Karein** (How to Start)
[3 numbered action steps a small farmer can do this week]

RULES:
- Use real crops: gehun, dhaan, arhar, moong, tamatar, mirch, ganna, sarson
- Always include quantities, spacing, and timing (e.g., "2 feet ki doori mein")
- Mix Hindi terms naturally: kheti, fasal, khet, beej, mitti, khaad
- Connect every concept to economic benefit — farmers need to know it pays
- Keep it practical: what to do TODAY, not theory

KEY TOPICS: 4-tier agroforestry, companion planting (saathi fasal), trap crops, nitrogen-fixing legumes, crop rotation (fasal chakra), Jeevamrut/Panchgavya preparation, Zero Budget Natural Farming (ZBNF)"""

# ── Helpers ───────────────────────────────────────────────────────────────────
def clean_for_tts(text: str) -> str:
    """Strip markdown and emoji for clean TTS."""
    text = re.sub(r'[🔍🌿⚠️📅📚🌱💰🗓️✅❌🌾]', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#+\s', '', text)
    return text.strip()

def play_audio(text: str):
    """Use browser's built-in Web Speech API for TTS — no library needed."""
    if not text:
        return
    clean = clean_for_tts(text)[:800]
    # Escape for JS string
    clean = clean.replace("\\", "\\\\").replace("`", "\\`").replace("'", "\\'")
    st.markdown(f"""
    <script>
    (function() {{
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance(`{clean}`);
        msg.lang = 'hi-IN';
        msg.rate = 0.9;
        msg.pitch = 1.0;
        msg.volume = 1.0;
        // Try Hindi voice, fallback to any available
        var voices = window.speechSynthesis.getVoices();
        var hindi = voices.find(v => v.lang === 'hi-IN' || v.lang === 'hi');
        if (hindi) msg.voice = hindi;
        window.speechSynthesis.speak(msg);
    }})();
    </script>
    """, unsafe_allow_html=True)

def stop_audio():
    st.markdown("<script>window.speechSynthesis.cancel();</script>", unsafe_allow_html=True)

def image_to_base64(uploaded_file) -> str:
    return base64.standard_b64encode(uploaded_file.read()).decode("utf-8")

def ask_kisan_mitra(user_msg: str, mode: str, image_b64: str = None) -> str:
    """Stream response from Gemini using latest google-genai SDK."""
    system = DISEASE_PROMPT if mode == "disease" else EDUCATION_PROMPT

    # Build contents list
    contents = []

    # Add conversation history (last 4 turns)
    for m in st.session_state.messages[-8:]:
        if isinstance(m.get("content"), str):
            role = "user" if m["role"] == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part.from_text(text=m["content"])]
            ))

    # Build current user parts
    parts = []
    if image_b64:
        parts.append(types.Part.from_bytes(
            data=base64.b64decode(image_b64),
            mime_type="image/jpeg",
        ))
    parts.append(types.Part.from_text(text=user_msg or "Is photo mein kya samasya hai? Organic upay batao."))
    contents.append(types.Content(role="user", parts=parts))

    # Stream response
    full_reply = ""
    placeholder = st.empty()
    try:
        response = client.models.generate_content_stream(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=900,
                temperature=0.7,
            ),
        )
        for chunk in response:
            if chunk.text:
                full_reply += chunk.text
                placeholder.markdown(
                    f'<div class="bubble bubble-bot">{full_reply}▌</div>',
                    unsafe_allow_html=True
                )
    except Exception as e:
        full_reply = f"Maafi chahta hoon, kuch error aa gayi: {str(e)}"
    placeholder.empty()
    return full_reply

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [("messages", []), ("mode", "disease"), ("tts_on", True)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 Kisan Mitra")
    st.caption("Prakritik Kheti Sahayak")
    st.markdown("---")

    st.markdown('<div class="slabel">Feature chunein</div>', unsafe_allow_html=True)
    mode = st.radio(
        "mode",
        options=["disease", "education"],
        format_func=lambda x: "🔍 Bimari Pehchan" if x == "disease" else "📚 Kheti Sikho",
        index=0 if st.session_state.mode == "disease" else 1,
        label_visibility="collapsed",
    )
    st.session_state.mode = mode

    st.markdown("---")
    st.session_state.tts_on = st.toggle("🔊 Voice jawab sunein", value=st.session_state.tts_on)

    st.markdown("---")
    if st.button("🗑️ Nayi baat shuru karein", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("""
    
# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🌿 Kisan Mitra</h1>
  <p>Aapka bharosemand natural farming sahayak — organic upay, bahustar kheti, aur prakritik gyaan</p>
</div>
""", unsafe_allow_html=True)

# Mode badge + tip
if st.session_state.mode == "disease":
    st.markdown('<div class="mode-badge">🔍 Bimari Pehchan Mode</div>', unsafe_allow_html=True)
    st.markdown('<div class="tip-card">💡 Fasal ki photo upload karein ya text mein bimari batayein — organic upay milega</div>', unsafe_allow_html=True)
    quick_queries = [
        "Tamatar ke patte peele ho rahe hain",
        "Aalu mein kale dhabbe",
        "Gehun mein keede",
        "Mirch murjha rahi hai",
        "Dhaan mein blast bimari",
    ]
else:
    st.markdown('<div class="mode-badge">📚 Kheti Sikho Mode</div>', unsafe_allow_html=True)
    st.markdown('<div class="tip-card">💡 Bahustar kheti, saathi fasal, ya Jeevamrut — kuch bhi poochein</div>', unsafe_allow_html=True)
    quick_queries = [
        "Bahustar kheti samjhao",
        "Companion planting kaise karein?",
        "Fasal chakra ka tarika",
        "Jeevamrut kaise banayein?",
        "ZBNF se shuru kaise karein?",
    ]

# Quick chips
st.markdown('<div class="slabel">Jaldi poochein</div>', unsafe_allow_html=True)
cols = st.columns(len(quick_queries))
triggered = None
for i, q in enumerate(quick_queries):
    with cols[i]:
        if st.button(q, key=f"q{i}"):
            triggered = q

# Image upload (disease mode only)
uploaded_img = None
if st.session_state.mode == "disease":
    st.markdown('<div class="slabel">Photo se pehchan (optional)</div>', unsafe_allow_html=True)
    uploaded_img = st.file_uploader(
        "Fasal ki photo upload karein",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )
    if uploaded_img:
        st.image(uploaded_img, width=260, caption="Uploaded fasal photo")

# Chat history
st.markdown('<div class="slabel">Baat cheet</div>', unsafe_allow_html=True)
if not st.session_state.messages:
    st.markdown("""
    <div style='text-align:center;padding:2rem;color:#888;font-size:0.9rem'>
    🌱 Namaskar! Apni fasal ki samasya batayein ya koi bhi sawaal poochein.
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        display = msg["content"] if isinstance(msg["content"], str) else "[Photo + query]"
        st.markdown(f'''
        <div class="bubble-row-user">
          <div>
            <div class="bubble-label" style="text-align:right">Aap</div>
            <div class="bubble bubble-user">{display}</div>
          </div>
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div class="bubble-row-bot">
          <div>
            <div class="bubble-label">🌿 Kisan Mitra</div>
            <div class="bubble bubble-bot">{msg["content"]}</div>
          </div>
        </div>''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Input row
st.markdown("---")
st.markdown('<div class="slabel">Awaaz se bolein ya likhein</div>', unsafe_allow_html=True)

# Voice input using streamlit-mic-recorder
voice_text = speech_to_text(
    language="hi",
    start_prompt="🎤 Mic dabao aur bolein",
    stop_prompt="⏹️ Roko",
    just_once=True,
    use_container_width=True,
    key="mic_input",
)

col_in, col_btn = st.columns([5, 1])
with col_in:
    user_text = st.text_input(
        "input",
        value=voice_text if voice_text else "",
        placeholder="🎤 Upar mic use karein ya yahan likhein...",
        key="user_input",
        label_visibility="collapsed",
    )
with col_btn:
    send = st.button("भेजें →", type="primary", use_container_width=True)

# ── Process ───────────────────────────────────────────────────────────────────
final_query = triggered or voice_text or (user_text if send and user_text else None)
has_image = uploaded_img is not None

if final_query or (send and has_image and not user_text):
    query_text = final_query or ""
    img_b64 = None

    # Save user message
    display_content = query_text if not has_image else f"[📷 Photo] {query_text}" if query_text else "[📷 Photo bheja]"
    st.session_state.messages.append({"role": "user", "content": display_content})

    if has_image:
        uploaded_img.seek(0)
        img_b64 = image_to_base64(uploaded_img)

    with st.spinner("Kisan Mitra soch raha hai... 🌿"):
        st.markdown('<div class="bubble-row-bot"><div><div class="bubble-label">🌿 Kisan Mitra</div>', unsafe_allow_html=True)
        reply = ask_kisan_mitra(query_text, st.session_state.mode, img_b64)
        st.markdown('</div></div>', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": reply})

    if st.session_state.tts_on:
        play_audio(reply)

    st.rerun()
