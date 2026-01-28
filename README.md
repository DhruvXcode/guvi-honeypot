# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

## GUVI Hackathon 2026 - Problem Statement 2

A production-ready AI-powered honeypot system that detects scam messages, engages scammers with a convincing victim persona, and extracts actionable intelligence.

---

## 🎯 Features

- **Scam Detection**: 4-layer detection (URL whitelist → automated message → strong indicators → LLM analysis)
- **AI Agent**: Simulates "Kamala Devi", a 67-year-old retired teacher from Lucknow
- **Intelligence Extraction**: Bank accounts, UPI IDs, phone numbers, phishing links
- **Multi-turn Conversations**: Maintains context across messages
- **Mandatory Callback**: Reports final results to GUVI endpoint

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
HONEYPOT_API_KEY=your_api_key_for_authentication
GUVI_CALLBACK_URL=https://hackathon.guvi.in/api/updateHoneyPotFinalResult
```

### 3. Run the Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📡 API Endpoint

### POST `/honeypot`

**Headers:**
```
x-api-key: your_api_key
Content-Type: application/json
```

**Request Body:**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your account will be blocked!",
    "timestamp": "2026-01-28T10:00:00Z"
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
  "scamDetected": true,
  "agentResponse": "blocked?? which account beta..",
  "engagementMetrics": {
    "engagementDurationSeconds": 120,
    "totalMessagesExchanged": 5
  },
  "extractedIntelligence": {
    "bankAccounts": [],
    "upiIds": ["scammer@upi"],
    "phishingLinks": [],
    "phoneNumbers": [],
    "suspiciousKeywords": ["blocked", "verify"]
  },
  "agentNotes": "Scammer using urgency tactics"
}
```

---

## 🏗️ Project Structure

```
├── main.py                 # FastAPI application entry
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in repo)
└── app/
    ├── config.py           # Configuration settings
    ├── models.py           # Pydantic models
    ├── routes/
    │   └── honeypot.py     # Main API endpoint
    └── services/
        ├── agent.py        # AI victim persona
        ├── scam_detector.py # Scam detection logic
        ├── intelligence.py  # Intel extraction
        └── callback.py      # GUVI callback service
```

---

## ☁️ Deployment (Railway/Render)

### Railway
1. Connect GitHub repo
2. Add environment variables in Railway dashboard
3. Deploy (auto-detects `main.py`)

### Render
1. Create new Web Service
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables

---

## 📋 GUVI Compliance Checklist

| Requirement | Status |
|-------------|--------|
| API Authentication (x-api-key) | ✅ |
| Scam Detection | ✅ |
| AI Agent Engagement | ✅ |
| Multi-turn Conversations | ✅ |
| Intelligence Extraction | ✅ |
| Mandatory Callback | ✅ |
| Response Format | ✅ |

---

## 🔬 Research-Backed Design

Enhanced with insights from academic papers:
- Temporal awareness (time-of-day context)
- Detailed persona (name, age, backstory)
- Message diversity (avoids detection)
- Information-seeking policies (excuse patterns)

---

## 📄 License

MIT License - Built for GUVI Hackathon 2026
