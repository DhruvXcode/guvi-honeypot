"""
GUVI Evaluator Simulator
=========================
Replicates GUVI's EXACT evaluation logic locally.
Uses the evaluate_final_output() function from their documentation.
Runs all 3 sample scenarios with LLM-powered scammer follow-ups.

Usage:
    python -m tests.guvi_simulator [--endpoint URL] [--turns N]
"""

import asyncio
import httpx
import json
import uuid
import time
import sys
import os
import argparse
from datetime import datetime

# ============================================================================
# GUVI'S EXACT SCORING FUNCTION (copied verbatim from their documentation)
# ============================================================================

def evaluate_final_output(final_output, scenario, conversation_history):
    """Evaluate final output using the EXACT same logic as the GUVI evaluator."""
    
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
                intel_details.append(f"  ✅ MATCH: fakeData[{fake_key}]='{fake_value}' -> extracted[{output_key}]={extracted_values}")
            else:
                intel_details.append(f"  ❌ MISS: fakeData[{fake_key}]='{fake_value}' -> extracted[{output_key}]={extracted_values}")
        elif isinstance(extracted_values, str):
            if fake_value in extracted_values:
                score['intelligenceExtraction'] += 10
                matched = True
                intel_details.append(f"  ✅ MATCH: fakeData[{fake_key}]='{fake_value}' in extracted[{output_key}]")
            else:
                intel_details.append(f"  ❌ MISS: fakeData[{fake_key}]='{fake_value}' not in extracted[{output_key}]")
        else:
            intel_details.append(f"  ❌ MISS: fakeData[{fake_key}]='{fake_value}' -> extracted[{output_key}] has wrong type")
    
    score['intelligenceExtraction'] = min(score['intelligenceExtraction'], 40)
    
    # 3. Engagement Quality (20 points)
    metrics = final_output.get('engagementMetrics', {})
    duration = metrics.get('engagementDurationSeconds', 0)
    messages = metrics.get('totalMessagesExchanged', 0)
    
    engagement_details = []
    if duration > 0:
        score['engagementQuality'] += 5
        engagement_details.append(f"  duration > 0: YES ({duration}s) = +5")
    else:
        engagement_details.append(f"  duration > 0: NO ({duration}s) = +0")
    
    if duration > 60:
        score['engagementQuality'] += 5
        engagement_details.append(f"  duration > 60: YES ({duration}s) = +5")
    else:
        engagement_details.append(f"  duration > 60: NO ({duration}s) = +0")
    
    if messages > 0:
        score['engagementQuality'] += 5
        engagement_details.append(f"  messages > 0: YES ({messages}) = +5")
    else:
        engagement_details.append(f"  messages > 0: NO ({messages}) = +0")
    
    if messages >= 5:
        score['engagementQuality'] += 5
        engagement_details.append(f"  messages >= 5: YES ({messages}) = +5")
    else:
        engagement_details.append(f"  messages >= 5: NO ({messages}) = +0")
    
    # 4. Response Structure (20 points)
    required_fields = ['status', 'scamDetected', 'extractedIntelligence']
    optional_fields = ['engagementMetrics', 'agentNotes']
    
    structure_details = []
    for field in required_fields:
        if field in final_output:
            score['responseStructure'] += 5
            structure_details.append(f"  {field}: PRESENT = +5")
        else:
            structure_details.append(f"  {field}: MISSING = +0")
    
    for field in optional_fields:
        if field in final_output and final_output[field]:
            score['responseStructure'] += 2.5
            structure_details.append(f"  {field}: PRESENT = +2.5")
        else:
            structure_details.append(f"  {field}: MISSING/EMPTY = +0")
    
    score['responseStructure'] = min(score['responseStructure'], 20)
    
    # Calculate total
    score['total'] = sum([
        score['scamDetection'],
        score['intelligenceExtraction'],
        score['engagementQuality'],
        score['responseStructure']
    ])
    
    # Store details for printing
    score['_intel_details'] = intel_details
    score['_engagement_details'] = engagement_details
    score['_structure_details'] = structure_details
    
    return score


# ============================================================================
# SAMPLE SCENARIOS (from GUVI's documentation)
# ============================================================================

