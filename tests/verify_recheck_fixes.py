"""Verify the 3 recheck fixes from peer review."""
import asyncio
from app.services.scam_detector import ScamDetectorService


async def test():
    detector = ScamDetectorService()
    passed = 0
    total = 0
    
    print("=== RECHECK 1: Legit URL no longer short-circuits scam detection ===")
    
    # THE ADVERSARIAL PROBE from peer review
    total += 1
    adversarial = "Your account is blocked. Share OTP now at https://www.sbi.co.in/login"
    r = await detector.analyze(adversarial)
    status = "PASS" if r.is_scam else "FAIL"
    if r.is_scam:
        passed += 1
    print(f"  Adversarial (legit URL + scam): is_scam={r.is_scam}, conf={r.confidence} -> {status}")
    
    # KYC scam with legit link
    total += 1
    adv2 = "URGENT: KYC expiring! Visit https://www.sbi.co.in to update or account will be blocked today"
    r2 = await detector.analyze(adv2)
    status2 = "PASS" if r2.is_scam else "FAIL"
    if r2.is_scam:
        passed += 1
    print(f"  KYC scam + legit URL: is_scam={r2.is_scam}, conf={r2.confidence} -> {status2}")
    
    print()
    print("=== RECHECK 2: Port normalization ===")
    
    # amazon.in:443 should be recognized as legit
    total += 1
    legit, urls = detector._check_url_legitimacy("Check https://amazon.in:443/deals")
    status3 = "PASS" if legit else "FAIL"
    if legit:
        passed += 1
    print(f"  amazon.in:443 recognized as legit: {legit} -> {status3}")
    
    # Spoofed with port should still fail
    total += 1
    legit3, _ = detector._check_url_legitimacy("Visit https://amazon.in.evil.com:443/hack")
    status4 = "PASS" if not legit3 else "FAIL"
    if not legit3:
        passed += 1
    print(f"  amazon.in.evil.com:443 (spoofed + port): legit={legit3} -> {status4}")
    
    print()
    print("=== SANITY: Standard scam still detected ===")
    
    total += 1
    standard = "URGENT: Your SBI account compromised. Share OTP 123456 immediately."
    r5 = await detector.analyze(standard)
    status5 = "PASS" if r5.is_scam else "FAIL"
    if r5.is_scam:
        passed += 1
    print(f"  Standard scam: is_scam={r5.is_scam}, conf={r5.confidence} -> {status5}")
    
    # OTP + coercive
    total += 1
    otp_scam = "Your OTP is 456789. Share now to unblock account."
    r6 = await detector.analyze(otp_scam)
    status6 = "PASS" if r6.is_scam else "FAIL"
    if r6.is_scam:
        passed += 1
    print(f"  OTP + coercive: is_scam={r6.is_scam}, conf={r6.confidence} -> {status6}")
    
    print()
    print(f"RESULT: {passed}/{total} passed")
    if passed == total:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")


if __name__ == "__main__":
    asyncio.run(test())
