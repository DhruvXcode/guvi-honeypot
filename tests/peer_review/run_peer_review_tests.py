import json
import time
from pathlib import Path

import requests
from fastapi.testclient import TestClient

from app.config import settings
from app.models import ExtractedIntelligence, ScamAnalysis
from app.routes import honeypot as hp
from app.services.intelligence import IntelligenceService
from app.services.scam_detector import ScamDetectorService
from main import app


OUT_DIR = Path('tests/peer_review')
OUT_DIR.mkdir(parents=True, exist_ok=True)


def record_case(store, suite, name, passed, details):
    store.append({
        'suite': suite,
        'name': name,
        'passed': bool(passed),
        'details': details,
    })


def run_intelligence_suite(results):
    service = IntelligenceService()

    cases = [
        {
            'name': 'phone_hyphen_preserved',
            'text': 'Call me at +91-9876543210 now.',
            'assertion': lambda intel: '+91-9876543210' in intel.phoneNumbers,
        },
        {
            'name': 'phone_space_normalized',
            'text': 'Call me at +91 8765432109 now.',
            'assertion': lambda intel: '+91-8765432109' in intel.phoneNumbers,
        },
        {
            'name': 'upi_fakebank_detected',
            'text': 'Transfer to scammer.fraud@fakebank for verification.',
            'assertion': lambda intel: 'scammer.fraud@fakebank' in intel.upiIds,
        },
        {
            'name': 'email_not_upi_fragment',
            'text': 'Contact offers@fake-amazon-deals.com for support.',
            'assertion': lambda intel: (
                'offers@fake-amazon-deals.com' in intel.emailAddresses
                and not any('offers@fake' == u.lower() for u in intel.upiIds)
            ),
        },
        {
            'name': 'bank_account_detected',
            'text': 'Account number 1234567890123456 needs verification.',
            'assertion': lambda intel: '1234567890123456' in intel.bankAccounts,
        },
        {
            'name': 'phone_not_bank_account',
            'text': 'Call 9876543210 immediately.',
            'assertion': lambda intel: '9876543210' not in intel.bankAccounts,
        },
        {
            'name': 'url_trailing_punctuation_trimmed',
            'text': 'Click http://amaz0n-deals.fake-site.com/claim?id=12345.',
            'assertion': lambda intel: 'http://amaz0n-deals.fake-site.com/claim?id=12345' in intel.phishingLinks,
        },
        {
            'name': 'case_policy_order_extraction',
            'text': 'Case REF-2026-001, policy POL-778899, order ORD-556677.',
            'assertion': lambda intel: (
                'REF-2026' in intel.caseIds
                and 'POL-778899' in intel.policyNumbers
                and 'ORD-556677' in intel.orderNumbers
            ),
        },
    ]

    for case in cases:
        intel = service.extract(case['text'])
        passed = False
        try:
            passed = bool(case['assertion'](intel))
        except Exception:
            passed = False

        record_case(
            results,
            'intelligence',
            case['name'],
            passed,
            {
                'input': case['text'],
                'output': intel.model_dump(),
            },
        )


def run_scam_detector_suite(results):
    detector = ScamDetectorService()

    legit, urls = detector._check_url_legitimacy('Visit https://www.amazon.in/help')
    record_case(
        results,
        'scam_detector',
        'legit_domain_detected',
        legit is True,
        {'input': 'https://www.amazon.in/help', 'is_legit': legit, 'urls': urls},
    )

    # Should be suspicious, but current logic uses substring matching and may misclassify.
    legit, urls = detector._check_url_legitimacy('Urgent verify at https://amazon.in.verify-now.ru/login')
    record_case(
        results,
        'scam_detector',
        'domain_spoofing_not_whitelisted',
        legit is False,
        {'input': 'https://amazon.in.verify-now.ru/login', 'is_legit': legit, 'urls': urls},
    )

    automated = detector._is_automated_message('Your OTP is 456789. Share now to unblock account.')
    record_case(
        results,
        'scam_detector',
        'otp_phrase_not_blindly_legit',
        automated is False,
        {'input': 'Your OTP is 456789. Share now to unblock account.', 'automated_detected': automated},
    )

    has_scam, patterns = detector._has_strong_scam_indicators(
        'Your account will be blocked today. Share your OTP immediately.'
    )
    record_case(
        results,
        'scam_detector',
        'strong_scam_indicators_detected',
        has_scam is True,
        {'input': 'Your account will be blocked today. Share your OTP immediately.', 'patterns': patterns},
    )

    quick = None
    try:
        import asyncio

        quick = asyncio.run(detector.analyze_quick('Your account is blocked today. Share OTP now.'))
        passed = quick.is_scam is True
    except Exception as exc:
        passed = False
        quick = {'error': str(exc)}

    record_case(
        results,
        'scam_detector',
        'analyze_quick_flags_obvious_scam',
        passed,
        {'output': quick.model_dump() if hasattr(quick, 'model_dump') else quick},
    )


