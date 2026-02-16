"""Verify that the LIVE Render server has our latest code changes."""
import requests

url = "https://guvi-honeypot-07tp.onrender.com/honeypot"
h = {"Content-Type": "application/json", "x-api-key": "hp_sk_guvi2026_dhruv_secret_key"}

# Send a message that should trigger a 2-4 sentence Hinglish response with follow-up question
p = {
    "sessionId": "deploy-check",
    "message": {
        "sender": "scammer",
        "text": "URGENT: Your SBI account has been compromised! Share your OTP immediately or your account will be blocked!",
        "timestamp": "2026-02-16T13:30:00Z"
    },
    "conversationHistory": [],
    "metadata": {"channel": "WhatsApp", "language": "English", "locale": "IN"}
}

try:
    r = requests.post(url, json=p, headers=h, timeout=30)
    d = r.json()
    reply = d.get("reply", "NONE")
    notes = d.get("agentNotes", "NONE")
    
    print(f"STATUS: {r.status_code}")
    print(f"REPLY: {reply}")
    print(f"REPLY LENGTH: {len(reply)} chars")
    print(f"AGENT NOTES: {notes[:200]}")
    
    # Check for our improvements
    checks = {
        "Hinglish (not English)": any(w in reply.lower() for w in ["ji", "hai", "kya", "nahi", "samajh", "achha", "mujhe", "aap", "batao"]),
        "Has follow-up question": "?" in reply,
        "Length > 80 chars (2+ sentences)": len(reply) > 80,
        "Red flags in notes": "Red flags" in notes or "red flag" in notes.lower(),
    }
    
    print("\n=== DEPLOYMENT CHECKS ===")
    all_pass = True
    for check, result in checks.items():
        status = "PASS" if result else "FAIL"
        if not result:
            all_pass = False
        print(f"  {status}: {check}")
    
    print(f"\nVERDICT: {'NEW CODE DEPLOYED' if all_pass else 'OLD CODE STILL RUNNING'}")
    
except Exception as e:
    print(f"ERROR: {e}")
