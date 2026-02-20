import asyncio
import os
import statistics
import time

import httpx
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('HONEYPOT_API_KEY', '')
URL = 'http://127.0.0.1:8000/honeypot'


def build_payload(i: int):
    return {
        'sessionId': f'load-{i}',
        'message': {
            'sender': 'scammer',
            'text': 'URGENT your account will be blocked today share OTP now',
            'timestamp': '2026-02-20T10:00:00Z',
        },
        'conversationHistory': [],
        'metadata': {'channel': 'SMS', 'language': 'English', 'locale': 'IN'},
    }


async def one(client: httpx.AsyncClient, i: int):
    started = time.perf_counter()
    try:
        res = await client.post(URL, json=build_payload(i), headers={'x-api-key': API_KEY}, timeout=30.0)
        elapsed = (time.perf_counter() - started) * 1000
        ok = res.status_code == 200
        return {'ok': ok, 'status': res.status_code, 'elapsed_ms': elapsed}
    except Exception as exc:
        elapsed = (time.perf_counter() - started) * 1000
        return {'ok': False, 'status': None, 'elapsed_ms': elapsed, 'error': f'{type(exc).__name__}: {exc}'}


async def run(total=20, concurrency=5):
    sem = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient() as client:
        async def wrapped(i):
            async with sem:
                return await one(client, i)

        tasks = [asyncio.create_task(wrapped(i)) for i in range(total)]
        return await asyncio.gather(*tasks)


def percentile(values, p):
    if not values:
        return 0.0
    values_sorted = sorted(values)
    idx = int(round((p / 100.0) * (len(values_sorted) - 1)))
    return values_sorted[idx]


def main():
    results = asyncio.run(run(total=20, concurrency=5))
    latencies = [r['elapsed_ms'] for r in results if r.get('ok')]
    failed = [r for r in results if not r.get('ok')]

    print('total', len(results))
    print('passed', len(latencies))
    print('failed', len(failed))
    if latencies:
        print('latency_ms_min', round(min(latencies), 2))
        print('latency_ms_avg', round(statistics.mean(latencies), 2))
        print('latency_ms_p95', round(percentile(latencies, 95), 2))
        print('latency_ms_max', round(max(latencies), 2))
    if failed:
        print('sample_failure', failed[0])


if __name__ == '__main__':
    main()
