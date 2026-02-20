# Peer Review Test Log

## Summary
- Total: 20
- Passed: 17
- Failed: 3
- Pass Rate: 85.0%

## Suite Breakdown
- intelligence: 8/8 passed, 0 failed
- scam_detector: 3/5 passed, 2 failed
- route: 6/6 passed, 0 failed
- live_endpoint: 0/1 passed, 1 failed

## Detailed Results
- [PASS] intelligence::phone_hyphen_preserved
  Details: {"input": "Call me at +91-9876543210 now.", "output": {"bankAccounts": [], "upiIds": [], "phishingLinks": [], "phoneNumbers": ["+91-9876543210"], "emailAddresses": [], "caseIds": [], "policyNumbers": [], "orderNumbers": [], "suspiciousKeywords": []}}
- [PASS] intelligence::phone_space_normalized
  Details: {"input": "Call me at +91 8765432109 now.", "output": {"bankAccounts": [], "upiIds": [], "phishingLinks": [], "phoneNumbers": ["+91-8765432109"], "emailAddresses": [], "caseIds": [], "policyNumbers": [], "orderNumbers": [], "suspiciousKeywords": []}}
- [PASS] intelligence::upi_fakebank_detected
  Details: {"input": "Transfer to scammer.fraud@fakebank for verification.", "output": {"bankAccounts": [], "upiIds": ["scammer.fraud@fakebank"], "phishingLinks": [], "phoneNumbers": [], "emailAddresses": [], "caseIds": [], "policyNumbers": [], "orderNumbers": [], "suspiciousKeywords": ["transfer"]}}
- [PASS] intelligence::email_not_upi_fragment
  Details: {"input": "Contact offers@fake-amazon-deals.com for support.", "output": {"bankAccounts": [], "upiIds": [], "phishingLinks": [], "phoneNumbers": [], "emailAddresses": ["offers@fake-amazon-deals.com"], "caseIds": [], "policyNumbers": [], "orderNumbers": [], "suspiciousKeywords": []}}
- [PASS] intelligence::bank_account_detected
  Details: {"input": "Account number 1234567890123456 needs verification.", "output": {"bankAccounts": ["1234567890123456"], "upiIds": [], "phishingLinks": [], "phoneNumbers": [], "emailAddresses": [], "caseIds": [], "policyNumbers": [], "orderNumbers": [], "suspiciousKeywords": []}}
- [PASS] intelligence::phone_not_bank_account
  Details: {"input": "Call 9876543210 immediately.", "output": {"bankAccounts": [], "upiIds": [], "phishingLinks": [], "phoneNumbers": ["+91-9876543210"], "emailAddresses": [], "caseIds": [], "policyNumbers": [], "orderNumbers": [], "suspiciousKeywords": ["immediate"]}}
- [PASS] intelligence::url_trailing_punctuation_trimmed
  Details: {"input": "Click http://amaz0n-deals.fake-site.com/claim?id=12345.", "output": {"bankAccounts": [], "upiIds": [], "phishingLinks": ["http://amaz0n-deals.fake-site.com/claim?id=12345"], "phoneNumbers": [], "emailAddresses": [], "caseIds": [], "policyNumbers": [], "orderNumbers": [], "suspiciousKeywords": []}}
- [PASS] intelligence::case_policy_order_extraction
  Details: {"input": "Case REF-2026-001, policy POL-778899, order ORD-556677.", "output": {"bankAccounts": [], "upiIds": [], "phishingLinks": [], "phoneNumbers": [], "emailAddresses": [], "caseIds": ["REF-2026", "POL-778899", "ORD-556677"], "policyNumbers": ["POL-778899"], "orderNumbers": ["ORD-556677"], "suspiciousKeywords": []}}
- [PASS] scam_detector::legit_domain_detected
  Details: {"input": "https://www.amazon.in/help", "is_legit": true, "urls": ["www.amazon.in"]}
- [FAIL] scam_detector::domain_spoofing_not_whitelisted
  Details: {"input": "https://amazon.in.verify-now.ru/login", "is_legit": true, "urls": ["amazon.in.verify-now.ru"]}
- [FAIL] scam_detector::otp_phrase_not_blindly_legit
  Details: {"input": "Your OTP is 456789. Share now to unblock account.", "automated_detected": true}
- [PASS] scam_detector::strong_scam_indicators_detected
  Details: {"input": "Your account will be blocked today. Share your OTP immediately.", "patterns": ["account (will be )?(blocked|suspended|closed) today", "share (your )?(otp|pin|password)"]}
- [PASS] scam_detector::analyze_quick_flags_obvious_scam
  Details: {"output": {"is_scam": true, "confidence": 0.85, "detected_patterns": ["share (your )?(otp|pin|password)"], "reasoning": "Quick scan: scam patterns detected"}}
- [PASS] route::spec_shape_on_valid_request
  Details: {"status_code": 200, "elapsed_ms": 9.07, "keys": ["status", "reply", "sessionId", "scamDetected", "scamType", "confidenceLevel", "extractedIntelligence", "totalMessagesExchanged", "engagementDurationSeconds", "engagementMetrics", "agentNotes"]}
- [PASS] route::callback_triggered_on_scam_turn_3_plus
  Details: {"status_code": 200, "callback_calls": 1, "scamDetected": true}
- [PASS] route::callback_not_triggered_for_legit
  Details: {"status_code": 200, "callback_calls_before": 1, "callback_calls_after": 1, "scamDetected": false}
- [PASS] route::invalid_api_key_rejected
  Details: {"status_code": 401, "body": "{\"detail\":\"Invalid API Key\"}"}
- [PASS] route::missing_api_key_behavior
  Details: {"status_code": 422, "body": "{\"detail\":[{\"type\":\"missing\",\"loc\":[\"header\",\"x-api-key\"],\"msg\":\"Field required\",\"input\":null}]}"}
- [PASS] route::malformed_json_fallback_response
  Details: {"status_code": 200, "keys": ["status", "reply", "sessionId", "scamDetected", "scamType", "confidenceLevel", "extractedIntelligence", "totalMessagesExchanged", "engagementDurationSeconds", "engagementMetrics", "agentNotes"]}
- [FAIL] live_endpoint::health_reachable
  Details: {"error": "ConnectionError: HTTPSConnectionPool(host='guvi-honeypot-07tp.onrender.com', port=443): Max retries exceeded with url: /health (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x00000147EFCB0050>: Failed to establish a new connection: [WinError 10013] An attempt was made to access a socket in a way forbidden by its access permissions'))"}
