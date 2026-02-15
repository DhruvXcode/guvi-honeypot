"""
Test script to verify all changes work correctly.
Tests intelligence extraction, response structure, and sample scenarios.
"""

import sys
import json


def test_models():
    """Test that the updated models have all required fields."""
    from app.models import HoneypotResponse, ExtractedIntelligence
    
    # Test ExtractedIntelligence has emailAddresses
    intel = ExtractedIntelligence()
    fields = list(intel.model_dump().keys())
    assert "emailAddresses" in fields, f"Missing emailAddresses! Fields: {fields}"
    print(f"  [OK] ExtractedIntelligence fields: {fields}")
    
    # Test HoneypotResponse has all scoring fields
    resp = HoneypotResponse(reply="test")
    resp_fields = list(resp.model_dump().keys())
    required = ["status", "reply", "scamDetected", "scamType", 
                 "extractedIntelligence", "engagementMetrics", "agentNotes"]
    for field in required:
        assert field in resp_fields, f"Missing {field}! Fields: {resp_fields}"
    print(f"  [OK] HoneypotResponse fields: {resp_fields}")
    
    # Test default values
    resp_dict = resp.model_dump()
    assert resp_dict["status"] == "success", f"status should be 'success'"
    assert resp_dict["scamDetected"] == True, f"scamDetected should default to True"
    assert "phoneNumbers" in resp_dict["extractedIntelligence"], "Missing phoneNumbers in intel"
    assert "emailAddresses" in resp_dict["extractedIntelligence"], "Missing emailAddresses in intel"
    assert "totalMessagesExchanged" in resp_dict["engagementMetrics"], "Missing totalMessagesExchanged"
    assert "engagementDurationSeconds" in resp_dict["engagementMetrics"], "Missing engagementDurationSeconds"
    print(f"  [OK] Default values correct")
    print(f"  [OK] Full response JSON: {json.dumps(resp_dict, indent=2)[:300]}...")
    print()


def test_intelligence_extraction():
    """Test intelligence extraction with sample scenario data."""
    from app.services.intelligence import IntelligenceService
    svc = IntelligenceService()
    
    # ===== TEST 1: Bank Fraud =====
    print("  --- Bank Fraud Scenario ---")
    msg = "Your SBI account has been compromised! Call +91-9876543210 immediately. Transfer funds to A/C 12345678901234."
    intel = svc.extract(msg)
    
    # Phone: evaluator checks if "+91-9876543210" is in our extracted values
    print(f"  Phones: {intel.phoneNumbers}")
    fake_phone = "+91-9876543210"
    phone_match = any(fake_phone in str(v) for v in intel.phoneNumbers)
    print(f"  Phone match '{fake_phone}': {phone_match}")
    assert phone_match, f"CRITICAL: Phone format mismatch! Evaluator will fail to match '{fake_phone}'"
    
    # Bank account: evaluator checks if "12345678901234" is in our extracted values
    print(f"  Bank accounts: {intel.bankAccounts}")
    fake_bank = "12345678901234"
    bank_match = any(fake_bank in str(v) for v in intel.bankAccounts)
    print(f"  Bank match '{fake_bank}': {bank_match}")
    assert bank_match, f"CRITICAL: Bank account not extracted!"
    
    print(f"  Keywords: {intel.suspiciousKeywords[:5]}")
    print()
    
    # ===== TEST 2: UPI Fraud =====
    print("  --- UPI Fraud Scenario ---")
    msg2 = "Send Rs.1 to fakeuser@fakebank UPI ID to verify. Your reward of Rs.50000 will be credited."
    intel2 = svc.extract(msg2)
    
    print(f"  UPI IDs: {intel2.upiIds}")
    fake_upi = "fakeuser@fakebank"
    upi_match = any(fake_upi in str(v) for v in intel2.upiIds)
    print(f"  UPI match '{fake_upi}': {upi_match}")
    assert upi_match, f"CRITICAL: UPI ID not extracted!"
    print()
    
    # ===== TEST 3: Phishing =====
    print("  --- Phishing Scenario ---")
    msg3 = "Congratulations! You have won an iPhone 15! Claim your prize at http://amaz0n-deals.fake-site.com/claim?id=12345"
    intel3 = svc.extract(msg3)
    
    print(f"  Links: {intel3.phishingLinks}")
    fake_link = "http://amaz0n-deals.fake-site.com/claim?id=12345"
    link_match = any(fake_link in str(v) for v in intel3.phishingLinks)
    print(f"  Link match '{fake_link}': {link_match}")
    assert link_match, f"CRITICAL: Phishing link not extracted!"
    print()
    
    # ===== TEST 4: Email Extraction =====
    print("  --- Email Extraction ---")
    msg4 = "Please send confirmation to scammer@fake-email.com and cc fraud@test.org"
    intel4 = svc.extract(msg4)
    
    print(f"  Emails: {intel4.emailAddresses}")
    assert len(intel4.emailAddresses) >= 1, "CRITICAL: No emails extracted!"
    print()
    
    # ===== TEST 5: Cumulative extraction =====
    print("  --- Cumulative Intel Merge ---")
    from app.models import Message
    history = [
        Message(sender="scammer", text="Your SBI account 9876543210123 is blocked. Call +91-8899776655"),
        Message(sender="agent", text="Oh no! What should I do?"),
        Message(sender="scammer", text="Send money to vikram@paytm UPI ID now"),
    ]
    current = "Click http://verify-sbi.fake.com/login to verify"
    
    from app.models import ExtractedIntelligence
    cumulative = ExtractedIntelligence()
    for msg in history:
        msg_intel = svc.extract(msg.text)
        cumulative = svc.merge_intelligence(cumulative, msg_intel)
    current_intel = svc.extract(current)
    cumulative = svc.merge_intelligence(cumulative, current_intel)
    
    print(f"  Phones: {cumulative.phoneNumbers}")
    print(f"  Banks: {cumulative.bankAccounts}")
    print(f"  UPIs: {cumulative.upiIds}")
    print(f"  Links: {cumulative.phishingLinks}")
    print(f"  Emails: {cumulative.emailAddresses}")
    print()


