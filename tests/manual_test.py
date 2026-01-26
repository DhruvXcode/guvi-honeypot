
import asyncio
from app.services.intelligence import IntelligenceService

async def test_intelligence_extraction():
    print("Testing Intelligence Extraction...")
    service = IntelligenceService()
    
    text = "Please transfer money to 123456789012 or send to scammer@okicici. Verify at http://fake-bank.com immediately!"
    
    intel = service.extract(text)
    print(f"Extracted: {intel}")
    
    # Check Bank Account (Positive)
    if "123456789012" in intel.bankAccounts:
        print("✅ Bank Account Extraction: PASS")
    else:
        print("❌ Bank Account Extraction: FAIL (Expected 123456789012)")

    # Check Timestamp (Negative)
    # The input text didn't have timestamp, let's add a test case for it
    ts_text = "Meeting at 1700000000"
    ts_intel = service.extract(ts_text)
    if not ts_intel.bankAccounts:
        print("✅ Timestamp Exclusion: PASS (Ignored 1700000000)")
    else:
        print(f"❌ Timestamp Exclusion: FAIL (Captured {ts_intel.bankAccounts})")
    
    # Check UPI
    if "scammer@okicici" in intel.upiIds:
        print("✅ UPI Extraction: PASS")
    else:
        print("❌ UPI Extraction: FAIL")
    
    # Check URL
    if "http://fake-bank.com" in intel.phishingLinks:
        print("✅ URL Extraction: PASS")
    else:
        print("❌ URL Extraction: FAIL")
    
    # Check Keywords
    if "verify" in intel.suspiciousKeywords:
        print("✅ Keyword Extraction: PASS")
    else:
        print("❌ Keyword Extraction: FAIL")

if __name__ == "__main__":
    asyncio.run(test_intelligence_extraction())