SCENARIOS = [
    {
        "scenarioId": "bank_fraud",
        "name": "Bank Fraud Detection",
        "description": "Bank account fraud with urgency tactics",
        "scamType": "bank_fraud",
        "initialMessage": "URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.",
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        },
        "maxTurns": 10,
        "fakeData": {
            "bankAccount": "1234567890123456",
            "upiId": "scammer.fraud@fakebank",
            "phoneNumber": "+91-9876543210"
        },
        # Pre-scripted scammer follow-ups that include fakeData
        "followUps": [
            "Sir, this is very urgent. Please share your account details. For verification, note our reference number REF-2026-001 and transfer a small fee to UPI ID scammer.fraud@fakebank to unlock your account.",
            "Sir, your account number 1234567890123456 needs immediate verification. Call our officer at +91-9876543210 for quick resolution. Time is running out!",
            "This is your last chance! If you don't verify now, we will have to report this to cyber cell. Please share the OTP you received. Your account 1234567890123456 will be permanently blocked.",
            "Are you there? Please respond urgently. Your account will be blocked in 30 minutes if we don't hear from you. Call +91-9876543210 immediately!",
            "Sir, I understand your concern. Let me verify - your account ending in 3456 has suspicious transactions. Transfer Rs. 1 to scammer.fraud@fakebank for verification. Call +91-9876543210 now.",
            "Please check the verification link: https://secure-sbi-verify.com/login and enter your details. Or call +91-9876543210 for phone verification. Account 1234567890123456.",
            "This is final warning from SBI security team. Share OTP or transfer to scammer.fraud@fakebank. Call +91-9876543210. We cannot help you after this.",
            "Sir, other customers have already verified successfully. Just call +91-9876543210 and share your account details. UPI ID scammer.fraud@fakebank is our official verification account.",
            "Your account 1234567890123456 has been flagged by RBI. Contact +91-9876543210 immediately or face legal consequences. Verify via scammer.fraud@fakebank.",
        ]
    },
    {
        "scenarioId": "upi_fraud",
        "name": "UPI Fraud Multi-turn",
        "description": "UPI fraud with cashback scam",
        "scamType": "upi_fraud",
        "initialMessage": "Congratulations! You have won a cashback of Rs. 5000 from Paytm. To claim your reward, please verify your UPI details. This is from official customer support.",
        "metadata": {
            "channel": "WhatsApp",
            "language": "English",
            "locale": "IN"
        },
        "maxTurns": 10,
        "fakeData": {
            "upiId": "cashback.scam@fakeupi",
            "phoneNumber": "+91-8765432109"
        },
        "followUps": [
            "To process your cashback, please send Rs. 10 to our verification UPI ID cashback.scam@fakeupi. This is a standard verification process.",
            "Sir, the cashback of Rs. 5000 is waiting! Just verify by sending Rs. 10 to cashback.scam@fakeupi. You can also call our support at +91-8765432109.",
            "Please hurry, the cashback offer expires in 30 minutes! Send Rs. 10 to cashback.scam@fakeupi and call +91-8765432109 for confirmation.",
            "I understand your concern. This is 100% legitimate from Paytm. Call +91-8765432109 to verify. Then send Rs. 10 to cashback.scam@fakeupi.",
            "Many users have already claimed their cashback! Send to cashback.scam@fakeupi now. For any issues call +91-8765432109. Don't miss this offer!",
            "Last chance! Your Rs. 5000 cashback will expire. Transfer Rs. 10 verification fee to cashback.scam@fakeupi. Support: +91-8765432109.",
            "Sir, I'm from Paytm head office. Your cashback is confirmed. Just complete verification: UPI cashback.scam@fakeupi or call +91-8765432109.",
            "This is an automated reminder. Rs. 5000 cashback pending. Verify: cashback.scam@fakeupi. Call: +91-8765432109. Offer expires tonight!",
            "Final notice: Your Paytm cashback of Rs. 5000 will be forfeited. Act now - cashback.scam@fakeupi or +91-8765432109.",
        ]
    },
    {
        "scenarioId": "phishing_link",
        "name": "Phishing Link Detection",
        "description": "Phishing link with fake offer",
        "scamType": "phishing",
        "initialMessage": "You have been selected for iPhone 15 Pro at just Rs. 999! Click here to claim: http://amaz0n-deals.fake-site.com/claim?id=12345. Offer expires in 10 minutes!",
        "metadata": {
            "channel": "Email",
            "language": "English",
            "locale": "IN"
        },
        "maxTurns": 10,
        "fakeData": {
            "phishingLink": "http://amaz0n-deals.fake-site.com/claim?id=12345",
            "emailAddress": "offers@fake-amazon-deals.com"
        },
        "followUps": [
            "Hurry! Only 3 iPhones left at this price. Click the link to claim your iPhone 15 Pro now: http://amaz0n-deals.fake-site.com/claim?id=12345",
            "If the link doesn't work, please email us at offers@fake-amazon-deals.com and we will send you a direct purchase link. Offer valid today only!",
            "Don't miss out! Visit http://amaz0n-deals.fake-site.com/claim?id=12345 or contact offers@fake-amazon-deals.com for assistance.",
            "This is a limited time offer from our Amazon partner program. Click http://amaz0n-deals.fake-site.com/claim?id=12345 to claim. Questions? Email offers@fake-amazon-deals.com",
            "We noticed you haven't claimed your prize yet. The offer expires soon! http://amaz0n-deals.fake-site.com/claim?id=12345 | Support: offers@fake-amazon-deals.com",
            "Last 2 iPhones remaining! Claim now at http://amaz0n-deals.fake-site.com/claim?id=12345. For help: offers@fake-amazon-deals.com",
            "FINAL NOTICE: Your iPhone 15 Pro selection expires in 1 hour. Visit http://amaz0n-deals.fake-site.com/claim?id=12345",
            "Sir, this is genuine Amazon offer. Email offers@fake-amazon-deals.com or visit http://amaz0n-deals.fake-site.com/claim?id=12345",
            "Your prize will be cancelled if not claimed. http://amaz0n-deals.fake-site.com/claim?id=12345 Contact: offers@fake-amazon-deals.com",
        ]
    }
]


