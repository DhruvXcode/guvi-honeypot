"""Quick test to verify intelligence extraction edge cases."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.intelligence import IntelligenceService

svc = IntelligenceService()

print("=" * 60)
print("  INTEL EXTRACTION EDGE CASE TESTS")
print("=" * 60)

failures = []

# Test 1: Email should NOT be extracted as UPI
print("\n--- Test 1: Email vs UPI disambiguation ---")
text = "email us at offers@fake-amazon-deals.com for assistance"
intel = svc.extract(text)
print(f"  UPI IDs: {intel.upiIds}")
print(f"  Emails:  {intel.emailAddresses}")
false_upi = [u for u in intel.upiIds if "offers@fake" in u.lower()]
if false_upi:
    print(f"  FAIL: Email prefix extracted as UPI: {false_upi}")
    failures.append("Email->UPI false positive")
else:
    print(f"  PASS: No false UPI from email")

# Test 2: Phone format - must match GUVI substring check
print("\n--- Test 2: Phone format preservation ---")
text = "Call our officer at +91-9876543210 for quick resolution"
intel = svc.extract(text)
print(f"  Phones: {intel.phoneNumbers}")
fake = "+91-9876543210"
matched = any(fake in str(v) for v in intel.phoneNumbers)
print(f"  GUVI match for '{fake}': {matched}")
if not matched:
    failures.append(f"Phone format mismatch for {fake}")

# Test 3: Phone without hyphen
print("\n--- Test 3: Phone +91 without hyphen ---")
text = "Call +919876543210 now"
intel = svc.extract(text)
print(f"  Phones: {intel.phoneNumbers}")
matched = any("+91-9876543210" in str(v) or "9876543210" in str(v) for v in intel.phoneNumbers)
print(f"  Contains 9876543210: {matched}")

# Test 4: Phone with space
print("\n--- Test 4: Phone +91 with space ---")
text = "Call +91 8765432109 now"
intel = svc.extract(text)
print(f"  Phones: {intel.phoneNumbers}")
fake = "+91-8765432109"
matched = any(fake in str(v) for v in intel.phoneNumbers)
print(f"  GUVI match for '{fake}': {matched}")
if not matched:
    # Check if at least the digits are there
    matched2 = any("8765432109" in str(v) for v in intel.phoneNumbers)
    print(f"  Fallback digits match: {matched2}")
    if not matched2:
        failures.append(f"Phone format mismatch for {fake}")

# Test 5: UPI ID extraction
print("\n--- Test 5: UPI ID extraction ---")
text = "transfer to UPI ID scammer.fraud@fakebank to unlock"
intel = svc.extract(text)
print(f"  UPI IDs: {intel.upiIds}")
fake = "scammer.fraud@fakebank"
matched = any(fake in str(v) for v in intel.upiIds)
print(f"  GUVI match for '{fake}': {matched}")
if not matched:
    failures.append(f"UPI mismatch for {fake}")

# Test 6: UPI ID cashback.scam@fakeupi
print("\n--- Test 6: UPI cashback format ---")
text = "send Rs. 10 to cashback.scam@fakeupi for verification"
intel = svc.extract(text)
print(f"  UPI IDs: {intel.upiIds}")
fake = "cashback.scam@fakeupi"
matched = any(fake in str(v) for v in intel.upiIds)
print(f"  GUVI match for '{fake}': {matched}")
if not matched:
    failures.append(f"UPI mismatch for {fake}")

# Test 7: Bank account
print("\n--- Test 7: Bank account ---")
text = "account number 1234567890123456 needs verification"
intel = svc.extract(text)
print(f"  Banks: {intel.bankAccounts}")
fake = "1234567890123456"
matched = any(fake in str(v) for v in intel.bankAccounts)
print(f"  GUVI match for '{fake}': {matched}")
if not matched:
    failures.append(f"Bank mismatch for {fake}")

# Test 8: Phishing link
print("\n--- Test 8: Phishing link ---")
text = "Click here: http://amaz0n-deals.fake-site.com/claim?id=12345"
intel = svc.extract(text)
print(f"  Links: {intel.phishingLinks}")
fake = "http://amaz0n-deals.fake-site.com/claim?id=12345"
matched = any(fake in str(v) for v in intel.phishingLinks)
print(f"  GUVI match for '{fake}': {matched}")
if not matched:
    failures.append(f"Link mismatch for {fake}")

# Test 9: Email address
print("\n--- Test 9: Email extraction ---")
text = "contact offers@fake-amazon-deals.com for help"
intel = svc.extract(text)
print(f"  Emails: {intel.emailAddresses}")
fake = "offers@fake-amazon-deals.com"
matched = any(fake in str(v) for v in intel.emailAddresses)
print(f"  GUVI match for '{fake}': {matched}")
if not matched:
    failures.append(f"Email mismatch for {fake}")

# Summary
print(f"\n{'=' * 60}")
if failures:
    print(f"  FAILURES ({len(failures)}):")
    for f in failures:
        print(f"    - {f}")
else:
    print("  ALL TESTS PASSED!")
print(f"{'=' * 60}")
