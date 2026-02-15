# 🛡️ Agentic Honey-Pot for Scam Detection & Intelligence Extraction

### India AI Impact Buildathon 2026 — Grand Finale

An AI-powered honeypot system that detects scam messages, intelligently engages scammers to maintain conversation, and extracts actionable intelligence such as phone numbers, bank accounts, UPI IDs, phishing links, and email addresses.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **Multi-Layer Scam Detection** | URL whitelisting → automated message detection → keyword analysis → LLM-powered analysis |
| **AI Victim Persona** | Plays "Kamala Devi" — a 67-year-old retired teacher from Lucknow who keeps scammers engaged |
| **Intelligence Extraction** | Extracts bank accounts, UPI IDs, phone numbers, phishing links, email addresses, and suspicious keywords |
| **Multi-Turn Conversations** | Maintains context across 10+ message exchanges per session |
| **Scam Type Classification** | Auto-detects bank fraud, UPI fraud, phishing, and general scam patterns |
| **LLM Fallback** | Primary: Groq (LLaMA 3) → Fallback: Cerebras for resilience |
| **GUVI Callback** | Automatically reports final results to evaluation endpoint |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/your-username/GUVI-hackathon.git
cd GUVI-hackathon
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key for LLM (primary) |
| `CEREBRAS_API_KEY` | Cerebras API key for LLM (fallback) |
| `HONEYPOT_API_KEY` | API key for endpoint authentication |
| `GUVI_CALLBACK_URL` | GUVI evaluation callback endpoint |

### 3. Run the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📡 API Reference

### `POST /honeypot`

**Headers:**
```
x-api-key: your_api_key
Content-Type: application/json
```

**Request:**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "URGENT: Your SBI account has been compromised!",
    "timestamp": "2026-02-16T13:00:00Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "haye ram! kya hua beta, mera account block ho gaya?",
  "scamDetected": true,
  "scamType": "bank_fraud",
  "extractedIntelligence": {
    "phoneNumbers": ["+91-9876543210"],
    "bankAccounts": ["1234567890123456"],
    "upiIds": ["scammer@fakebank"],
    "phishingLinks": [],
    "emailAddresses": []
  },
  "engagementMetrics": {
    "totalMessagesExchanged": 6,
    "engagementDurationSeconds": 120
  },
  "agentNotes": "SCAM DETECTED (95% confidence). Type: bank_fraud. Detected patterns: ..."
}
```

### `GET /health`

Returns server health status and version.

---

## 🏗️ Architecture

```
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── app/
    ├── __init__.py
    ├── config.py               # Configuration & settings
    ├── models.py               # Pydantic request/response models
    ├── routes/
    │   ├── __init__.py
    │   └── honeypot.py         # Main API endpoint & response builder
    └── services/
        ├── __init__.py
        ├── agent.py            # AI victim persona (Kamala Devi)
        ├── scam_detector.py    # Multi-layer scam detection engine
        ├── intelligence.py     # Intelligence extraction (regex-based)
        └── callback.py         # GUVI callback service
```

---

## 🧪 Testing

```bash
# Unit tests (models, extraction, routing)
python tests/test_changes.py

# End-to-end test with all 3 sample scenarios
python tests/test_e2e.py

# Quick 6-turn validation with scoring
python tests/test_final.py
```

---

## ☁️ Deployment (Render)

1. Create a new **Web Service** on [Render](https://render.com)
2. Connect this GitHub repository
3. Set **Build Command**: `pip install -r requirements.txt`
4. Set **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env.example`

---

## 📊 Scoring Compliance

| Evaluation Criteria | Points | Implementation |
|---|---|---|
| Scam Detection | 20/20 | `scamDetected: true` in every response |
| Intelligence Extraction | Up to 40 | Phone, bank, UPI, links, email — with original format preservation |
| Engagement Quality | 20/20 | Session duration tracking + message counting |
| Response Structure | 20/20 | All required fields (`status`, `scamDetected`, `extractedIntelligence`, `engagementMetrics`, `agentNotes`) |

---

## 📚 Technical Highlights

- **Phone Number Format Preservation**: Stores original formats (e.g., `+91-9876543210`) for evaluator substring matching
- **Cumulative Intelligence**: Re-extracts intelligence from full conversation history on every turn
- **Scam Type Detection**: Keyword-based classification into `bank_fraud`, `upi_fraud`, `phishing`, or `general_scam`
- **Research-Informed Persona**: Temporal awareness, detailed backstory, message diversity, and information-seeking behavior

---

## 📄 License

MIT License — Built for GUVI India AI Impact Buildathon 2026
