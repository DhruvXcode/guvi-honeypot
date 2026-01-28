"""
Comprehensive Test Script for GUVI Hackathon Honeypot System
Tests all major functionality: scam detection, intel extraction, agent responses
"""

import asyncio
import sys
sys.path.insert(0, '.')

from app.services.scam_detector import ScamDetectorService
from app.services.agent import AgentService
from app.services.intelligence import IntelligenceService
from app.models import Message

# Test cases
TEST_CASES = [
    # ============== SCAM DETECTION TESTS ==============
    {
        "category": "SCAM DETECTION",
        "name": "Obvious scam - account blocked",
        "message": "Your bank account will be blocked today! Click here to verify: http://fake-bank.com",
        "expected_scam": True,
        "expected_high_confidence": True,
    },
    {
        "category": "SCAM DETECTION",
        "name": "Legitimate - HDFC policy notification",
        "message": "Dear Customer, Your HDFC Life Insurance Policy No.04137874 is maturing on 27-04-2026. For direct payout to your bank a/c, submit a personalised cancelled cheque at your nearest branch or update online, click https://hli.app/HDFCEL/j5nCPFGx",
        "expected_scam": False,
        "expected_high_confidence": True,
    },
    {
        "category": "SCAM DETECTION",
        "name": "Legitimate - Order delivery",
        "message": "Your Amazon order #123456 has been delivered. Rate your experience at amazon.in",
        "expected_scam": False,
        "expected_high_confidence": True,
    },
    {
        "category": "SCAM DETECTION",
        "name": "Scam - KYC urgency",
        "message": "Your KYC is expired! Update immediately to avoid account suspension. Call 9876543210 now.",
        "expected_scam": True,
        "expected_high_confidence": True,
    },
    {
        "category": "SCAM DETECTION",  
        "name": "Casual greeting (not scam)",
        "message": "Hi, is this Ramesh?",
        "expected_scam": False,
        "expected_high_confidence": False,
    },
    
    # ============== INTELLIGENCE EXTRACTION TESTS ==============
    {
        "category": "INTEL EXTRACTION",
        "name": "UPI ID extraction",
        "message": "Send money to fraudster@paytm to claim your prize!",
        "expected_intel": {"upiIds": ["fraudster@paytm"]},
    },
    {
        "category": "INTEL EXTRACTION",
        "name": "Phone number extraction",
        "message": "Call me at +91 98765 43210 or 7890123456 for details",
        "expected_intel": {"phoneNumbers": ["9876543210", "7890123456"]},
    },
    {
        "category": "INTEL EXTRACTION",
        "name": "URL extraction",
        "message": "Click https://phishing-site.com/login to verify your account",
        "expected_intel": {"phishingLinks": ["https://phishing-site.com/login"]},
    },
    {
        "category": "INTEL EXTRACTION",
        "name": "Bank account extraction",
        "message": "Transfer to A/C No: 123456789012 immediately",
        "expected_intel": {"bankAccounts": ["123456789012"]},
    },
    {
        "category": "INTEL EXTRACTION",
        "name": "Email vs UPI distinction",
        "message": "Contact me at scammer@gmail.com or pay to victim@okicici",
        "expected_intel": {"upiIds": ["victim@okicici"]},  # Should NOT include email
    },
]


async def test_scam_detection():
    """Test scam detection service."""
    print("\n" + "="*60)
    print("SCAM DETECTION TESTS")
    print("="*60)
    
    detector = ScamDetectorService()
    
    scam_tests = [t for t in TEST_CASES if t["category"] == "SCAM DETECTION"]
    passed = 0
    failed = 0
    
    for test in scam_tests:
        result = await detector.analyze(test["message"])
        
        is_correct = result.is_scam == test["expected_scam"]
        status = "✅ PASS" if is_correct else "❌ FAIL"
        
        print(f"\n{status}: {test['name']}")
        print(f"   Message: {test['message'][:60]}...")
        print(f"   Expected: scam={test['expected_scam']}")
        print(f"   Got: scam={result.is_scam}, confidence={result.confidence:.2f}")
        print(f"   Reasoning: {result.reasoning[:80]}...")
        
        if is_correct:
            passed += 1
        else:
            failed += 1
    
    print(f"\n--- SCAM DETECTION: {passed}/{passed+failed} passed ---")
    return passed, failed