def run_route_suite(results):
    class StubScamDetector:
        async def analyze(self, message, history=None):
            text = (message or '').lower()
            if 'legit' in text:
                return ScamAnalysis(
                    is_scam=False,
                    confidence=0.88,
                    detected_patterns=['manual_legit_stub'],
                    reasoning='Stub classified as legitimate',
                )
            return ScamAnalysis(
                is_scam=True,
                confidence=0.93,
                detected_patterns=['manual_scam_stub'],
                reasoning='Stub classified as scam',
            )

    class StubAgent:
        async def generate_response(self, **kwargs):
            return 'ji samajh nahi aa raha.. aapka number kya hai?? aap kis company se ho ji??'

    class StubCallback:
        def __init__(self):
            self.calls = []

        async def send_final_result(self, **kwargs):
            self.calls.append(kwargs)
            return True

    original_scam = hp.scam_detector
    original_agent = hp.agent_service
    original_callback = hp.callback_service

    stub_callback = StubCallback()
    hp.scam_detector = StubScamDetector()
    hp.agent_service = StubAgent()
    hp.callback_service = stub_callback

    old_key = settings.HONEYPOT_API_KEY
    settings.HONEYPOT_API_KEY = 'peer-review-key'

    try:
        client = TestClient(app)

        payload = {
            'sessionId': 'peer-1',
            'message': {'sender': 'scammer', 'text': 'share otp now', 'timestamp': '2026-02-20T10:00:00Z'},
            'conversationHistory': [],
            'metadata': {'channel': 'SMS', 'language': 'English', 'locale': 'IN'},
        }

        start = time.perf_counter()
        res = client.post('/honeypot', json=payload, headers={'x-api-key': 'peer-review-key'})
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        data = res.json() if res.status_code == 200 else {}
        required_keys = ['status', 'reply', 'scamDetected', 'extractedIntelligence', 'engagementMetrics', 'agentNotes']
        passed = res.status_code == 200 and all(k in data for k in required_keys)

        record_case(
            results,
            'route',
            'spec_shape_on_valid_request',
            passed,
            {
                'status_code': res.status_code,
                'elapsed_ms': elapsed_ms,
                'keys': list(data.keys()),
            },
        )

        # Callback should trigger from turn >= 3 when scam is true. Provide history of 2 messages.
        payload2 = {
            'sessionId': 'peer-2',
            'message': {'sender': 'scammer', 'text': 'share otp now', 'timestamp': '2026-02-20T10:01:00Z'},
            'conversationHistory': [
                {'sender': 'scammer', 'text': 'hello', 'timestamp': 1730000000000},
                {'sender': 'user', 'text': 'hi', 'timestamp': 1730000005000},
            ],
            'metadata': {'channel': 'WhatsApp', 'language': 'English', 'locale': 'IN'},
        }

        res2 = client.post('/honeypot', json=payload2, headers={'x-api-key': 'peer-review-key'})
        data2 = res2.json() if res2.status_code == 200 else {}
        callback_triggered = len(stub_callback.calls) >= 1

        record_case(
            results,
            'route',
            'callback_triggered_on_scam_turn_3_plus',
            callback_triggered,
            {
                'status_code': res2.status_code,
                'callback_calls': len(stub_callback.calls),
                'scamDetected': data2.get('scamDetected'),
            },
        )

        # Legit message should not trigger callback due should_send_callback.
        before = len(stub_callback.calls)
        payload3 = {
            'sessionId': 'peer-3',
            'message': {'sender': 'scammer', 'text': 'legit monthly bill notice', 'timestamp': '2026-02-20T10:02:00Z'},
            'conversationHistory': [
                {'sender': 'scammer', 'text': 'bill reminder', 'timestamp': 1730000000000},
                {'sender': 'user', 'text': 'ok', 'timestamp': 1730000005000},
            ],
            'metadata': {'channel': 'SMS', 'language': 'English', 'locale': 'IN'},
        }

        res3 = client.post('/honeypot', json=payload3, headers={'x-api-key': 'peer-review-key'})
        data3 = res3.json() if res3.status_code == 200 else {}
        after = len(stub_callback.calls)

        record_case(
            results,
            'route',
            'callback_not_triggered_for_legit',
            after == before,
            {
                'status_code': res3.status_code,
                'callback_calls_before': before,
                'callback_calls_after': after,
                'scamDetected': data3.get('scamDetected'),
            },
        )

        # Invalid auth should return 401.
        res4 = client.post('/honeypot', json=payload, headers={'x-api-key': 'wrong-key'})
        record_case(
            results,
            'route',
            'invalid_api_key_rejected',
            res4.status_code == 401,
            {'status_code': res4.status_code, 'body': res4.text[:200]},
        )

        # Missing API key currently returns 422 from FastAPI dependency validation.
        res5 = client.post('/honeypot', json=payload)
        record_case(
            results,
            'route',
            'missing_api_key_behavior',
            res5.status_code == 422,
            {'status_code': res5.status_code, 'body': res5.text[:200]},
        )

        # Malformed JSON path should still return a 200 fallback response.
        res6 = client.post('/honeypot', data='not-json', headers={'x-api-key': 'peer-review-key', 'Content-Type': 'application/json'})
        ok = res6.status_code == 200
        details = {'status_code': res6.status_code}
        if ok:
            details['keys'] = list(res6.json().keys())
        else:
            details['body'] = res6.text[:200]

        record_case(
            results,
            'route',
            'malformed_json_fallback_response',
            ok,
            details,
        )

    finally:
        hp.scam_detector = original_scam
        hp.agent_service = original_agent
        hp.callback_service = original_callback
        settings.HONEYPOT_API_KEY = old_key