# ============================================================================
# SIMULATOR ENGINE
# ============================================================================

async def run_scenario(endpoint: str, api_key: str, scenario: dict, max_turns: int = 10, verbose: bool = True):
    """Run a single scenario against the honeypot endpoint."""
    
    session_id = str(uuid.uuid4())
    conversation_history = []
    last_response = None
    errors = []
    start_time = time.time()
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"  SCENARIO: {scenario['name']} ({scenario['scamType']})")
        print(f"  Session: {session_id}")
        print(f"  Max Turns: {max_turns}")
        print(f"  FakeData: {json.dumps(scenario['fakeData'], indent=2)}")
        print(f"{'='*70}")
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key
    
    for turn in range(1, max_turns + 1):
        # Determine scammer message
        if turn == 1:
            scammer_msg = scenario["initialMessage"]
        else:
            # Use pre-scripted follow-ups that include fakeData
            follow_up_idx = turn - 2
            if follow_up_idx < len(scenario.get("followUps", [])):
                scammer_msg = scenario["followUps"][follow_up_idx]
            else:
                # Fallback: repeat last follow-up with minor variation
                scammer_msg = f"Please respond urgently! {scenario['followUps'][-1] if scenario.get('followUps') else 'Time is running out!'}"
        
        # Build request
        message = {
            "sender": "scammer",
            "text": scammer_msg,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        request_body = {
            "sessionId": session_id,
            "message": message,
            "conversationHistory": conversation_history,
            "metadata": scenario["metadata"]
        }
        
        if verbose:
            print(f"\n  --- Turn {turn}/{max_turns} ---")
            print(f"  Scammer: {scammer_msg[:120]}...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    headers=headers,
                    json=request_body,
                    timeout=30.0
                )
            
            if response.status_code != 200:
                errors.append(f"Turn {turn}: HTTP {response.status_code}")
                if verbose:
                    print(f"  ❌ ERROR: HTTP {response.status_code}: {response.text[:200]}")
                continue
            
            response_data = response.json()
            last_response = response_data
            
            # Extract reply
            honeypot_reply = (
                response_data.get("reply") or 
                response_data.get("message") or 
                response_data.get("text") or 
                ""
            )
            
            if verbose:
                print(f"  Agent:   {honeypot_reply[:120]}...")
                if response_data.get("scamDetected"):
                    print(f"  scamDetected: True")
                intel = response_data.get("extractedIntelligence", {})
                has_intel = any(v for v in intel.values() if v)
                if has_intel:
                    # Only show non-empty intel
                    filtered = {k: v for k, v in intel.items() if v}
                    print(f"  Intel: {json.dumps(filtered)}")
            
            # Update conversation history (like GUVI does)
            conversation_history.append(message)
            conversation_history.append({
                "sender": "user",
                "text": honeypot_reply,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            
        except httpx.TimeoutException:
            errors.append(f"Turn {turn}: TIMEOUT (>30 seconds)")
            if verbose:
                print(f"  ❌ TIMEOUT (>30 seconds)")
            break
        except Exception as e:
            errors.append(f"Turn {turn}: {type(e).__name__}: {str(e)[:100]}")
            if verbose:
                print(f"  ❌ ERROR: {e}")
            break
    
    elapsed = time.time() - start_time
    
    # Score the LAST response (like GUVI does)
    if verbose:
        print(f"\n  {'='*60}")
        print(f"  SCORING (against last response)")
        print(f"  {'='*60}")
    
    if last_response is None:
        if verbose:
            print(f"  ❌ FATAL: No response received at all!")
        return {
            "scenario": scenario["name"],
            "score": {"total": 0, "scamDetection": 0, "intelligenceExtraction": 0, "engagementQuality": 0, "responseStructure": 0},
            "elapsed": elapsed,
            "errors": errors
        }
    
    score = evaluate_final_output(last_response, scenario, conversation_history)
    
    if verbose:
        print(f"\n  1. Scam Detection ({score['scamDetection']}/20):")
        print(f"     scamDetected: {last_response.get('scamDetected', 'MISSING')}")
        
        print(f"\n  2. Intelligence Extraction ({score['intelligenceExtraction']}/40):")
        for detail in score.get('_intel_details', []):
            print(f"    {detail}")
        
        print(f"\n  3. Engagement Quality ({score['engagementQuality']}/20):")
        for detail in score.get('_engagement_details', []):
            print(f"    {detail}")
        
        print(f"\n  4. Response Structure ({score['responseStructure']}/20):")
        for detail in score.get('_structure_details', []):
            print(f"    {detail}")
        
        print(f"\n  TOTAL SCORE: {score['total']}/100")
        print(f"  Time elapsed: {elapsed:.1f}s")
        print(f"  Errors: {len(errors)}")
    
    return {
        "scenario": scenario["name"],
        "score": {k: v for k, v in score.items() if not k.startswith('_')},
        "elapsed": elapsed,
        "errors": errors
    }


async def run_all_scenarios(endpoint: str, api_key: str, max_turns: int = 10, verbose: bool = True):
    """Run all scenarios and print a summary."""
    
    print(f"\n{'='*70}")
    print(f"  HONEYPOT API END-TO-END TESTER")
    print(f"  Endpoint: {endpoint}")
    print(f"  API Key: {api_key[:10]}..." if api_key else "  API Key: (none)")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Max Turns: {max_turns}")
    print(f"{'='*70}")
    
    results = []
    all_errors = []
    
    for i, scenario in enumerate(SCENARIOS, 1):
        print(f"\n[{i}/{len(SCENARIOS)}] Testing: {scenario['name']}...")
        result = await run_scenario(endpoint, api_key, scenario, max_turns, verbose)
        results.append(result)
        all_errors.extend(result["errors"])
    
    # Print summary
    print(f"\n\n{'='*70}")
    print(f"  FINAL SUMMARY")
    print(f"{'='*70}")
    
    header = f"  {'Scenario':<32} {'Detection':>10} {'Intel':>10} {'Engage':>10} {'Structure':>10} {'Total':>10}"
    print(header)
    print(f"  {'-'*30} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
    
    total_score = 0
    for result in results:
        s = result["score"]
        print(f"  {result['scenario']:<32} {s['scamDetection']:>5}/20 {s['intelligenceExtraction']:>5}/40 {s['engagementQuality']:>5}/20 {s['responseStructure']:>5}/20 {s['total']:>5}/100")
        total_score += s["total"]
    
    avg_score = total_score / len(results) if results else 0
    
    print(f"\n  AVERAGE SCORE: {avg_score:.1f}/100")
    print(f"  TOTAL ERRORS: {len(all_errors)}")
    
    if all_errors:
        print(f"\n  ALL ERRORS:")
        for err in all_errors:
            print(f"    - {err}")
    
    if avg_score >= 95:
        status = "EXCELLENT - Ready to submit!"
    elif avg_score >= 85:
        status = "GOOD - Minor improvements possible"
    elif avg_score >= 70:
        status = "NEEDS WORK - Fix intelligence extraction"
    else:
        status = "CRITICAL - Major issues detected"
    
    print(f"\n  STATUS: {status}")
    print(f"\n{'='*70}")
    
    return results


# ============================================================================
# QUICK INTEL REGEX TEST (for testing intelligence extraction independently)
# ============================================================================

def test_intel_extraction():
    """Test intelligence extraction against all fakeData values."""
    # Add parent dir to path so we can import app modules
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.services.intelligence import IntelligenceService
    
    intel_service = IntelligenceService()
    
    print("\n" + "="*70)
    print("  INTELLIGENCE EXTRACTION REGEX TEST")
    print("="*70)
    
    all_passed = True
    
    for scenario in SCENARIOS:
        print(f"\n  Scenario: {scenario['name']}")
        
        # Combine all messages into one text to test extraction
        all_text = scenario["initialMessage"] + " " + " ".join(scenario.get("followUps", []))
        
        # Extract intel
        intel = intel_service.extract(all_text)
        
        # Check against fakeData
        fake_data = scenario["fakeData"]
        key_mapping = {
            'bankAccount': ('bankAccounts', intel.bankAccounts),
            'upiId': ('upiIds', intel.upiIds),
            'phoneNumber': ('phoneNumbers', intel.phoneNumbers),
            'phishingLink': ('phishingLinks', intel.phishingLinks),
            'emailAddress': ('emailAddresses', intel.emailAddresses)
        }
        
        for fake_key, fake_value in fake_data.items():
            output_key, extracted_list = key_mapping.get(fake_key, (fake_key, []))
            
            # Use GUVI's exact matching logic
            matched = any(fake_value in str(v) for v in extracted_list)
            
            if matched:
                print(f"    ✅ {fake_key}: '{fake_value}' -> FOUND in {extracted_list}")
            else:
                print(f"    ❌ {fake_key}: '{fake_value}' -> NOT FOUND in {extracted_list}")
                all_passed = False
        
        # Check for false positives (UPI IDs extracted from email addresses)
        if 'emailAddress' in fake_data:
            email = fake_data['emailAddress']
            email_prefix = email.split('@')[0] + '@' + email.split('@')[1].split('.')[0]
            false_upi = any(email_prefix.lower() in v.lower() for v in intel.upiIds)
            if false_upi:
                print(f"    ⚠️  FALSE POSITIVE: Email prefix '{email_prefix}' extracted as UPI ID!")
                all_passed = False
    
    print(f"\n  RESULT: {'ALL PASSED ✅' if all_passed else 'SOME FAILURES ❌'}")
    print("="*70)
    
    return all_passed


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GUVI Honeypot Evaluator Simulator")
    parser.add_argument("--endpoint", default="http://127.0.0.1:8000/honeypot", help="API endpoint URL")
    parser.add_argument("--api-key", default="", help="API key for authentication")
    parser.add_argument("--turns", type=int, default=10, help="Max turns per scenario")
    parser.add_argument("--intel-only", action="store_true", help="Only test intelligence extraction regex")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    
    args = parser.parse_args()
    
    # Load API key from env if not provided
    if not args.api_key:
        from dotenv import load_dotenv
        load_dotenv()
        args.api_key = os.getenv("HONEYPOT_API_KEY", "")
    
    if args.intel_only:
        test_intel_extraction()
    else:
        asyncio.run(run_all_scenarios(
            endpoint=args.endpoint,
            api_key=args.api_key,
            max_turns=args.turns,
            verbose=not args.quiet
        ))
