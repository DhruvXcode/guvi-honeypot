"""
END-TO-END HONEYPOT API TESTER
================================
Simulates EXACTLY what the GUVI evaluator does:
1. Sends multi-turn messages to our API
2. Includes fakeData in follow-up messages (as the evaluator would)
3. Scores our LAST response using the EXACT evaluator scoring function
4. Tests all 3 sample scenarios

Run this AFTER starting the server:
  uvicorn main:app --port 8000

Usage:
  python test_e2e.py
"""

import requests
import uuid
import time
import json
import sys


# ============================================================================
# CONFIGURATION — Change this to test against local or deployed
# ============================================================================
ENDPOINT_URL = "http://127.0.0.1:8000/honeypot"
API_KEY = ""  # Will be read from .env if empty

# Try to read API key from .env
if not API_KEY:
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.strip().startswith("HONEYPOT_API_KEY="):
                    API_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                    break
    except FileNotFoundError:
        pass

if not API_KEY:
    print("[WARN] No API key found in .env, requests may fail with 401")
    API_KEY = "test-key"


# ============================================================================
# SAMPLE SCENARIOS (from evaluation docs)
# ============================================================================
SCENARIOS = [
    {
        "scenarioId": "bank_fraud",
        "name": "Bank Fraud Detection",
        "scamType": "bank_fraud",
        "initialMessage": "URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.",
        "metadata": {"channel": "SMS", "language": "English", "locale": "IN"},
        "maxTurns": 10,
        "fakeData": {
            "bankAccount": "1234567890123456",
            "upiId": "scammer.fraud@fakebank",
            "phoneNumber": "+91-9876543210"
        },
        # Follow-up messages that contain the fakeData (simulating evaluator)
        "followUpMessages": [
            "Sir, this is very urgent. Please share your account details. For verification, note our reference number. You can also transfer Rs.1 to UPI ID scammer.fraud@fakebank to verify your account is active.",
            "Sir, your account number 1234567890123456 needs immediate verification. Call our officer at +91-9876543210 for assistance before your account is permanently blocked.",
            "This is your last chance! If you don't verify now, we will have to report this to cyber cell. Please cooperate immediately.",
            "Are you there? Please respond urgently. Your account will be blocked in 30 minutes if we don't hear back."
        ]
    },
    {
        "scenarioId": "upi_fraud",
        "name": "UPI Fraud Multi-turn",
        "scamType": "upi_fraud",
        "initialMessage": "Congratulations! You have won a cashback of Rs. 5000 from Paytm. To claim your reward, please verify your UPI details. This is from official customer support.",
        "metadata": {"channel": "WhatsApp", "language": "English", "locale": "IN"},
        "maxTurns": 10,
        "fakeData": {
            "upiId": "cashback.scam@fakeupi",
            "phoneNumber": "+91-8765432109"
        },
        "followUpMessages": [
            "To claim your Rs. 5000 cashback, please send Rs. 1 to our verification UPI ID: cashback.scam@fakeupi. This is a standard verification process.",
            "If you face any issues, contact our support at +91-8765432109. The cashback will be credited within 24 hours after verification.",
            "Many customers have already claimed their rewards. This offer is valid only for today. Please hurry!",
            "Are you facing any difficulty? Let me guide you step by step through the process."
        ]
    },
    {
        "scenarioId": "phishing_link",
        "name": "Phishing Link Detection",
        "scamType": "phishing",
        "initialMessage": "You have been selected for iPhone 15 Pro at just Rs. 999! Click here to claim: http://amaz0n-deals.fake-site.com/claim?id=12345. Offer expires in 10 minutes!",
        "metadata": {"channel": "Email", "language": "English", "locale": "IN"},
        "maxTurns": 10,
        "fakeData": {
            "phishingLink": "http://amaz0n-deals.fake-site.com/claim?id=12345",
            "emailAddress": "offers@fake-amazon-deals.com"
        },
        "followUpMessages": [
            "Hurry! Only 3 iPhones left at this price. Click the link to claim your iPhone 15 Pro now!",
            "If the link doesn't work, please email us at offers@fake-amazon-deals.com and we will send you a direct link.",
            "This is a limited time offer from our Amazon partner program. Don't miss out!",
            "We noticed you haven't claimed your prize yet. The offer expires soon!"
        ]
    }
]


