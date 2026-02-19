"""Minimal test to find the failure."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.intelligence import IntelligenceService
svc = IntelligenceService()

# Test each case and print PASS/FAIL only
tests = []

# T1: Email vs UPI
intel = svc.extract("email us at offers@fake-amazon-deals.com for assistance")
fp = [u for u in intel.upiIds if "offers@fake" in u.lower()]
tests.append(("T1-EmailUPI", "FAIL" if fp else "PASS", f"UPIs={intel.upiIds} Emails={intel.emailAddresses}"))

# T2: Phone +91-hyphen
intel = svc.extract("Call at +91-9876543210 now")
m = any("+91-9876543210" in str(v) for v in intel.phoneNumbers)
tests.append(("T2-PhoneHyphen", "PASS" if m else "FAIL", f"phones={intel.phoneNumbers}"))

# T3: Phone +91-space  
intel = svc.extract("Call +91 8765432109 now")
m = any("+91-8765432109" in str(v) for v in intel.phoneNumbers)
tests.append(("T3-PhoneSpace", "PASS" if m else "FAIL", f"phones={intel.phoneNumbers} (need +91-8765432109 substring)"))

# T4: UPI fakebank
intel = svc.extract("transfer to scammer.fraud@fakebank")
m = any("scammer.fraud@fakebank" in str(v) for v in intel.upiIds)
tests.append(("T4-UPI-fakebank", "PASS" if m else "FAIL", f"upis={intel.upiIds}"))

# T5: UPI fakeupi
intel = svc.extract("send to cashback.scam@fakeupi")
m = any("cashback.scam@fakeupi" in str(v) for v in intel.upiIds)
tests.append(("T5-UPI-fakeupi", "PASS" if m else "FAIL", f"upis={intel.upiIds}"))

# T6: Bank account
intel = svc.extract("account number 1234567890123456")
m = any("1234567890123456" in str(v) for v in intel.bankAccounts)
tests.append(("T6-Bank", "PASS" if m else "FAIL", f"banks={intel.bankAccounts}"))

# T7: Phishing link
intel = svc.extract("Click: http://amaz0n-deals.fake-site.com/claim?id=12345")
m = any("http://amaz0n-deals.fake-site.com/claim?id=12345" in str(v) for v in intel.phishingLinks)
tests.append(("T7-Link", "PASS" if m else "FAIL", f"links={intel.phishingLinks}"))

# T8: Email
intel = svc.extract("contact offers@fake-amazon-deals.com")
m = any("offers@fake-amazon-deals.com" in str(v) for v in intel.emailAddresses)
tests.append(("T8-Email", "PASS" if m else "FAIL", f"emails={intel.emailAddresses}"))

for name, result, detail in tests:
    print(f"{result}: {name} | {detail}")

fails = [t for t in tests if t[1] == "FAIL"]
print(f"\nTotal: {len(tests)-len(fails)}/{len(tests)} passed")
