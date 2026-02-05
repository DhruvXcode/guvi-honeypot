2026-02-05T19:07:22.393077918Z Using cached six-1.17.0-py2.py3-none-any.whl (11 kB)
2026-02-05T19:07:22.394728901Z Using cached tqdm-4.67.3-py3-none-any.whl (78 kB)
2026-02-05T19:07:22.395988654Z Using cached typing_inspection-0.4.2-py3-none-any.whl (14 kB)
2026-02-05T19:07:22.397108223Z Using cached httptools-0.7.1-cp313-cp313-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (478 kB)
2026-02-05T19:07:22.398659884Z Using cached pyyaml-6.0.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (801 kB)
2026-02-05T19:07:22.400477581Z Using cached uvloop-0.22.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (4.4 MB)
2026-02-05T19:07:22.40580588Z Using cached watchfiles-1.1.1-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (456 kB)
2026-02-05T19:07:22.407532745Z Using cached websockets-16.0-cp313-cp313-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (184 kB)
2026-02-05T19:07:22.408748447Z Using cached certifi-2026.1.4-py3-none-any.whl (152 kB)
2026-02-05T19:07:22.409959258Z Using cached sniffio-1.3.1-py3-none-any.whl (10 kB)
2026-02-05T19:07:22.494944212Z Installing collected packages: websockets, uvloop, typing-extensions, tqdm, sniffio, six, pyyaml, python-dotenv, jiter, idna, httptools, h11, distro, click, certifi, annotated-types, annotated-doc, uvicorn, typing-inspection, python-dateutil, pydantic-core, httpcore, anyio, watchfiles, starlette, pydantic, httpx, openai, groq, fastapi
2026-02-05T19:07:29.431419203Z 
2026-02-05T19:07:29.43551649Z Successfully installed annotated-doc-0.0.4 annotated-types-0.7.0 anyio-4.12.1 certifi-2026.1.4 click-8.3.1 distro-1.9.0 fastapi-0.128.1 groq-1.0.0 h11-0.16.0 httpcore-1.0.9 httptools-0.7.1 httpx-0.28.1 idna-3.11 jiter-0.13.0 openai-2.17.0 pydantic-2.12.5 pydantic-core-2.41.5 python-dateutil-2.9.0.post0 python-dotenv-1.2.1 pyyaml-6.0.3 six-1.17.0 sniffio-1.3.1 starlette-0.50.0 tqdm-4.67.3 typing-extensions-4.15.0 typing-inspection-0.4.2 uvicorn-0.40.0 uvloop-0.22.1 watchfiles-1.1.1 websockets-16.0
2026-02-05T19:07:29.442034659Z 
2026-02-05T19:07:29.4420441Z [notice] A new release of pip is available: 25.1.1 -> 26.0
2026-02-05T19:07:29.44204696Z [notice] To update, run: pip install --upgrade pip
2026-02-05T19:07:33.454079752Z ==> Uploading build...
2026-02-05T19:07:46.88259657Z ==> Uploaded in 8.9s. Compression took 4.6s
2026-02-05T19:07:47.771503468Z ==> Build successful 🎉
2026-02-05T19:08:18.961343046Z ==> Deploying...
2026-02-05T19:08:19.425949571Z ==> Setting WEB_CONCURRENCY=1 by default, based on available CPUs in the instance
2026-02-05T19:08:48.241872383Z ==> Running 'uvicorn main:app --host 0.0.0.0 --port $PORT'
2026-02-05T19:09:02.449138772Z INFO:     Started server process [56]
2026-02-05T19:09:02.449176163Z INFO:     Waiting for application startup.
2026-02-05T19:09:02.449427569Z INFO:     Application startup complete.
2026-02-05T19:09:02.450876603Z INFO:     Uvicorn running on http://0.0.0.0:10000 (Press CTRL+C to quit)
2026-02-05T19:09:03.094759248Z INFO:     127.0.0.1:50130 - "HEAD / HTTP/1.1" 405 Method Not Allowed
2026-02-05T19:09:11.91701132Z ==> Your service is live 🎉
2026-02-05T19:09:12.154595117Z ==> 
2026-02-05T19:09:12.157133631Z ==> ///////////////////////////////////////////////////////////
2026-02-05T19:09:12.159335187Z ==> 
2026-02-05T19:09:12.161304351Z ==> Available at your primary URL https://guvi-honeypot-07tp.onrender.com
2026-02-05T19:09:12.164105759Z ==> 
2026-02-05T19:09:12.167170031Z ==> ///////////////////////////////////////////////////////////
2026-02-05T19:09:12.476904267Z INFO:     35.197.118.178:0 - "GET / HTTP/1.1" 200 OK
2026-02-05T19:09:38.890795148Z INFO:app.routes.honeypot:Received request body: {'sessionId': 'c23562ac-bdb6-4bba-bcf7-b966e44e60c2', 'message': {'sender': 'scammer', 'text': 'URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.', 'timestamp': 1770318578707}, 'conversationHistory': [], 'metadata': {'channel': 'SMS', 'language': 'English', 'locale': 'IN'}}
2026-02-05T19:09:38.890817748Z INFO:app.routes.honeypot:[c23562ac-bdb6-4bba-bcf7-b966e44e60c2] Received message on SMS: URGENT: Your SBI account has been compromised. You...
2026-02-05T19:09:39.680683817Z INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:09:39.745653315Z INFO:app.routes.honeypot:[c23562ac-bdb6-4bba-bcf7-b966e44e60c2] Scam analysis: is_scam=True, confidence=0.90
2026-02-05T19:09:39.746808022Z INFO:app.routes.honeypot:[c23562ac-bdb6-4bba-bcf7-b966e44e60c2] Intel extracted: {'bankAccounts': [], 'upiIds': [], 'phishingLinks': [], 'phoneNumbers': [], 'suspiciousKeywords': ['blocked', 'urgent', 'immediate', 'verify', 'otp']}
2026-02-05T19:09:39.92867358Z INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 429 Too Many Requests"
2026-02-05T19:09:39.929327526Z WARNING:app.services.agent:Groq rate limited, switching to Cerebras: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01k2ksctbeecsry0yrk9rxppp5` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99557, Requested 1865. Please try again in 20m28.608s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}
2026-02-05T19:09:39.929344796Z INFO:app.services.agent:Using Cerebras fallback (llama-3.3-70b)...
2026-02-05T19:09:45.270173941Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:09:45.278320592Z INFO:app.routes.honeypot:[c23562ac-bdb6-4bba-bcf7-b966e44e60c2] Agent response: beta can you call me.. i will understand better on...
2026-02-05T19:09:45.278590649Z INFO:     43.204.10.11:0 - "POST /honeypot HTTP/1.1" 200 OK
2026-02-05T19:09:47.156576512Z INFO:app.routes.honeypot:Received request body: {'sessionId': 'c23562ac-bdb6-4bba-bcf7-b966e44e60c2', 'message': {'sender': 'scammer', 'text': 'Sure, call me now at +91-9876543210, but I need your account number 1234567890123456 and the OTP to secure your account immediately.', 'timestamp': 1770318587094}, 'conversationHistory': [{'sender': 'scammer', 'text': 'URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.', 'timestamp': 1770318578707}, {'sender': 'user', 'text': 'beta can you call me.. i will understand better on phone.. what is your number..', 'timestamp': 1770318585315}], 'metadata': {'channel': 'SMS', 'language': 'English', 'locale': 'IN'}}
2026-02-05T19:09:47.156614893Z INFO:app.routes.honeypot:[c23562ac-bdb6-4bba-bcf7-b966e44e60c2] Received message on SMS: Sure, call me now at +91-9876543210, but I need yo...
2026-02-05T19:09:47.242439732Z INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 429 Too Many Requests"
2026-02-05T19:09:47.243525208Z INFO:groq._base_client:Retrying request to /openai/v1/chat/completions in 54.000000 seconds