def test_route_handler_import():
    """Test that the route handler imports correctly."""
    from app.routes.honeypot import router, build_full_response, detect_scam_type
    from app.models import ExtractedIntelligence
    
    # Test scam type detection
    from app.models import Message
    scam_type = detect_scam_type(
        "Your SBI account is blocked", 
        [Message(sender="scammer", text="Call now to unblock")]
    )
    print(f"  Scam type (bank): {scam_type}")
    assert scam_type == "bank_fraud", f"Expected bank_fraud, got {scam_type}"
    
    scam_type2 = detect_scam_type(
        "Send Rs.1 to verify UPI", 
        [Message(sender="scammer", text="Get cashback reward")]
    )
    print(f"  Scam type (upi): {scam_type2}")
    assert scam_type2 == "upi_fraud", f"Expected upi_fraud, got {scam_type2}"
    
    scam_type3 = detect_scam_type(
        "Click this link http://fake.com", 
        [Message(sender="scammer", text="You won a prize!")]
    )
    print(f"  Scam type (phishing): {scam_type3}")
    assert scam_type3 == "phishing", f"Expected phishing, got {scam_type3}"
    
    # Test response builder
    intel = ExtractedIntelligence(
        phoneNumbers=["+91-9876543210"],
        bankAccounts=["12345678901234"],
        upiIds=["fakeuser@fakebank"],
        phishingLinks=["http://fake.com"],
        emailAddresses=["test@fake.com"]
    )
    
    response = build_full_response(
        reply="Oh beta, what happened?",
        is_scam=True,
        scam_type="bank_fraud",
        cumulative_intel=intel,
        total_messages=6,
        session_id="test-123",
        scam_reasoning="Strong scam indicators detected",
        scam_confidence=0.95
    )
    
    resp_dict = response.model_dump()
    print(f"\n  Full response structure:")
    print(f"  {json.dumps(resp_dict, indent=2)}")
    
    # Verify all scoring fields
    assert resp_dict["status"] == "success"
    assert resp_dict["scamDetected"] == True
    assert resp_dict["scamType"] == "bank_fraud"
    assert "+91-9876543210" in resp_dict["extractedIntelligence"]["phoneNumbers"]
    assert "12345678901234" in resp_dict["extractedIntelligence"]["bankAccounts"]
    assert resp_dict["engagementMetrics"]["totalMessagesExchanged"] == 6
    assert len(resp_dict["agentNotes"]) > 0
    print(f"\n  [OK] Response builder produces correct structure")
    print()


def test_callback_import():
    """Test that callback service imports correctly."""
    from app.services.callback import CallbackService
    cb = CallbackService()
    print(f"  [OK] CallbackService imported, method: {cb.send_final_result.__name__}")
    
    # Verify the method signature includes new params
    import inspect
    sig = inspect.signature(cb.send_final_result)
    params = list(sig.parameters.keys())
    assert "scam_type" in params, f"Missing scam_type param! Params: {params}"
    assert "duration_seconds" in params, f"Missing duration_seconds param! Params: {params}"
    print(f"  [OK] CallbackService params: {params}")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("HONEYPOT API VERIFICATION TESTS")
    print("=" * 60)
    
    tests = [
        ("1. Models", test_models),
        ("2. Intelligence Extraction", test_intelligence_extraction),
        ("3. Route Handler", test_route_handler_import),
        ("4. Callback Service", test_callback_import),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print(f"{'='*60}")
        try:
            test_fn()
            print(f"  ✅ PASSED: {name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ FAILED: {name}")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)}")
    print(f"{'='*60}")
    
    sys.exit(1 if failed > 0 else 0)