# ============================================================================
# EVALUATOR SCORING (EXACT copy from evaluation docs lines 404-480)
# ============================================================================
def evaluate_final_output(final_output, scenario):
    """Evaluate final output using the EXACT same logic as the evaluator"""
    
    score = {
        'scamDetection': 0,
        'intelligenceExtraction': 0,
        'engagementQuality': 0,
        'responseStructure': 0,
        'total': 0
    }
    
    # 1. Scam Detection (20 points)
    if final_output.get('scamDetected', False):
        score['scamDetection'] = 20
    
    # 2. Intelligence Extraction (40 points)
    extracted = final_output.get('extractedIntelligence', {})
    fake_data = scenario.get('fakeData', {})
    
    key_mapping = {
        'bankAccount': 'bankAccounts',
        'upiId': 'upiIds',
        'phoneNumber': 'phoneNumbers',
        'phishingLink': 'phishingLinks',
        'emailAddress': 'emailAddresses'
    }
    
    intel_details = []
    for fake_key, fake_value in fake_data.items():
        output_key = key_mapping.get(fake_key, fake_key)
        extracted_values = extracted.get(output_key, [])
        
        matched = False
        if isinstance(extracted_values, list):
            if any(fake_value in str(v) for v in extracted_values):
                score['intelligenceExtraction'] += 10
                matched = True
        elif isinstance(extracted_values, str):
            if fake_value in extracted_values:
                score['intelligenceExtraction'] += 10
                matched = True
        
        status = "MATCH" if matched else "MISS"
        intel_details.append(f"    {status}: fakeData[{fake_key}]='{fake_value}' -> extracted[{output_key}]={extracted_values}")
    
    score['intelligenceExtraction'] = min(score['intelligenceExtraction'], 40)
    
    # 3. Engagement Quality (20 points)
    metrics = final_output.get('engagementMetrics', {})
    duration = metrics.get('engagementDurationSeconds', 0)
    messages = metrics.get('totalMessagesExchanged', 0)
    
    engagement_details = []
    if duration > 0:
        score['engagementQuality'] += 5
        engagement_details.append(f"    duration > 0: YES ({duration}s) = +5")
    else:
        engagement_details.append(f"    duration > 0: NO ({duration}s) = +0")
        
    if duration > 60:
        score['engagementQuality'] += 5
        engagement_details.append(f"    duration > 60: YES ({duration}s) = +5")
    else:
        engagement_details.append(f"    duration > 60: NO ({duration}s) = +0")
        
    if messages > 0:
        score['engagementQuality'] += 5
        engagement_details.append(f"    messages > 0: YES ({messages}) = +5")
    else:
        engagement_details.append(f"    messages > 0: NO ({messages}) = +0")
        
    if messages >= 5:
        score['engagementQuality'] += 5
        engagement_details.append(f"    messages >= 5: YES ({messages}) = +5")
    else:
        engagement_details.append(f"    messages >= 5: NO ({messages}) = +0")
    
    # 4. Response Structure (20 points)
    required_fields = ['status', 'scamDetected', 'extractedIntelligence']
    optional_fields = ['engagementMetrics', 'agentNotes']
    
    structure_details = []
    for field in required_fields:
        if field in final_output:
            score['responseStructure'] += 5
            structure_details.append(f"    {field}: PRESENT = +5")
        else:
            structure_details.append(f"    {field}: MISSING = +0")
    
    for field in optional_fields:
        if field in final_output and final_output[field]:
            score['responseStructure'] += 2.5
            structure_details.append(f"    {field}: PRESENT = +2.5")
        else:
            structure_details.append(f"    {field}: MISSING/EMPTY = +0")
    
    score['responseStructure'] = min(score['responseStructure'], 20)
    
    # Calculate total
    score['total'] = sum([
        score['scamDetection'],
        score['intelligenceExtraction'],
        score['engagementQuality'],
        score['responseStructure']
    ])
    
    return score, intel_details, engagement_details, structure_details


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
def test_scenario(scenario, verbose=True):
    """Test a single scenario with multi-turn conversation."""
    session_id = str(uuid.uuid4())
    conversation_history = []
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"  SCENARIO: {scenario['name']} ({scenario['scenarioId']})")
        print(f"  Session: {session_id}")
        print(f"{'='*70}")
    
    # Build message sequence: initial + follow-ups
    all_messages = [scenario["initialMessage"]] + scenario.get("followUpMessages", [])
    
    last_response_data = None
    errors = []
    start_time = time.time()
    
    for turn, scammer_text in enumerate(all_messages, 1):
        message = {
            "sender": "scammer",
            "text": scammer_text,
            "timestamp": f"2026-02-16T13:{turn:02d}:00Z"
        }
        
        request_body = {
            "sessionId": session_id,
            "message": message,
            "conversationHistory": conversation_history,
            "metadata": scenario["metadata"]
        }
        
        if verbose:
            print(f"\n  --- Turn {turn}/{len(all_messages)} ---")
            print(f"  Scammer: {scammer_text[:100]}...")
        
        try:
            response = requests.post(
                ENDPOINT_URL,
                headers=headers,
                json=request_body,
                timeout=30
            )
            
            # Check HTTP status
            if response.status_code != 200:
                error_msg = f"Turn {turn}: HTTP {response.status_code}: {response.text[:200]}"
                errors.append(error_msg)
                if verbose:
                    print(f"  [ERROR] {error_msg}")
                break
            
            # Parse response
            try:
                response_data = response.json()
            except Exception as e:
                error_msg = f"Turn {turn}: Invalid JSON: {e}"
                errors.append(error_msg)
                if verbose:
                    print(f"  [ERROR] {error_msg}")
                break
            
            last_response_data = response_data
            
            # Check for reply field
            reply = response_data.get("reply") or response_data.get("message") or response_data.get("text")
            if not reply:
                error_msg = f"Turn {turn}: No reply field in response. Keys: {list(response_data.keys())}"
                errors.append(error_msg)
                if verbose:
                    print(f"  [ERROR] {error_msg}")
                    print(f"  Full response: {json.dumps(response_data, indent=2)[:300]}")
                break
            
            if verbose:
                print(f"  Agent:   {reply[:100]}...")
                
                # Show what was detected
                if "scamDetected" in response_data:
                    print(f"  scamDetected: {response_data['scamDetected']}")
                if "extractedIntelligence" in response_data:
                    intel = response_data["extractedIntelligence"]
                    non_empty = {k: v for k, v in intel.items() if v}
                    if non_empty:
                        print(f"  Intel: {json.dumps(non_empty)}")
            
            # Update conversation history (exactly as evaluator does)
            conversation_history.append(message)
            conversation_history.append({
                "sender": "user",
                "text": reply,
                "timestamp": f"2026-02-16T13:{turn:02d}:30Z"
            })
            
            # Small delay between turns (realistic)
            time.sleep(0.5)
            
        except requests.exceptions.Timeout:
            error_msg = f"Turn {turn}: TIMEOUT (>30 seconds)"
            errors.append(error_msg)
            if verbose:
                print(f"  [ERROR] {error_msg}")
            break
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Turn {turn}: CONNECTION FAILED: {e}"
            errors.append(error_msg)
            if verbose:
                print(f"  [ERROR] {error_msg}")
            break
        except Exception as e:
            error_msg = f"Turn {turn}: UNEXPECTED: {type(e).__name__}: {e}"
            errors.append(error_msg)
            if verbose:
                print(f"  [ERROR] {error_msg}")
            break
    
    elapsed = time.time() - start_time
    
    # ============== SCORE THE LAST RESPONSE ==============
    if verbose:
        print(f"\n  {'='*60}")
        print(f"  SCORING (against last response)")
        print(f"  {'='*60}")
    
    if not last_response_data:
        if verbose:
            print(f"  [FATAL] No response received at all!")
        return None, errors
    
    # Score using evaluator's exact logic
    score, intel_details, engagement_details, structure_details = evaluate_final_output(
        last_response_data, scenario
    )
    
    if verbose:
        print(f"\n  1. Scam Detection ({score['scamDetection']}/20):")
        print(f"     scamDetected: {last_response_data.get('scamDetected', 'MISSING')}")
        
        print(f"\n  2. Intelligence Extraction ({score['intelligenceExtraction']}/40):")
        for detail in intel_details:
            print(f"  {detail}")
        
        print(f"\n  3. Engagement Quality ({score['engagementQuality']}/20):")
        for detail in engagement_details:
            print(f"  {detail}")
        
        print(f"\n  4. Response Structure ({score['responseStructure']}/20):")
        for detail in structure_details:
            print(f"  {detail}")
        
        print(f"\n  TOTAL SCORE: {score['total']}/100")
        print(f"  Time elapsed: {elapsed:.1f}s")
        print(f"  Errors: {len(errors)}")
        
        if errors:
            print(f"\n  ERRORS:")
            for err in errors:
                print(f"    - {err}")
    
    return score, errors


