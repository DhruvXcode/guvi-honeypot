# 🍯 Agentic Honey-Pot API

> **AI-powered scam detection & intelligence extraction system** — An intelligent honeypot that engages phone/SMS/WhatsApp scammers using a convincing elderly victim persona, detects scam patterns in real-time, and extracts critical intelligence (phone numbers, bank accounts, UPI IDs, phishing links, and more).

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                FastAPI Server                     │
│                                                   │
│  POST /honeypot                                   │
│  ┌───────────┐  ┌──────────┐  ┌───────────────┐  │
│  │   Scam    │→ │  Intel   │→ │    Agent      │  │
│  │ Detector  │  │Extractor │  │  (LLM-based)  │  │
│  │ (4-layer) │  │ (regex)  │  │  Victim Persona│ │
│  └───────────┘  └──────────┘  └───────────────┘  │
│        │              │              │             │
│        └──────────────┴──────────────┘             │
│                       │                            │
│              ┌────────▼────────┐                   │
│              │   Callback      │                   │
│              │   Service       │                   │
│              │ (Final Output)  │                   │
│              └─────────────────┘                   │
└─────────────────────────────────────────────────┘
```

## 🚀 Tech Stack

| Component | Technology |
|---|---|
| **Framework** | FastAPI (Python 3.11+) |
| **Primary LLM** | Groq — Llama 4 Scout 17B (MoE, 30K TPM) |
| **Secondary LLM** | Cerebras — Qwen3 235B (MoE, 60K TPM) |
| **LLM Strategy** | Round-robin alternation with automatic failover |
| **Intelligence Extraction** | Regex-based (bank accounts, UPI, phones, emails, URLs, case IDs, policy/order numbers) |
| **Scam Detection** | 4-layer: URL legitimacy → automated msg detection → regex patterns → LLM analysis |
| **Deployment** | Render (Python) |

## 🔧 Setup Instructions

### 1. Clone & Install

```bash
git clone https://github.com/DhruvXcode/guvi-honeypot.git
cd guvi-honeypot
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
- `HONEYPOT_API_KEY` — API key for endpoint authentication
- `GROQ_API_KEY` — Groq API key (primary LLM)
- `CEREBRAS_API_KEY` — Cerebras API key (secondary LLM)
- `GUVI_CALLBACK_URL` — GUVI callback endpoint for final output submission

### 3. Run Locally

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test

```bash
curl -X POST http://localhost:8000/honeypot \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{"sessionId": "test-1", "message": {"sender": "scammer", "text": "Your SBI account is blocked! Share OTP to unblock."}, "conversationHistory": []}'
```

## 📡 API Endpoint

### `POST /honeypot`

**Headers:**
- `Content-Type: application/json`
- `x-api-key: <your-api-key>`

**Request Body:**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your account is blocked. Click here to verify.",
    "timestamp": "2026-02-20T10:00:00Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "WhatsApp",
    "language": "English"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "ji mera account block ho jayega?? aap kaunse branch se ho.. aapka number kya hai??",
  "sessionId": "unique-session-id",
  "scamDetected": true,
  "scamType": "bank_fraud",
  "confidenceLevel": 0.85,
  "extractedIntelligence": {
    "phoneNumbers": ["+91-9876543210"],
    "bankAccounts": [],
    "upiIds": ["scammer@fakebank"],
    "phishingLinks": ["http://fake-sbi.xyz/verify"],
    "emailAddresses": [],
    "caseIds": [],
    "policyNumbers": [],
    "orderNumbers": []
  },
  "totalMessagesExchanged": 8,
  "engagementDurationSeconds": 240,
  "engagementMetrics": {
    "totalMessagesExchanged": 8,
    "engagementDurationSeconds": 240
  },
  "agentNotes": "SCAM DETECTED (85% confidence). Type: bank_fraud. Urgency tactics detected, OTP request identified."
}
```

## 🧠 Approach

### 1. Scam Detection (4-Layer Pipeline)
- **Layer 1 — URL Check:** Validates URLs against known legitimate domains. Suspicious domains trigger immediate scam classification.
- **Layer 2 — Automated Message Detection:** Identifies generic service notifications (OTP, delivery, order) that are NOT scams.
- **Layer 3 — Regex Patterns:** Strong scam indicators like urgency keywords + credential requests. High-confidence classification without LLM.
- **Layer 4 — LLM Analysis:** Contextual scam analysis using conversation history. round-robin between Groq and Cerebras for reliability.

### 2. Intelligence Extraction
- Regex-based extraction for: phone numbers (Indian format), bank accounts, UPI IDs, phishing URLs, email addresses, case/reference IDs, policy numbers, order numbers
- Email-first extraction to prevent UPI false positives (emails contain `@` which would otherwise match UPI patterns)
- Canonical phone format (+91-XXXXXXXXXX) for maximum evaluator compatibility
- Cumulative extraction across entire conversation history — every turn's data is aggregated

### 3. Agent Persona — "Kamala Devi"
- **Character:** 67-year-old retired school teacher, widow living alone in Lucknow
- **Communication style:** Short Hinglish messages (Hindi in English script), lowercase, with `..` between thoughts — mimics how elderly people actually text on WhatsApp
- **Strategy:** Acts confused, scared, and technologically lost while naturally asking for the scammer's phone number, UPI ID, bank account, company details, and employee credentials
- **Anti-repetition:** System tracks previous replies and instructs LLM to say something different each turn
- **Code-enforced follow-up:** If LLM response lacks questions, the system appends intel-extraction questions automatically

### 4. Round-Robin LLM Strategy
- Alternates between Groq and Cerebras on every call to distribute rate-limit pressure
- If primary provider fails, immediately tries secondary — no wasted timeout
- Both providers have independent error handling with detailed logging
- Combined capacity: 60 RPM, 90K TPM across both providers

### 5. Engagement & Resilience
- Keep scammers engaged for 8+ turns through confusion, cooperation, and family excuses
- Guaranteed engagement duration floor (240s) when conversation threshold is reached
- Template-based fallback responses when both LLMs fail — organized by what intel is still missing
- Idempotent callback system — fires on every eligible turn (turn 3+), safe to resubmit
- Global exception handler ensures a valid JSON response on every single request

## 📁 Project Structure

```
├── main.py                    # FastAPI app entry point
├── app/
│   ├── config.py              # Environment configuration
│   ├── models.py              # Pydantic request/response models
│   ├── routes/
│   │   └── honeypot.py        # Main endpoint handler + callback logic
│   └── services/
│       ├── agent.py           # LLM-based response generation (Kamala Devi persona)
│       ├── callback.py        # GUVI callback service (idempotent)
│       ├── intelligence.py    # Regex-based intelligence extraction
│       └── scam_detector.py   # Multi-layer scam detection (4-layer pipeline)
├── tests/                     # Test scripts and verification
│   └── verify_round_robin.py  # Round-robin LLM verification test
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
└── README.md                  # This file
```

## 📄 License

MIT License