def run_live_connectivity_suite(results):
    url = 'https://guvi-honeypot-07tp.onrender.com/health'
    try:
        started = time.perf_counter()
        res = requests.get(url, timeout=15)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        record_case(
            results,
            'live_endpoint',
            'health_reachable',
            res.status_code == 200,
            {'status_code': res.status_code, 'elapsed_ms': elapsed_ms, 'body': res.text[:200]},
        )
    except Exception as exc:
        record_case(
            results,
            'live_endpoint',
            'health_reachable',
            False,
            {'error': f'{type(exc).__name__}: {exc}'},
        )


def summarize(results):
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed

    by_suite = {}
    for row in results:
        suite = row['suite']
        by_suite.setdefault(suite, {'total': 0, 'passed': 0, 'failed': 0})
        by_suite[suite]['total'] += 1
        if row['passed']:
            by_suite[suite]['passed'] += 1
        else:
            by_suite[suite]['failed'] += 1

    return {
        'total': total,
        'passed': passed,
        'failed': failed,
        'pass_rate': round((passed / total) * 100, 2) if total else 0.0,
        'by_suite': by_suite,
    }


def write_outputs(results):
    summary = summarize(results)

    payload = {
        'generated_at_epoch_ms': int(time.time() * 1000),
        'summary': summary,
        'results': results,
    }

    json_path = OUT_DIR / 'results.json'
    json_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')

    lines = []
    lines.append('# Peer Review Test Log')
    lines.append('')
    lines.append('## Summary')
    lines.append(f"- Total: {summary['total']}")
    lines.append(f"- Passed: {summary['passed']}")
    lines.append(f"- Failed: {summary['failed']}")
    lines.append(f"- Pass Rate: {summary['pass_rate']}%")
    lines.append('')
    lines.append('## Suite Breakdown')
    for suite, metrics in summary['by_suite'].items():
        lines.append(f"- {suite}: {metrics['passed']}/{metrics['total']} passed, {metrics['failed']} failed")
    lines.append('')
    lines.append('## Detailed Results')
    for row in results:
        status = 'PASS' if row['passed'] else 'FAIL'
        lines.append(f"- [{status}] {row['suite']}::{row['name']}")
        lines.append(f"  Details: {json.dumps(row['details'], ensure_ascii=True)}")

    md_path = OUT_DIR / 'TEST-LOG.md'
    md_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    return json_path, md_path, summary


def main():
    results = []

    run_intelligence_suite(results)
    run_scam_detector_suite(results)
    run_route_suite(results)
    run_live_connectivity_suite(results)

    json_path, md_path, summary = write_outputs(results)

    print('Peer review tests completed.')
    print(f"Results JSON: {json_path}")
    print(f"Test Log: {md_path}")
    print(f"Passed: {summary['passed']} / {summary['total']}")


if __name__ == '__main__':
    main()
