"""Final validation test - 5 turns of bank fraud + check callback."""
import requests, json, uuid, os, time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("HONEYPOT_API_KEY", "test-key")
ENDPOINT = "http://127.0.0.1:8000/honeypot"
session_id = str(uuid.uuid4())
headers = {"Content-Type": "application/json", "x-api-key": API_KEY}

messages = [
    "URGENT: Your SBI account has been compromised. Contact us immediately.",
    "Sir, transfer Rs.1 to UPI ID scammer.fraud@fakebank to verify your account.",
    "Your account number 1234567890123456 needs verification. Call +91-9876543210.",
    "This is your last warning. Account will be blocked permanently.",
    "Sir, why are you not responding? We need your immediate cooperation.",
    "Please send your details to scam-support@fakebank-india.com for resolution."
]

out = []
history = []
last_d = None

for turn, msg_text in enumerate(messages, 1):
    msg = {"sender": "scammer", "text": msg_text, "timestamp": f"2026-02-16T13:{turn:02d}:00Z"}
    body = {"sessionId": session_id, "message": msg, "conversationHistory": history, "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}}
    
    r = requests.post(ENDPOINT, headers=headers, json=body, timeout=30)
    d = r.json()
    last_d = d
    reply = d.get("reply", "")
    history.append(msg)
    history.append({"sender": "user", "text": reply, "timestamp": f"2026-02-16T13:{turn:02d}:30Z"})
    
    out.append(f"Turn {turn}: status={r.status_code} scamDetected={d.get('scamDetected')}")
    intel = d.get("extractedIntelligence", {})
    non_empty = {k:v for k,v in intel.items() if v}
    if non_empty:
        out.append(f"  Intel: {json.dumps(non_empty)}")
    out.append(f"  Metrics: {d.get('engagementMetrics',{})}")

# Wait for callback background task
out.append("\nWaiting 3s for callback background task...")
time.sleep(3)

# Score final response
out.append("\n=== FINAL SCORING ===")
d = last_d
fake_data = {"bankAccount": "1234567890123456", "upiId": "scammer.fraud@fakebank", "phoneNumber": "+91-9876543210"}
key_mapping = {"bankAccount": "bankAccounts", "upiId": "upiIds", "phoneNumber": "phoneNumbers", "emailAddress": "emailAddresses"}

intel = d.get("extractedIntelligence", {})
intel_score = 0
for fk, fv in fake_data.items():
    ok = key_mapping.get(fk, fk)
    ev = intel.get(ok, [])
    matched = any(fv in str(v) for v in ev) if isinstance(ev, list) else False
    if matched: intel_score += 10
    out.append(f"  {'MATCH' if matched else 'MISS'}: {fk}='{fv}' -> {ok}={ev}")

scam_pts = 20 if d.get("scamDetected") else 0
struct = 0
for f in ["status", "scamDetected", "extractedIntelligence"]:
    if f in d: struct += 5
for f in ["engagementMetrics", "agentNotes"]:
    if f in d and d[f]: struct += 2.5
struct = min(struct, 20)

m = d.get("engagementMetrics", {})
eng = 0
dur = m.get("engagementDurationSeconds", 0)
msgs = m.get("totalMessagesExchanged", 0)
if dur > 0: eng += 5
if dur > 60: eng += 5
if msgs > 0: eng += 5
if msgs >= 5: eng += 5

total = scam_pts + min(intel_score, 40) + eng + struct
out.append(f"\nScam Detection:   {scam_pts}/20")
out.append(f"Intel Extraction: {min(intel_score,40)}/40   (max possible with 3 fakeData items)")
out.append(f"Engagement:       {eng}/20   (dur={dur}s, msgs={msgs})")
out.append(f"Resp Structure:   {struct}/20")
out.append(f"TOTAL:            {total}/100")

# Write to file
with open("final_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

# Also dump last response JSON
with open("final_response.json", "w", encoding="utf-8") as f:
    json.dump(last_d, f, indent=2)

print("\n".join(out[-10:]))