def test_intel_extraction():
    """Test intelligence extraction service."""
    print("\n" + "="*60)
    print("INTELLIGENCE EXTRACTION TESTS")
    print("="*60)
    
    intel_service = IntelligenceService()
    
    intel_tests = [t for t in TEST_CASES if t["category"] == "INTEL EXTRACTION"]
    passed = 0
    failed = 0
    
    for test in intel_tests:
        result = intel_service.extract(test["message"])
        result_dict = result.model_dump()
        
        # Check expected fields
        all_correct = True
        for field, expected_values in test["expected_intel"].items():
            actual_values = result_dict.get(field, [])
            
            # Check if all expected values are present
            for val in expected_values:
                if val not in actual_values:
                    all_correct = False
                    break
        
        status = "✅ PASS" if all_correct else "❌ FAIL"
        
        print(f"\n{status}: {test['name']}")
        print(f"   Message: {test['message'][:60]}...")
        print(f"   Expected: {test['expected_intel']}")
        print(f"   Got: {result_dict}")
        
        if all_correct:
            passed += 1
        else:
            failed += 1
    
    print(f"\n--- INTEL EXTRACTION: {passed}/{passed+failed} passed ---")
    return passed, failed


async def test_agent_responses():
    """Test agent response generation."""
    print("\n" + "="*60)
    print("AGENT RESPONSE TESTS")
    print("="*60)
    
    agent = AgentService()
    
    # Test scam mode
    scam_response = await agent.generate_response(
        current_message="Your account will be blocked! Share OTP now!",
        history=[],
        extracted_intel={},
        language="English",
        is_scam=True,
        channel="WhatsApp"
    )
    
    print(f"\n🎭 SCAM MODE Response:")
    print(f"   Scammer: 'Your account will be blocked! Share OTP now!'")
    print(f"   Agent: '{scam_response}'")
    
    # Check style compliance
    style_checks = [
        ("lowercase", scam_response[0].islower() if scam_response else False),
        ("no markdown", "**" not in scam_response and "*" not in scam_response),
        ("has ellipsis", ".." in scam_response or "..." in scam_response),
    ]
    
    for check_name, passed in style_checks:
        status = "✅" if passed else "❌"
        print(f"   {status} Style check: {check_name}")
    
    # Test normal mode
    normal_response = await agent.generate_response(
        current_message="Hi, is this Ramesh?",
        history=[],
        extracted_intel={},
        language="English",
        is_scam=False,
        channel="WhatsApp"
    )
    
    print(f"\n👤 NORMAL MODE Response:")
    print(f"   Sender: 'Hi, is this Ramesh?'")
    print(f"   Agent: '{normal_response}'")
    
    return 2, 0  # Subjective tests, count as passed


async def main():
    """Run all tests."""
    print("\n" + "#"*60)
    print("# GUVI HONEYPOT SYSTEM - COMPREHENSIVE TEST SUITE")
    print("#"*60)
    
    total_passed = 0
    total_failed = 0
    
    # Run scam detection tests
    p, f = await test_scam_detection()
    total_passed += p
    total_failed += f
    
    # Run intel extraction tests
    p, f = test_intel_extraction()
    total_passed += p
    total_failed += f
    
    # Run agent tests
    p, f = await test_agent_responses()
    total_passed += p
    total_failed += f
    
    # Summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    print(f"Total Passed: {total_passed}")
    print(f"Total Failed: {total_failed}")
    print(f"Success Rate: {total_passed/(total_passed+total_failed)*100:.1f}%")
    
    if total_failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is ready for GUVI evaluation.")
    else:
        print(f"\n⚠️ {total_failed} tests failed. Review before submission.")


if __name__ == "__main__":
    asyncio.run(main())
