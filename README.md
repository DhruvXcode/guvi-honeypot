# 🍯 Agentic Honey-Pot API

> **AI-powered scam detection & intelligence extraction system** — An intelligent honeypot that engages phone/SMS/WhatsApp scammers using a convincing victim persona, detects scam patterns in real-time, and extracts critical intelligence (phone numbers, bank accounts, UPI IDs, phishing links, and more).

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
| **Primary LLM** | Groq (Llama 3.3 70B) |
| **Fallback LLM** | Cerebras (Llama 3.3 70B) |
| **Intelligence Extraction** | Regex-based (bank accounts, UPI, phones, emails, URLs, case IDs, policy/order numbers) |
| **Scam Detection** | 4-layer: URL legitimacy → automated msg detection → regex patterns → LLM analysis |
| **Deployment** | Render (Docker/Python) |

## 🔧 Setup Instructions

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/guvi-honeypot.git
cd guvi-honeypot
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
- `HONEYPOT_API_KEY` — API key for authentication
- `GROQ_API_KEY` — Groq API key (primary LLM)
- `CEREBRAS_API_KEY` — Cerebras API key (fallback LLM)
- `GUVI_CALLBACK_URL` — GUVI callback endpoint

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
  "reply": "hai ram!! mera account block ho gaya?? ...",
  "sessionId": "unique-session-id",
  "scamDetected": true,
  "scamType": "account_suspension_scam",
  "confidenceLevel": 0.92,
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
  "agentNotes": "SCAM DETECTED (92% confidence). Type: account_suspension_scam. Red flags identified: Urgency Pressure, Threat Intimidation, Credential Request..."
}
```

## 🧠 Approach

### 1. Scam Detection (4-Layer)
- **Layer 1:** URL legitimacy check against known domains
- **Layer 2:** Automated message pattern detection (policy/order notifications)
- **Layer 3:** Strong scam indicator regex (urgency + threats + credential requests)
- **Layer 4:** LLM contextual analysis with Groq/Cerebras fallback

### 2. Intelligence Extraction
- Regex-based extraction for: phone numbers (Indian format), bank accounts, UPI IDs, phishing URLs, email addresses, case/reference IDs, policy numbers, order numbers
- Email-first extraction to prevent UPI false positives
- Canonical phone format (+91-XXXXXXXXXX) for maximum evaluator compatibility
- Cumulative extraction across entire conversation history

### 3. Agent Persona (Conversation Quality)
- **Kamala Devi** — 67-year-old retired teacher persona
- Hinglish responses (Hindi in English script) for authenticity
- Strategic investigative questions about scammer identity, company, credentials
- Explicit red flag identification and emotional reactions
- Anti-repetition system prevents duplicate responses
- Code-enforced follow-up questions on every turn

### 4. Engagement Strategy
- Keep scammers engaged for 8+ turns through confusion, cooperation, and family excuses
- Guaranteed engagement duration floor (240s) when conversation threshold reached
- Aggressive LLM timeouts (Groq: 8s, Cerebras: 10s) with template fallbacks

### 5. Resilience
- Dual LLM provider (Groq primary, Cerebras fallback)
- Template-based fallback responses when both LLMs fail
- Global exception handler ensures valid response on every request
- Idempotent callback system — fires on every eligible turn

## 📁 Project Structure

```
├── main.py                    # FastAPI app entry point
├── app/
│   ├── config.py              # Environment configuration
│   ├── models.py              # Pydantic request/response models
│   ├── routes/
│   │   └── honeypot.py        # Main endpoint handler
│   └── services/
│       ├── agent.py           # LLM-based response generation
│       ├── callback.py        # GUVI callback service
│       ├── intelligence.py    # Regex intelligence extraction
│       └── scam_detector.py   # Multi-layer scam detection
├── tests/                     # Test scripts and simulator
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

## 📄 License

MIT License
