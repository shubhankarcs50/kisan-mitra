# 🌿 Kisan Mitra — Natural Farming Voice Consultant

> A voice-enabled AI assistant helping Indian farmers transition to natural and organic farming through crop disease identification and multilevel farming education.


## 🎯 Problem Statement

Farmers transitioning to natural farming lack instant, accessible expert guidance on:
- Identifying crop diseases and getting organic remedies
- Understanding multilevel/multi-layer cropping strategies
- Accessing knowledge in their own language (Hindi/Hinglish)

## ✨ Features Built

### 🔍 Feature 1: Disease Identification & Organic Treatment
- Farmer describes or **uploads a photo** of their crop problem
- AI identifies the disease/pest and suggests **only organic remedies**
- Solutions use locally available materials: neem, cow dung, garlic, turmeric
- Structured response: Problem → Remedy → Precautions → Timing

### 📚 Feature 2: Natural Farming Education (Multilevel Cropping)
- Explains bahustar kheti (multi-tier farming), companion planting, crop rotation
- Real Indian crop examples: gehun, dhaan, tamatar, arhar, ganna
- Practical step-by-step guidance farmers can implement immediately
- Covers ZBNF, Jeevamrut, Panchgavya preparation

### 🔊 Shared Features
- **Voice output** — answers read aloud in Hindi via gTTS
- **Hindi + English** mixed responses (Hinglish) for maximum accessibility
- **Quick query chips** — one-tap sample questions for easy demo
- **Streaming responses** — real-time answer generation
- **Conversation memory** — remembers last 4 turns of context

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit (Python) |
| AI Model | Claude Sonnet (Anthropic API) |
| Text-to-Speech | gTTS (Google Text-to-Speech) |
| Image Input | Anthropic Vision API (base64) |
| Deployment | Streamlit Cloud |
| Language | Python 3.10+ |

---

## 🧠 Prompt Design

### Design Philosophy
- **Role-specific system prompts** — separate prompts for Disease ID vs Education
- **Structured output format** — emoji-labeled sections for scannability on mobile
- **Hinglish by design** — prompts instruct the model to mix Hindi/English naturally
- **Organic-only guardrail** — disease prompt strictly forbids chemical recommendations
- **Farmer-first language** — prompts specify using local crop names, affordable materials

### Disease Identification Prompt Strategy
```
Structured as: Problem → Organic Remedies (with steps) → Precautions → Timing
Guardrail: "Suggest ONLY organic/natural remedies — no synthetic pesticides"
Localization: "Use local, low-cost materials: neem, cow dung, garlic, turmeric, ash"
```

### Education Prompt Strategy
```
Structured as: Concept → Practical Example → Benefits → How to Start
Grounding: "Always include quantities, spacing, and timing"
Economic hook: "Connect every concept to economic benefit"
```

---

## 🌍 Localization Approach

- **Language**: Hinglish (Hindi + English blend) — matches how rural farmers actually speak
- **Font**: Noto Sans + Noto Sans Devanagari — supports both scripts
- **Terminology**: Uses local farming terms (fasal, khet, beej, khaad, keede)
- **Examples**: All crop examples are Indian varieties relevant to the target region
- **TTS**: gTTS Hindi voice — farmers can listen even if they struggle to read

---

## 🚀 Running Locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/kisan-mitra
cd kisan-mitra

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# 4. Run
streamlit run app.py
```

## ☁️ Deploy on Streamlit Cloud (Free)

1. Push this repo to GitHub (must be public)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repo → set `app.py` as main file
4. Under **Advanced settings → Secrets**, add:
   ```toml
   ANTHROPIC_API_KEY = "your-key-here"
   ```
5. Click Deploy — live URL in ~2 minutes!

---

## 📁 Project Structure

```
kisan-mitra/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .streamlit/
│   ├── config.toml                 # Theme (green palette)
│   └── secrets.toml.template       # API key template
└── README.md
```

---

## 🎨 Design Decisions

- **Green palette** (#1D9E75) — evokes nature, farming, growth
- **Wide layout** — better for desktop/smartboard display
- **Chat bubble UI** — familiar WhatsApp-like interface farmers already know
- **Quick chips** — removes typing barrier; one tap to ask a question
- **Sidebar mode toggle** — clean separation between two features

---

*Built with 🌿 for Indian farmers transitioning to natural farming*
