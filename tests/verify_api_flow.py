
from fastapi.testclient import TestClient
from app.config import settings
from main import app
import os
import json

# Setup API Key for testing
headers = {"x-api-key": settings.HONEYPOT_API_KEY}

def test_full_flow():
    client = TestClient(app)
    
    print("🚀 Starting API Flow Verification...")
    
    payload = {
        "sessionId": "test-session-123",
        "message": {
            "sender": "scammer",
            "text": "Your bank account 123456789 is blocked. Verify immediately at http://scam-bank.com",
            "timestamp": "2026-01-26T10:00:00Z"
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English"
        }
    }
    
    print("\n1. Sending Scam Message...")
    try:
        response = client.post("/api/honeypot", json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"DEBUG: Full Response: {json.dumps(data, indent=2)}")
            print("✅ API Response: 200 OK")
            
            # Verify Scam Detection
            if data["scamDetected"]:
                print("✅ Scam Detected: TRUE")
            else:
                print("❌ Scam Detected: FALSE (Check Logic)")
                
            # Verify Intelligence
            intel = data["extractedIntelligence"]
            if "123456789" in str(intel["bankAccounts"]):
                 print("✅ Bank Account Extracted")
            else:
                 print("❌ Failed to extract Bank Account")
                 
            # Verify Agent Response
            if data["agentResponse"]:
                print(f"✅ Agent Replied: \"{data['agentResponse'][:50]}...\"")
            else:
                print("❌ No Agent Response")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Exception during request: {e}")

if __name__ == "__main__":
    test_full_flow()