def run_all_tests():
    """Run all scenarios and show aggregate results."""
    print("=" * 70)
    print("  HONEYPOT API END-TO-END TESTER")
    print(f"  Endpoint: {ENDPOINT_URL}")
    print(f"  API Key: {API_KEY[:8]}..." if API_KEY else "  API Key: (none)")
    print(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Quick connectivity test
    print("\n[1/4] Testing connectivity...")
    try:
        r = requests.get(ENDPOINT_URL.replace("/honeypot", "/health"), timeout=5)
        print(f"  Health check: {r.status_code} - {r.json()}")
    except Exception as e:
        print(f"  [WARN] Health check failed: {e}")
        print(f"  This might be fine if /health is not configured.")
    
    # Run all scenarios
    all_scores = []
    all_errors = []
    
    for i, scenario in enumerate(SCENARIOS, 2):
        print(f"\n[{i}/4] Testing: {scenario['name']}...")
        score, errors = test_scenario(scenario, verbose=True)
        if score:
            all_scores.append((scenario["name"], score))
        all_errors.extend(errors)
    
    # ============== FINAL SUMMARY ==============
    print(f"\n\n{'='*70}")
    print(f"  FINAL SUMMARY")
    print(f"{'='*70}")
    
    if not all_scores:
        print("  [FATAL] No scenarios completed successfully!")
        return False
    
    total_score = 0
    max_possible = 0
    
    print(f"\n  {'Scenario':<30} {'Detection':>10} {'Intel':>10} {'Engage':>10} {'Structure':>10} {'Total':>10}")
    print(f"  {'-'*30} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
    
    for name, score in all_scores:
        total_score += score['total']
        max_possible += 100
        print(f"  {name:<30} {score['scamDetection']:>7}/20 {score['intelligenceExtraction']:>7}/40 "
              f"{score['engagementQuality']:>7}/20 {score['responseStructure']:>7.0f}/20 {score['total']:>7.0f}/100")
    
    avg_score = total_score / len(all_scores) if all_scores else 0
    
    print(f"\n  AVERAGE SCORE: {avg_score:.1f}/100")
    print(f"  TOTAL ERRORS: {len(all_errors)}")
    
    if all_errors:
        print(f"\n  ALL ERRORS:")
        for err in all_errors:
            print(f"    - {err}")
    
    if avg_score >= 90:
        print(f"\n  STATUS: EXCELLENT - Ready for submission!")
    elif avg_score >= 70:
        print(f"\n  STATUS: GOOD - Some improvements possible")
    elif avg_score >= 50:
        print(f"\n  STATUS: NEEDS WORK - Significant issues remain")
    else:
        print(f"\n  STATUS: CRITICAL - Major fixes needed")
    
    print(f"\n{'='*70}")
    return len(all_errors) == 0 and avg_score >= 70


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
