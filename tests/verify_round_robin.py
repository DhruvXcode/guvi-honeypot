"""Verify round-robin LLM and agentNotes fix."""
import asyncio, sys, os

# Ensure we load from .env
from dotenv import load_dotenv
load_dotenv()

def test_round_robin_init():
    """Test that round-robin counters are initialized correctly."""
    from app.services.agent import AgentService
    agent = AgentService()
    assert hasattr(agent, '_call_counter'), 'Missing _call_counter in agent'
    assert agent._call_counter == 0
    assert not hasattr(agent, 'use_cerebras'), 'use_cerebras should be removed from agent!'
    print('PASS: Agent round-robin counter initialized')

    from app.services.scam_detector import ScamDetectorService
    detector = ScamDetectorService()
    assert hasattr(detector, '_call_counter'), 'Missing _call_counter in detector'
    assert detector._call_counter == 0
    assert not hasattr(detector, 'use_cerebras'), 'use_cerebras should be removed from detector!'
    print('PASS: Scam detector round-robin counter initialized')
    return detector

def test_scam_detection(detector):
    """Test scam detection still works with strong indicators."""
    analysis = asyncio.run(detector.analyze(
        'URGENT: Your account blocked! Share OTP now or face legal action!'
    ))
    assert analysis.is_scam == True, f'Expected scam, got {analysis.is_scam}'
    assert analysis.confidence >= 0.8, f'Low confidence: {analysis.confidence}'
    print(f'PASS: Scam detected - is_scam={analysis.is_scam}, confidence={analysis.confidence}')
    
    # Check reasoning doesn't expose "rate limit"
    if analysis.reasoning and 'rate limit' in analysis.reasoning.lower():
        print(f'FAIL: Reasoning exposes rate limiting: {analysis.reasoning}')
        sys.exit(1)
    print(f'PASS: Clean reasoning: {analysis.reasoning[:80]}')

def test_fallback_reasoning(detector):
    """Test that the fallback reasoning is clean (no 'rate limited' text)."""
    from app.models import ScamAnalysis
    # The fallback text is in the code - verify it doesn't mention rate limiting
    import inspect
    source = inspect.getsource(detector.analyze)
    if 'LLM rate limited' in source:
        print('FAIL: Still has "LLM rate limited" in fallback reasoning')
        sys.exit(1)
    if 'llm_fallback' in source:
        print('FAIL: Still has "llm_fallback" in detected_patterns')
        sys.exit(1)
    print('PASS: Fallback reasoning is clean (no rate limit exposure)')

def test_intel_extraction():
    """Test intelligence extraction works correctly."""
    from app.services.intelligence import IntelligenceService
    intel = IntelligenceService()
    result = intel.extract(
        'Call me at +91-9876543210 and use UPI scammer.fraud@fakebank, '
        'account 1234567890123456, link https://secure-fakebank.com/verify'
    )
    assert len(result.phoneNumbers) > 0, 'No phone numbers extracted'
    assert len(result.upiIds) > 0, 'No UPI IDs extracted'
    assert len(result.bankAccounts) > 0, 'No bank accounts extracted'
    assert len(result.phishingLinks) > 0, 'No phishing links extracted'
    print(f'PASS: Intel extraction - phones={result.phoneNumbers}, '
          f'upi={result.upiIds}, bank={result.bankAccounts}, '
          f'links={result.phishingLinks}')

def test_round_robin_methods_exist():
    """Verify the new round-robin methods exist."""
    from app.services.agent import AgentService
    agent = AgentService()
    assert hasattr(agent, '_try_groq'), 'Missing _try_groq in agent'
    assert hasattr(agent, '_try_cerebras'), 'Missing _try_cerebras in agent'
    print('PASS: Agent has _try_groq and _try_cerebras methods')
    
    from app.services.scam_detector import ScamDetectorService
    detector = ScamDetectorService()
    assert hasattr(detector, '_try_groq_detection'), 'Missing _try_groq_detection'
    assert hasattr(detector, '_try_cerebras_detection'), 'Missing _try_cerebras_detection'
    print('PASS: Detector has _try_groq_detection and _try_cerebras_detection methods')

if __name__ == '__main__':
    print('=' * 60)
    print('Round-Robin LLM & AgentNotes Verification')
    print('=' * 60)
    
    detector = test_round_robin_init()
    test_round_robin_methods_exist()
    test_fallback_reasoning(detector)
    test_scam_detection(detector)
    test_intel_extraction()
    
    print()
    print('=' * 60)
    print('ALL TESTS PASSED')
    print('=' * 60)
