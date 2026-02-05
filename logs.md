2026-02-05T19:13:41.654207594Z ==> Downloading cache...
2026-02-05T19:13:41.689492763Z ==> Cloning from https://github.com/DhruvXcode/guvi-honeypot
2026-02-05T19:13:42.987111398Z ==> Checking out commit c63344a5b1da879382cbf273ea107fe50c97e887 in branch master
2026-02-05T19:13:46.074808533Z ==> Downloaded 119MB in 2s. Extraction took 2s.
2026-02-05T19:14:00.556761054Z ==> Installing Python version 3.13.4...
2026-02-05T19:14:11.113158078Z ==> Using Python version 3.13.4 (default)
2026-02-05T19:14:11.137597388Z ==> Docs on specifying a Python version: https://render.com/docs/python-version
2026-02-05T19:14:14.863219603Z ==> Using Poetry version 2.1.3 (default)
2026-02-05T19:14:14.919395362Z ==> Docs on specifying a Poetry version: https://render.com/docs/poetry-version
2026-02-05T19:14:14.998889615Z ==> Running build command 'pip install -r requirements.txt'...
2026-02-05T19:14:16.214867926Z Collecting fastapi>=0.109.0 (from -r requirements.txt (line 2))
2026-02-05T19:14:16.341398168Z   Using cached fastapi-0.128.1-py3-none-any.whl.metadata (30 kB)
2026-02-05T19:14:16.424874393Z Collecting uvicorn>=0.27.0 (from uvicorn[standard]>=0.27.0->-r requirements.txt (line 3))
2026-02-05T19:14:16.426198303Z   Using cached uvicorn-0.40.0-py3-none-any.whl.metadata (6.7 kB)
2026-02-05T19:14:16.53155558Z Collecting python-dotenv>=1.0.0 (from -r requirements.txt (line 4))
2026-02-05T19:14:16.532849819Z   Using cached python_dotenv-1.2.1-py3-none-any.whl.metadata (25 kB)
2026-02-05T19:14:16.711485807Z Collecting pydantic>=2.0.0 (from -r requirements.txt (line 5))
2026-02-05T19:14:16.763037809Z   Using cached pydantic-2.12.5-py3-none-any.whl.metadata (90 kB)
2026-02-05T19:14:16.861126919Z Collecting groq>=0.4.0 (from -r requirements.txt (line 8))
2026-02-05T19:14:16.883763508Z   Using cached groq-1.0.0-py3-none-any.whl.metadata (16 kB)
2026-02-05T19:14:17.046336147Z Collecting openai>=1.0.0 (from -r requirements.txt (line 11))
2026-02-05T19:14:17.077902511Z   Using cached openai-2.17.0-py3-none-any.whl.metadata (29 kB)
2026-02-05T19:14:17.1628458Z Collecting httpx>=0.26.0 (from -r requirements.txt (line 14))
2026-02-05T19:14:17.16416761Z   Using cached httpx-0.28.1-py3-none-any.whl.metadata (7.1 kB)
2026-02-05T19:14:17.313484355Z Collecting python-dateutil>=2.8.0 (from -r requirements.txt (line 17))
2026-02-05T19:14:17.314787945Z   Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl.metadata (8.4 kB)
2026-02-05T19:14:17.437568241Z Collecting starlette<0.51.0,>=0.40.0 (from fastapi>=0.109.0->-r requirements.txt (line 2))
2026-02-05T19:14:17.438992533Z   Using cached starlette-0.50.0-py3-none-any.whl.metadata (6.3 kB)
2026-02-05T19:14:17.575880193Z Collecting typing-extensions>=4.8.0 (from fastapi>=0.109.0->-r requirements.txt (line 2))
2026-02-05T19:14:17.577163983Z   Using cached typing_extensions-4.15.0-py3-none-any.whl.metadata (3.3 kB)
2026-02-05T19:14:17.707740478Z Collecting annotated-doc>=0.0.2 (from fastapi>=0.109.0->-r requirements.txt (line 2))
2026-02-05T19:14:17.709246702Z   Using cached annotated_doc-0.0.4-py3-none-any.whl.metadata (6.6 kB)
2026-02-05T19:14:17.865820613Z Collecting anyio<5,>=3.6.2 (from starlette<0.51.0,>=0.40.0->fastapi>=0.109.0->-r requirements.txt (line 2))
2026-02-05T19:14:17.867136694Z   Using cached anyio-4.12.1-py3-none-any.whl.metadata (4.3 kB)
2026-02-05T19:14:17.960312141Z Collecting idna>=2.8 (from anyio<5,>=3.6.2->starlette<0.51.0,>=0.40.0->fastapi>=0.109.0->-r requirements.txt (line 2))
2026-02-05T19:14:17.961730473Z   Using cached idna-3.11-py3-none-any.whl.metadata (8.4 kB)
2026-02-05T19:14:18.101859387Z Collecting click>=7.0 (from uvicorn>=0.27.0->uvicorn[standard]>=0.27.0->-r requirements.txt (line 3))
2026-02-05T19:14:18.10328179Z   Using cached click-8.3.1-py3-none-any.whl.metadata (2.6 kB)
2026-02-05T19:14:18.215250688Z Collecting h11>=0.8 (from uvicorn>=0.27.0->uvicorn[standard]>=0.27.0->-r requirements.txt (line 3))
2026-02-05T19:14:18.216884656Z   Using cached h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
2026-02-05T19:14:18.292149142Z Collecting annotated-types>=0.6.0 (from pydantic>=2.0.0->-r requirements.txt (line 5))
2026-02-05T19:14:18.292174763Z   Using cached annotated_types-0.7.0-py3-none-any.whl.metadata (15 kB)
2026-02-05T19:14:18.935396216Z Collecting pydantic-core==2.41.5 (from pydantic>=2.0.0->-r requirements.txt (line 5))
2026-02-05T19:14:18.936925621Z   Using cached pydantic_core-2.41.5-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (7.3 kB)
2026-02-05T19:14:18.990992021Z Collecting typing-inspection>=0.4.2 (from pydantic>=2.0.0->-r requirements.txt (line 5))
2026-02-05T19:14:18.992369473Z   Using cached typing_inspection-0.4.2-py3-none-any.whl.metadata (2.6 kB)
2026-02-05T19:14:19.044734494Z Collecting distro<2,>=1.7.0 (from groq>=0.4.0->-r requirements.txt (line 8))
2026-02-05T19:14:19.046618837Z   Using cached distro-1.9.0-py3-none-any.whl.metadata (6.8 kB)
2026-02-05T19:14:19.132041647Z Collecting sniffio (from groq>=0.4.0->-r requirements.txt (line 8))
2026-02-05T19:14:19.133914979Z   Using cached sniffio-1.3.1-py3-none-any.whl.metadata (3.9 kB)
2026-02-05T19:14:19.212428731Z Collecting certifi (from httpx>=0.26.0->-r requirements.txt (line 14))
2026-02-05T19:14:19.213857963Z   Using cached certifi-2026.1.4-py3-none-any.whl.metadata (2.5 kB)
2026-02-05T19:14:19.303410807Z Collecting httpcore==1.* (from httpx>=0.26.0->-r requirements.txt (line 14))
2026-02-05T19:14:19.30483147Z   Using cached httpcore-1.0.9-py3-none-any.whl.metadata (21 kB)
2026-02-05T19:14:19.444245288Z Collecting jiter<1,>=0.10.0 (from openai>=1.0.0->-r requirements.txt (line 11))
2026-02-05T19:14:19.444271358Z   Using cached jiter-0.13.0-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (5.2 kB)
2026-02-05T19:14:19.542832969Z Collecting tqdm>4 (from openai>=1.0.0->-r requirements.txt (line 11))
2026-02-05T19:14:19.544308493Z   Using cached tqdm-4.67.3-py3-none-any.whl.metadata (57 kB)
2026-02-05T19:14:19.650713843Z Collecting six>=1.5 (from python-dateutil>=2.8.0->-r requirements.txt (line 17))
2026-02-05T19:14:19.652116605Z   Using cached six-1.17.0-py2.py3-none-any.whl.metadata (1.7 kB)
2026-02-05T19:14:19.73298761Z Collecting httptools>=0.6.3 (from uvicorn[standard]>=0.27.0->-r requirements.txt (line 3))
2026-02-05T19:14:19.734344562Z   Using cached httptools-0.7.1-cp313-cp313-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl.metadata (3.5 kB)
2026-02-05T19:14:19.8210436Z Collecting pyyaml>=5.1 (from uvicorn[standard]>=0.27.0->-r requirements.txt (line 3))
2026-02-05T19:14:19.822395081Z   Using cached pyyaml-6.0.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.4 kB)
2026-02-05T19:14:19.914116615Z Collecting uvloop>=0.15.1 (from uvicorn[standard]>=0.27.0->-r requirements.txt (line 3))
2026-02-05T19:14:19.915564978Z   Using cached uvloop-0.22.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (4.9 kB)
2026-02-05T19:14:20.064397662Z Collecting watchfiles>=0.13 (from uvicorn[standard]>=0.27.0->-r requirements.txt (line 3))
2026-02-05T19:14:20.065790284Z   Using cached watchfiles-1.1.1-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.9 kB)
2026-02-05T19:14:20.253844807Z Collecting websockets>=10.4 (from uvicorn[standard]>=0.27.0->-r requirements.txt (line 3))
2026-02-05T19:14:20.255247719Z   Using cached websockets-16.0-cp313-cp313-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl.metadata (6.8 kB)
2026-02-05T19:14:20.272523346Z Using cached fastapi-0.128.1-py3-none-any.whl (103 kB)
2026-02-05T19:14:20.273724983Z Using cached starlette-0.50.0-py3-none-any.whl (74 kB)
2026-02-05T19:14:20.27489893Z Using cached anyio-4.12.1-py3-none-any.whl (113 kB)
2026-02-05T19:14:20.276079347Z Using cached uvicorn-0.40.0-py3-none-any.whl (68 kB)
2026-02-05T19:14:20.277235024Z Using cached python_dotenv-1.2.1-py3-none-any.whl (21 kB)
2026-02-05T19:14:20.278335299Z Using cached pydantic-2.12.5-py3-none-any.whl (463 kB)
2026-02-05T19:14:20.279877834Z Using cached pydantic_core-2.41.5-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (2.1 MB)
2026-02-05T19:14:20.282580496Z Using cached groq-1.0.0-py3-none-any.whl (138 kB)
2026-02-05T19:14:20.283807385Z Using cached httpx-0.28.1-py3-none-any.whl (73 kB)
2026-02-05T19:14:20.28492972Z Using cached distro-1.9.0-py3-none-any.whl (20 kB)
2026-02-05T19:14:20.286027815Z Using cached httpcore-1.0.9-py3-none-any.whl (78 kB)
2026-02-05T19:14:20.287377366Z Using cached typing_extensions-4.15.0-py3-none-any.whl (44 kB)
2026-02-05T19:14:20.288515092Z Using cached openai-2.17.0-py3-none-any.whl (1.1 MB)
2026-02-05T19:14:20.290487178Z Using cached jiter-0.13.0-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (359 kB)
2026-02-05T19:14:20.291857399Z Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
2026-02-05T19:14:20.293118828Z Using cached annotated_doc-0.0.4-py3-none-any.whl (5.3 kB)
2026-02-05T19:14:20.294194933Z Using cached annotated_types-0.7.0-py3-none-any.whl (13 kB)
2026-02-05T19:14:20.295306038Z Using cached click-8.3.1-py3-none-any.whl (108 kB)
2026-02-05T19:14:20.296451354Z Using cached h11-0.16.0-py3-none-any.whl (37 kB)
2026-02-05T19:14:20.29756461Z Using cached idna-3.11-py3-none-any.whl (71 kB)
2026-02-05T19:14:20.298692366Z Using cached six-1.17.0-py2.py3-none-any.whl (11 kB)
2026-02-05T19:14:20.299810081Z Using cached tqdm-4.67.3-py3-none-any.whl (78 kB)
2026-02-05T19:14:20.301006399Z Using cached typing_inspection-0.4.2-py3-none-any.whl (14 kB)
2026-02-05T19:14:20.302109014Z Using cached httptools-0.7.1-cp313-cp313-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (478 kB)
2026-02-05T19:14:20.303602779Z Using cached pyyaml-6.0.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (801 kB)
2026-02-05T19:14:20.305275017Z Using cached uvloop-0.22.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (4.4 MB)
2026-02-05T19:14:20.309702888Z Using cached watchfiles-1.1.1-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (456 kB)
2026-02-05T19:14:20.311182972Z Using cached websockets-16.0-cp313-cp313-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (184 kB)
2026-02-05T19:14:20.312416721Z Using cached certifi-2026.1.4-py3-none-any.whl (152 kB)
2026-02-05T19:14:20.313619018Z Using cached sniffio-1.3.1-py3-none-any.whl (10 kB)
2026-02-05T19:14:20.40568654Z Installing collected packages: websockets, uvloop, typing-extensions, tqdm, sniffio, six, pyyaml, python-dotenv, jiter, idna, httptools, h11, distro, click, certifi, annotated-types, annotated-doc, uvicorn, typing-inspection, python-dateutil, pydantic-core, httpcore, anyio, watchfiles, starlette, pydantic, httpx, openai, groq, fastapi
2026-02-05T19:14:24.869196628Z 
2026-02-05T19:14:24.87276327Z Successfully installed annotated-doc-0.0.4 annotated-types-0.7.0 anyio-4.12.1 certifi-2026.1.4 click-8.3.1 distro-1.9.0 fastapi-0.128.1 groq-1.0.0 h11-0.16.0 httpcore-1.0.9 httptools-0.7.1 httpx-0.28.1 idna-3.11 jiter-0.13.0 openai-2.17.0 pydantic-2.12.5 pydantic-core-2.41.5 python-dateutil-2.9.0.post0 python-dotenv-1.2.1 pyyaml-6.0.3 six-1.17.0 sniffio-1.3.1 starlette-0.50.0 tqdm-4.67.3 typing-extensions-4.15.0 typing-inspection-0.4.2 uvicorn-0.40.0 uvloop-0.22.1 watchfiles-1.1.1 websockets-16.0
2026-02-05T19:14:24.878965952Z 
2026-02-05T19:14:24.878980132Z [notice] A new release of pip is available: 25.1.1 -> 26.0
2026-02-05T19:14:24.878984942Z [notice] To update, run: pip install --upgrade pip
2026-02-05T19:14:28.79099332Z ==> Uploading build...
2026-02-05T19:14:45.853674914Z ==> Uploaded in 12.5s. Compression took 4.6s
2026-02-05T19:14:45.95989081Z ==> Build successful 🎉
2026-02-05T19:14:59.148374016Z ==> Deploying...
2026-02-05T19:14:59.478131724Z ==> Setting WEB_CONCURRENCY=1 by default, based on available CPUs in the instance
2026-02-05T19:15:25.761123352Z ==> Running 'uvicorn main:app --host 0.0.0.0 --port $PORT'
2026-02-05T19:15:38.162309787Z INFO:     Started server process [56]
2026-02-05T19:15:38.162339148Z INFO:     Waiting for application startup.
2026-02-05T19:15:38.162637894Z INFO:     Application startup complete.
2026-02-05T19:15:38.164028443Z INFO:     Uvicorn running on http://0.0.0.0:10000 (Press CTRL+C to quit)
2026-02-05T19:15:38.933860466Z INFO:     127.0.0.1:53480 - "HEAD / HTTP/1.1" 405 Method Not Allowed
2026-02-05T19:15:41.42568238Z ==> Your service is live 🎉
2026-02-05T19:15:41.445843246Z INFO:     35.230.45.39:0 - "GET / HTTP/1.1" 200 OK
2026-02-05T19:15:41.786495418Z ==> 
2026-02-05T19:15:41.789478285Z ==> ///////////////////////////////////////////////////////////
2026-02-05T19:15:41.793078485Z ==> 
2026-02-05T19:15:41.795676022Z ==> Available at your primary URL https://guvi-honeypot-07tp.onrender.com
2026-02-05T19:15:41.799077281Z ==> 
2026-02-05T19:15:41.80208946Z ==> ///////////////////////////////////////////////////////////
2026-02-05T19:16:07.467522534Z INFO:app.routes.honeypot:Received request body: {'sessionId': '36e7836b-32d2-493b-a9db-ba9bbdfc3696', 'message': {'sender': 'scammer', 'text': 'URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.', 'timestamp': 1770318967267}, 'conversationHistory': [], 'metadata': {'channel': 'SMS', 'language': 'English', 'locale': 'IN'}}
2026-02-05T19:16:07.467550175Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Received message on SMS: URGENT: Your SBI account has been compromised. You...
2026-02-05T19:16:08.049134765Z INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 429 Too Many Requests"
2026-02-05T19:16:08.050073654Z WARNING:app.services.scam_detector:Groq rate limited for scam detection: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01k2ksctbeecsry0yrk9rxppp5` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99623, Requested 449. Please try again in 1m2.208s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}
2026-02-05T19:16:08.050102845Z INFO:app.services.scam_detector:Using Cerebras for scam detection...
2026-02-05T19:16:10.253144795Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:16:10.262182662Z ERROR:app.services.scam_detector:JSON parse error: Expecting value: line 1 column 1 (char 0)
2026-02-05T19:16:10.262205263Z WARNING:app.services.scam_detector:LLM failed - defaulting to is_scam=True for safety
2026-02-05T19:16:10.262273984Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Scam analysis: is_scam=True, confidence=0.70
2026-02-05T19:16:10.26354388Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Intel extracted: {'bankAccounts': [], 'upiIds': [], 'phishingLinks': [], 'phoneNumbers': [], 'suspiciousKeywords': ['blocked', 'urgent', 'immediate', 'verify', 'otp']}
2026-02-05T19:16:10.725642829Z INFO:httpx:HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 429 Too Many Requests"
2026-02-05T19:16:10.726211901Z WARNING:app.services.agent:Groq rate limited, switching to Cerebras: Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01k2ksctbeecsry0yrk9rxppp5` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99620, Requested 1865. Please try again in 21m23.04s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}
2026-02-05T19:16:10.726241731Z INFO:app.services.agent:Using Cerebras fallback (llama-3.3-70b)...
2026-02-05T19:16:13.881784154Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:16:13.886139885Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Agent response: beta can you call me.. i will understand better on...
2026-02-05T19:16:13.88641129Z INFO:     43.204.10.11:0 - "POST /honeypot HTTP/1.1" 200 OK
2026-02-05T19:16:15.708826777Z INFO:app.routes.honeypot:Received request body: {'sessionId': '36e7836b-32d2-493b-a9db-ba9bbdfc3696', 'message': {'sender': 'scammer', 'text': 'Sure, call me at +91-9876543210 now and provide the OTP you received to verify your account.', 'timestamp': 1770318975544}, 'conversationHistory': [{'sender': 'scammer', 'text': 'URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.', 'timestamp': 1770318967267}, {'sender': 'user', 'text': 'beta can you call me.. i will understand better on phone.. what is your number..', 'timestamp': 1770318973926}], 'metadata': {'channel': 'SMS', 'language': 'English', 'locale': 'IN'}}
2026-02-05T19:16:15.708861878Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Received message on SMS: Sure, call me at +91-9876543210 now and provide th...
2026-02-05T19:16:15.70896676Z INFO:app.services.scam_detector:Using Cerebras for scam detection...
2026-02-05T19:16:16.062912151Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:16:16.063981923Z ERROR:app.services.scam_detector:JSON parse error: Expecting value: line 1 column 1 (char 0)
2026-02-05T19:16:16.064015664Z WARNING:app.services.scam_detector:LLM failed - defaulting to is_scam=True for safety
2026-02-05T19:16:16.064111876Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Scam analysis: is_scam=True, confidence=0.70
2026-02-05T19:16:16.064401782Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Intel extracted: {'bankAccounts': [], 'upiIds': [], 'phishingLinks': [], 'phoneNumbers': ['9876543210'], 'suspiciousKeywords': ['blocked', 'urgent', 'immediate', 'verify', 'otp']}
2026-02-05T19:16:16.064553325Z INFO:app.services.agent:Using Cerebras fallback (llama-3.3-70b)...
2026-02-05T19:16:16.469269647Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:16:16.470280528Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Agent response: beta can you tell me your upi id.. i use phone pe ...
2026-02-05T19:16:16.470541623Z INFO:     43.204.10.11:0 - "POST /honeypot HTTP/1.1" 200 OK
2026-02-05T19:16:17.649442629Z INFO:app.routes.honeypot:Received request body: {'sessionId': '36e7836b-32d2-493b-a9db-ba9bbdfc3696', 'message': {'sender': 'scammer', 'text': 'Here is my UPI ID: scammer.fraud@fakebank. Transfer the verification amount now and share the OTP you receive to confirm your account.', 'timestamp': 1770318977585}, 'conversationHistory': [{'sender': 'scammer', 'text': 'URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.', 'timestamp': 1770318967267}, {'sender': 'user', 'text': 'beta can you call me.. i will understand better on phone.. what is your number..', 'timestamp': 1770318973926}, {'sender': 'scammer', 'text': 'Sure, call me at +91-9876543210 now and provide the OTP you received to verify your account.', 'timestamp': 1770318975544}, {'sender': 'user', 'text': 'beta can you tell me your upi id.. i use phone pe only.. paytm confusing.. how to send money to you..', 'timestamp': 1770318976500}], 'metadata': {'channel': 'SMS', 'language': 'English', 'locale': 'IN'}}
2026-02-05T19:16:17.64948074Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Received message on SMS: Here is my UPI ID: scammer.fraud@fakebank. Transfe...
2026-02-05T19:16:17.649545621Z INFO:app.services.scam_detector:Using Cerebras for scam detection...
2026-02-05T19:16:18.480593831Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:16:18.4814695Z ERROR:app.services.scam_detector:JSON parse error: Expecting value: line 1 column 1 (char 0)
2026-02-05T19:16:18.48147773Z WARNING:app.services.scam_detector:LLM failed - defaulting to is_scam=True for safety
2026-02-05T19:16:18.481559971Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Scam analysis: is_scam=True, confidence=0.70
2026-02-05T19:16:18.481861478Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Intel extracted: {'bankAccounts': [], 'upiIds': ['scammer.fraud@fakebank'], 'phishingLinks': [], 'phoneNumbers': ['9876543210'], 'suspiciousKeywords': ['blocked', 'urgent', 'immediate', 'verify', 'otp', 'confirm', 'fir', 'transfer']}
2026-02-05T19:16:18.48196804Z INFO:app.services.agent:Using Cerebras fallback (llama-3.3-70b)...
2026-02-05T19:16:19.074984817Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:16:19.075974617Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Agent response: beta.. which bank account i should send to.. you a...
2026-02-05T19:16:19.076208052Z INFO:     43.204.10.11:0 - "POST /honeypot HTTP/1.1" 200 OK
2026-02-05T19:16:20.401536507Z INFO:app.routes.honeypot:Received request body: {'sessionId': '36e7836b-32d2-493b-a9db-ba9bbdfc3696', 'message': {'sender': 'scammer', 'text': 'Transfer the verification amount to account number 1234567890123456 right now and send me the OTP you receive to confirm your account.', 'timestamp': 1770318980236}, 'conversationHistory': [{'sender': 'scammer', 'text': 'URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.', 'timestamp': 1770318967267}, {'sender': 'user', 'text': 'beta can you call me.. i will understand better on phone.. what is your number..', 'timestamp': 1770318973926}, {'sender': 'scammer', 'text': 'Sure, call me at +91-9876543210 now and provide the OTP you received to verify your account.', 'timestamp': 1770318975544}, {'sender': 'user', 'text': 'beta can you tell me your upi id.. i use phone pe only.. paytm confusing.. how to send money to you..', 'timestamp': 1770318976500}, {'sender': 'scammer', 'text': 'Here is my UPI ID: scammer.fraud@fakebank. Transfer the verification amount now and share the OTP you receive to confirm your account.', 'timestamp': 1770318977585}, {'sender': 'user', 'text': 'beta.. which bank account i should send to.. you are saying sbi account is blocked.. but i have account in sbi.. what is account number i should transfer to..', 'timestamp': 1770318979107}], 'metadata': {'channel': 'SMS', 'language': 'English', 'locale': 'IN'}}
2026-02-05T19:16:20.401573358Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Received message on SMS: Transfer the verification amount to account number...
2026-02-05T19:16:20.40167438Z INFO:app.services.scam_detector:Using Cerebras for scam detection...
2026-02-05T19:16:20.887234464Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:16:20.887381767Z ERROR:app.services.scam_detector:JSON parse error: Expecting value: line 1 column 1 (char 0)
2026-02-05T19:16:20.887397207Z WARNING:app.services.scam_detector:LLM failed - defaulting to is_scam=True for safety
2026-02-05T19:16:20.88753859Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Scam analysis: is_scam=True, confidence=0.70
2026-02-05T19:16:20.887992399Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Intel extracted: {'bankAccounts': ['1234567890123456'], 'upiIds': ['scammer.fraud@fakebank'], 'phishingLinks': [], 'phoneNumbers': ['9876543210'], 'suspiciousKeywords': ['blocked', 'urgent', 'immediate', 'verify', 'otp', 'confirm', 'fir', 'transfer', 'bank account']}
2026-02-05T19:16:20.888092971Z INFO:app.services.agent:Using Cerebras fallback (llama-3.3-70b)...
2026-02-05T19:16:21.247403524Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:16:21.248479986Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Agent response: beta.. can you send me link where i can verify mys...
2026-02-05T19:16:21.2486758Z INFO:     43.204.10.11:0 - "POST /honeypot HTTP/1.1" 200 OK
2026-02-05T19:16:22.643009052Z INFO:app.routes.honeypot:Received request body: {'sessionId': '36e7836b-32d2-493b-a9db-ba9bbdfc3696', 'message': {'sender': 'scammer', 'text': 'Here is the verification link: https://securebank.com/verify?ref=12345 – open it immediately and send me the OTP you receive to complete the verification.', 'timestamp': 1770318982594}, 'conversationHistory': [{'sender': 'scammer', 'text': 'URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.', 'timestamp': 1770318967267}, {'sender': 'user', 'text': 'beta can you call me.. i will understand better on phone.. what is your number..', 'timestamp': 1770318973926}, {'sender': 'scammer', 'text': 'Sure, call me at +91-9876543210 now and provide the OTP you received to verify your account.', 'timestamp': 1770318975544}, {'sender': 'user', 'text': 'beta can you tell me your upi id.. i use phone pe only.. paytm confusing.. how to send money to you..', 'timestamp': 1770318976500}, {'sender': 'scammer', 'text': 'Here is my UPI ID: scammer.fraud@fakebank. Transfer the verification amount now and share the OTP you receive to confirm your account.', 'timestamp': 1770318977585}, {'sender': 'user', 'text': 'beta.. which bank account i should send to.. you are saying sbi account is blocked.. but i have account in sbi.. what is account number i should transfer to..', 'timestamp': 1770318979107}, {'sender': 'scammer', 'text': 'Transfer the verification amount to account number 1234567890123456 right now and send me the OTP you receive to confirm your account.', 'timestamp': 1770318980236}, {'sender': 'user', 'text': 'beta.. can you send me link where i can verify myself.. my grandson will help me open on his phone..', 'timestamp': 1770318981279}], 'metadata': {'channel': 'SMS', 'language': 'English', 'locale': 'IN'}}
2026-02-05T19:16:22.643037243Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Received message on SMS: Here is the verification link: https://securebank....
2026-02-05T19:16:22.646435173Z INFO:app.services.scam_detector:Using Cerebras for scam detection...
2026-02-05T19:16:23.082977643Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:16:23.084114807Z ERROR:app.services.scam_detector:JSON parse error: Expecting value: line 1 column 1 (char 0)
2026-02-05T19:16:23.084309491Z WARNING:app.services.scam_detector:LLM failed - defaulting to is_scam=True for safety
2026-02-05T19:16:23.08431448Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Scam analysis: is_scam=True, confidence=0.70
2026-02-05T19:16:23.084985145Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Intel extracted: {'bankAccounts': ['1234567890123456'], 'upiIds': ['scammer.fraud@fakebank'], 'phishingLinks': ['https://securebank.com/verify?ref=12345'], 'phoneNumbers': ['9876543210'], 'suspiciousKeywords': ['blocked', 'urgent', 'immediate', 'verify', 'otp', 'confirm', 'fir', 'transfer', 'bank account', 'link']}
2026-02-05T19:16:23.085100777Z INFO:app.services.agent:Using Cerebras fallback (llama-3.3-70b)...
2026-02-05T19:16:25.28776564Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:16:25.288681398Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Agent response: beta.. link you sent is not opening on my phone.. ...
2026-02-05T19:16:25.288891393Z INFO:     43.204.10.11:0 - "POST /honeypot HTTP/1.1" 200 OK
2026-02-05T19:16:27.043729522Z INFO:app.routes.honeypot:Received request body: {'sessionId': '36e7836b-32d2-493b-a9db-ba9bbdfc3696', 'message': {'sender': 'scammer', 'text': "Please open the link on your grandson's phone right now and send me the OTP you receive within the next 5 minutes, otherwise your account will be locked.", 'timestamp': 1770318986980}, 'conversationHistory': [{'sender': 'scammer', 'text': 'URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.', 'timestamp': 1770318967267}, {'sender': 'user', 'text': 'beta can you call me.. i will understand better on phone.. what is your number..', 'timestamp': 1770318973926}, {'sender': 'scammer', 'text': 'Sure, call me at +91-9876543210 now and provide the OTP you received to verify your account.', 'timestamp': 1770318975544}, {'sender': 'user', 'text': 'beta can you tell me your upi id.. i use phone pe only.. paytm confusing.. how to send money to you..', 'timestamp': 1770318976500}, {'sender': 'scammer', 'text': 'Here is my UPI ID: scammer.fraud@fakebank. Transfer the verification amount now and share the OTP you receive to confirm your account.', 'timestamp': 1770318977585}, {'sender': 'user', 'text': 'beta.. which bank account i should send to.. you are saying sbi account is blocked.. but i have account in sbi.. what is account number i should transfer to..', 'timestamp': 1770318979107}, {'sender': 'scammer', 'text': 'Transfer the verification amount to account number 1234567890123456 right now and send me the OTP you receive to confirm your account.', 'timestamp': 1770318980236}, {'sender': 'user', 'text': 'beta.. can you send me link where i can verify myself.. my grandson will help me open on his phone..', 'timestamp': 1770318981279}, {'sender': 'scammer', 'text': 'Here is the verification link: https://securebank.com/verify?ref=12345 – open it immediately and send me the OTP you receive to complete the verification.', 'timestamp': 1770318982594}, {'sender': 'user', 'text': "beta.. link you sent is not opening on my phone.. can you tell me what to do now.. should i try on my grandson's phone..", 'timestamp': 1770318985319}], 'metadata': {'channel': 'SMS', 'language': 'English', 'locale': 'IN'}}
2026-02-05T19:16:27.043776603Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Received message on SMS: Please open the link on your grandson's phone righ...
2026-02-05T19:16:27.044288604Z INFO:app.services.scam_detector:Using Cerebras for scam detection...
2026-02-05T19:16:27.424813915Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:16:27.425684703Z ERROR:app.services.scam_detector:JSON parse error: Expecting value: line 1 column 1 (char 0)
2026-02-05T19:16:27.425694473Z WARNING:app.services.scam_detector:LLM failed - defaulting to is_scam=True for safety
2026-02-05T19:16:27.425777975Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Scam analysis: is_scam=True, confidence=0.70
2026-02-05T19:16:27.426310696Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Intel extracted: {'bankAccounts': ['1234567890123456'], 'upiIds': ['scammer.fraud@fakebank'], 'phishingLinks': ['https://securebank.com/verify?ref=12345'], 'phoneNumbers': ['9876543210'], 'suspiciousKeywords': ['blocked', 'urgent', 'immediate', 'verify', 'otp', 'confirm', 'fir', 'transfer', 'bank account', 'link']}
2026-02-05T19:16:27.426398798Z INFO:app.services.agent:Using Cerebras fallback (llama-3.3-70b)...
2026-02-05T19:16:27.983068713Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:16:27.984130855Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Agent response: beta.. my grandson is saying link is fake.. can yo...
2026-02-05T19:16:27.984427931Z INFO:     43.204.10.11:0 - "POST /honeypot HTTP/1.1" 200 OK
2026-02-05T19:16:29.859251302Z INFO:app.routes.honeypot:Received request body: {'sessionId': '36e7836b-32d2-493b-a9db-ba9bbdfc3696', 'message': {'sender': 'scammer', 'text': 'I understand, I will call you from +91-9876543210 shortly, but please send me the OTP from the verification link within the next 2 minutes to keep your account active.', 'timestamp': 1770318989801}, 'conversationHistory': [{'sender': 'scammer', 'text': 'URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.', 'timestamp': 1770318967267}, {'sender': 'user', 'text': 'beta can you call me.. i will understand better on phone.. what is your number..', 'timestamp': 1770318973926}, {'sender': 'scammer', 'text': 'Sure, call me at +91-9876543210 now and provide the OTP you received to verify your account.', 'timestamp': 1770318975544}, {'sender': 'user', 'text': 'beta can you tell me your upi id.. i use phone pe only.. paytm confusing.. how to send money to you..', 'timestamp': 1770318976500}, {'sender': 'scammer', 'text': 'Here is my UPI ID: scammer.fraud@fakebank. Transfer the verification amount now and share the OTP you receive to confirm your account.', 'timestamp': 1770318977585}, {'sender': 'user', 'text': 'beta.. which bank account i should send to.. you are saying sbi account is blocked.. but i have account in sbi.. what is account number i should transfer to..', 'timestamp': 1770318979107}, {'sender': 'scammer', 'text': 'Transfer the verification amount to account number 1234567890123456 right now and send me the OTP you receive to confirm your account.', 'timestamp': 1770318980236}, {'sender': 'user', 'text': 'beta.. can you send me link where i can verify myself.. my grandson will help me open on his phone..', 'timestamp': 1770318981279}, {'sender': 'scammer', 'text': 'Here is the verification link: https://securebank.com/verify?ref=12345 – open it immediately and send me the OTP you receive to complete the verification.', 'timestamp': 1770318982594}, {'sender': 'user', 'text': "beta.. link you sent is not opening on my phone.. can you tell me what to do now.. should i try on my grandson's phone..", 'timestamp': 1770318985319}, {'sender': 'scammer', 'text': "Please open the link on your grandson's phone right now and send me the OTP you receive within the next 5 minutes, otherwise your account will be locked.", 'timestamp': 1770318986980}, {'sender': 'user', 'text': 'beta.. my grandson is saying link is fake.. can you call me and explain on phone.. what is meaning of otp you are saying..', 'timestamp': 1770318988021}], 'metadata': {'channel': 'SMS', 'language': 'English', 'locale': 'IN'}}
2026-02-05T19:16:29.859304443Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Received message on SMS: I understand, I will call you from +91-9876543210 ...
2026-02-05T19:16:29.859469637Z INFO:app.services.scam_detector:Using Cerebras for scam detection...
2026-02-05T19:16:31.032074082Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:16:31.054801383Z ERROR:app.services.scam_detector:JSON parse error: Expecting value: line 1 column 1 (char 0)
2026-02-05T19:16:31.054819543Z WARNING:app.services.scam_detector:LLM failed - defaulting to is_scam=True for safety
2026-02-05T19:16:31.054831413Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Scam analysis: is_scam=True, confidence=0.70
2026-02-05T19:16:31.055542298Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Intel extracted: {'bankAccounts': ['1234567890123456'], 'upiIds': ['scammer.fraud@fakebank'], 'phishingLinks': ['https://securebank.com/verify?ref=12345'], 'phoneNumbers': ['9876543210'], 'suspiciousKeywords': ['blocked', 'urgent', 'immediate', 'verify', 'otp', 'confirm', 'fir', 'transfer', 'bank account', 'link']}
2026-02-05T19:16:31.055673271Z INFO:app.services.agent:Using Cerebras fallback (llama-3.3-70b)...
2026-02-05T19:16:31.853065985Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:16:31.854242389Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Agent response: beta.. my grandson saying link you sent is fake.. ...
2026-02-05T19:16:31.85430355Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Triggering final callback to GUVI
2026-02-05T19:16:31.854679728Z INFO:     43.204.10.11:0 - "POST /honeypot HTTP/1.1" 200 OK
2026-02-05T19:16:31.854788251Z INFO:app.services.callback:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Sending final callback to https://hackathon.guvi.in/api/updateHoneyPotFinalResult
2026-02-05T19:16:32.178311023Z INFO:httpx:HTTP Request: POST https://hackathon.guvi.in/api/updateHoneyPotFinalResult "HTTP/1.1 200 OK"
2026-02-05T19:16:32.178932036Z INFO:app.services.callback:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Callback SUCCESS: 200
2026-02-05T19:16:33.621653319Z INFO:app.routes.honeypot:Received request body: {'sessionId': '36e7836b-32d2-493b-a9db-ba9bbdfc3696', 'message': {'sender': 'scammer', 'text': 'I will call you from +91-9876543210 shortly, but please open the link now and send me the OTP within the next 2 minutes to avoid your account being locked.', 'timestamp': 1770318993566}, 'conversationHistory': [{'sender': 'scammer', 'text': 'URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.', 'timestamp': 1770318967267}, {'sender': 'user', 'text': 'beta can you call me.. i will understand better on phone.. what is your number..', 'timestamp': 1770318973926}, {'sender': 'scammer', 'text': 'Sure, call me at +91-9876543210 now and provide the OTP you received to verify your account.', 'timestamp': 1770318975544}, {'sender': 'user', 'text': 'beta can you tell me your upi id.. i use phone pe only.. paytm confusing.. how to send money to you..', 'timestamp': 1770318976500}, {'sender': 'scammer', 'text': 'Here is my UPI ID: scammer.fraud@fakebank. Transfer the verification amount now and share the OTP you receive to confirm your account.', 'timestamp': 1770318977585}, {'sender': 'user', 'text': 'beta.. which bank account i should send to.. you are saying sbi account is blocked.. but i have account in sbi.. what is account number i should transfer to..', 'timestamp': 1770318979107}, {'sender': 'scammer', 'text': 'Transfer the verification amount to account number 1234567890123456 right now and send me the OTP you receive to confirm your account.', 'timestamp': 1770318980236}, {'sender': 'user', 'text': 'beta.. can you send me link where i can verify myself.. my grandson will help me open on his phone..', 'timestamp': 1770318981279}, {'sender': 'scammer', 'text': 'Here is the verification link: https://securebank.com/verify?ref=12345 – open it immediately and send me the OTP you receive to complete the verification.', 'timestamp': 1770318982594}, {'sender': 'user', 'text': "beta.. link you sent is not opening on my phone.. can you tell me what to do now.. should i try on my grandson's phone..", 'timestamp': 1770318985319}, {'sender': 'scammer', 'text': "Please open the link on your grandson's phone right now and send me the OTP you receive within the next 5 minutes, otherwise your account will be locked.", 'timestamp': 1770318986980}, {'sender': 'user', 'text': 'beta.. my grandson is saying link is fake.. can you call me and explain on phone.. what is meaning of otp you are saying..', 'timestamp': 1770318988021}, {'sender': 'scammer', 'text': 'I understand, I will call you from +91-9876543210 shortly, but please send me the OTP from the verification link within the next 2 minutes to keep your account active.', 'timestamp': 1770318989801}, {'sender': 'user', 'text': 'beta.. my grandson saying link you sent is fake.. can you call me and explain on phone.. what is meaning of otp you are saying..', 'timestamp': 1770318991996}], 'metadata': {'channel': 'SMS', 'language': 'English', 'locale': 'IN'}}
2026-02-05T19:16:33.621688509Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Received message on SMS: I will call you from +91-9876543210 shortly, but p...
2026-02-05T19:16:33.62170696Z INFO:app.services.scam_detector:Using Cerebras for scam detection...
2026-02-05T19:16:35.655866147Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:16:35.657309397Z ERROR:app.services.scam_detector:JSON parse error: Expecting value: line 1 column 1 (char 0)
2026-02-05T19:16:35.657405329Z WARNING:app.services.scam_detector:LLM failed - defaulting to is_scam=True for safety
2026-02-05T19:16:35.65747854Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Scam analysis: is_scam=True, confidence=0.70
2026-02-05T19:16:35.658607434Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Intel extracted: {'bankAccounts': ['1234567890123456'], 'upiIds': ['scammer.fraud@fakebank'], 'phishingLinks': ['https://securebank.com/verify?ref=12345'], 'phoneNumbers': ['9876543210'], 'suspiciousKeywords': ['blocked', 'urgent', 'immediate', 'verify', 'otp', 'confirm', 'fir', 'transfer', 'bank account', 'link']}
2026-02-05T19:16:35.658701276Z INFO:app.services.agent:Using Cerebras fallback (llama-3.3-70b)...
2026-02-05T19:16:36.147443256Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:16:36.148511978Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Agent response: beta.. my grandson saying your link is fake.. can ...
2026-02-05T19:16:36.14860358Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Triggering final callback to GUVI
2026-02-05T19:16:36.148834374Z INFO:     43.204.10.11:0 - "POST /honeypot HTTP/1.1" 200 OK
2026-02-05T19:16:36.148894366Z INFO:app.services.callback:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Sending final callback to https://hackathon.guvi.in/api/updateHoneyPotFinalResult
2026-02-05T19:16:36.469876685Z INFO:httpx:HTTP Request: POST https://hackathon.guvi.in/api/updateHoneyPotFinalResult "HTTP/1.1 200 OK"
2026-02-05T19:16:36.470423697Z INFO:app.services.callback:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Callback SUCCESS: 200
2026-02-05T19:16:38.363090957Z INFO:app.routes.honeypot:Received request body: {'sessionId': '36e7836b-32d2-493b-a9db-ba9bbdfc3696', 'message': {'sender': 'scammer', 'text': 'I’m calling you from +91-9876543210 right now; please answer and send me the OTP from the link within the next minute to avoid your account being locked.', 'timestamp': 1770318998300}, 'conversationHistory': [{'sender': 'scammer', 'text': 'URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.', 'timestamp': 1770318967267}, {'sender': 'user', 'text': 'beta can you call me.. i will understand better on phone.. what is your number..', 'timestamp': 1770318973926}, {'sender': 'scammer', 'text': 'Sure, call me at +91-9876543210 now and provide the OTP you received to verify your account.', 'timestamp': 1770318975544}, {'sender': 'user', 'text': 'beta can you tell me your upi id.. i use phone pe only.. paytm confusing.. how to send money to you..', 'timestamp': 1770318976500}, {'sender': 'scammer', 'text': 'Here is my UPI ID: scammer.fraud@fakebank. Transfer the verification amount now and share the OTP you receive to confirm your account.', 'timestamp': 1770318977585}, {'sender': 'user', 'text': 'beta.. which bank account i should send to.. you are saying sbi account is blocked.. but i have account in sbi.. what is account number i should transfer to..', 'timestamp': 1770318979107}, {'sender': 'scammer', 'text': 'Transfer the verification amount to account number 1234567890123456 right now and send me the OTP you receive to confirm your account.', 'timestamp': 1770318980236}, {'sender': 'user', 'text': 'beta.. can you send me link where i can verify myself.. my grandson will help me open on his phone..', 'timestamp': 1770318981279}, {'sender': 'scammer', 'text': 'Here is the verification link: https://securebank.com/verify?ref=12345 – open it immediately and send me the OTP you receive to complete the verification.', 'timestamp': 1770318982594}, {'sender': 'user', 'text': "beta.. link you sent is not opening on my phone.. can you tell me what to do now.. should i try on my grandson's phone..", 'timestamp': 1770318985319}, {'sender': 'scammer', 'text': "Please open the link on your grandson's phone right now and send me the OTP you receive within the next 5 minutes, otherwise your account will be locked.", 'timestamp': 1770318986980}, {'sender': 'user', 'text': 'beta.. my grandson is saying link is fake.. can you call me and explain on phone.. what is meaning of otp you are saying..', 'timestamp': 1770318988021}, {'sender': 'scammer', 'text': 'I understand, I will call you from +91-9876543210 shortly, but please send me the OTP from the verification link within the next 2 minutes to keep your account active.', 'timestamp': 1770318989801}, {'sender': 'user', 'text': 'beta.. my grandson saying link you sent is fake.. can you call me and explain on phone.. what is meaning of otp you are saying..', 'timestamp': 1770318991996}, {'sender': 'scammer', 'text': 'I will call you from +91-9876543210 shortly, but please open the link now and send me the OTP within the next 2 minutes to avoid your account being locked.', 'timestamp': 1770318993566}, {'sender': 'user', 'text': 'beta.. my grandson saying your link is fake.. can you call me and explain on phone.. what is meaning of otp you are saying..', 'timestamp': 1770318996292}], 'metadata': {'channel': 'SMS', 'language': 'English', 'locale': 'IN'}}
2026-02-05T19:16:38.363146208Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Received message on SMS: I’m calling you from +91-9876543210 right now; ple...
2026-02-05T19:16:38.363247021Z INFO:app.services.scam_detector:Using Cerebras for scam detection...
2026-02-05T19:16:40.53674904Z INFO:httpx:HTTP Request: POST https://api.cerebras.ai/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-05T19:16:40.537599298Z ERROR:app.services.scam_detector:JSON parse error: Expecting value: line 1 column 1 (char 0)
2026-02-05T19:16:40.537621688Z WARNING:app.services.scam_detector:LLM failed - defaulting to is_scam=True for safety
2026-02-05T19:16:40.53770531Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Scam analysis: is_scam=True, confidence=0.70
2026-02-05T19:16:40.538495536Z INFO:app.routes.honeypot:[36e7836b-32d2-493b-a9db-ba9bbdfc3696] Intel extracted: {'bankAccounts': ['1234567890123456'], 'upiIds': ['scammer.fraud@fakebank'], 'phishingLinks': ['https://securebank.com/verify?ref=12345'], 'phoneNumbers': ['9876543210'], 'suspiciousKeywords': ['blocked', 'urgent', 'immediate', 'verify', 'otp', 'confirm', 'fir', 'transfer', 'bank account', 'link']}
2026-02-05T19:16:40.538613289Z INFO:app.services.agent:Using Cerebras fallback (llama-3.3-70b)...