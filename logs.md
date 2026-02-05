2026-02-05T18:33:51.385255838Z     ~~~^
2026-02-05T18:33:51.385258289Z         app,
2026-02-05T18:33:51.385260569Z         ^^^^
2026-02-05T18:33:51.385262909Z     ...<46 lines>...
2026-02-05T18:33:51.385265479Z         h11_max_incomplete_event_size=h11_max_incomplete_event_size,
2026-02-05T18:33:51.385268159Z         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-02-05T18:33:51.385270679Z     )
2026-02-05T18:33:51.385273089Z     ^
2026-02-05T18:33:51.385275729Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/uvicorn/main.py", line 594, in run
2026-02-05T18:33:51.385278189Z     server.run()
2026-02-05T18:33:51.385280629Z     ~~~~~~~~~~^^
2026-02-05T18:33:51.385283199Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/uvicorn/server.py", line 67, in run
2026-02-05T18:33:51.385286769Z     return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
2026-02-05T18:33:51.385289469Z   File "/opt/render/project/python/Python-3.13.4/lib/python3.13/asyncio/runners.py", line 195, in run
2026-02-05T18:33:51.385291769Z     return runner.run(main)
2026-02-05T18:33:51.38529409Z            ~~~~~~~~~~^^^^^^
2026-02-05T18:33:51.385296299Z   File "/opt/render/project/python/Python-3.13.4/lib/python3.13/asyncio/runners.py", line 118, in run
2026-02-05T18:33:51.38529869Z     return self._loop.run_until_complete(task)
2026-02-05T18:33:51.385300899Z            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
2026-02-05T18:33:51.38530326Z   File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
2026-02-05T18:33:51.38530565Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/uvicorn/server.py", line 71, in serve
2026-02-05T18:33:51.38530791Z     await self._serve(sockets)
2026-02-05T18:33:51.38531022Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/uvicorn/server.py", line 78, in _serve
2026-02-05T18:33:51.38531254Z     config.load()
2026-02-05T18:33:51.38531481Z     ~~~~~~~~~~~^^
2026-02-05T18:33:51.38531719Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/uvicorn/config.py", line 439, in load
2026-02-05T18:33:51.38531951Z     self.loaded_app = import_from_string(self.app)
2026-02-05T18:33:51.38533744Z                       ~~~~~~~~~~~~~~~~~~^^^^^^^^^^
2026-02-05T18:33:51.385348671Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/uvicorn/importer.py", line 22, in import_from_string
2026-02-05T18:33:51.385351331Z     raise exc from None
2026-02-05T18:33:51.385353931Z   File "/opt/render/project/src/.venv/lib/python3.13/site-packages/uvicorn/importer.py", line 19, in import_from_string
2026-02-05T18:33:51.385356521Z     module = importlib.import_module(module_str)
2026-02-05T18:33:51.385359211Z   File "/opt/render/project/python/Python-3.13.4/lib/python3.13/importlib/__init__.py", line 88, in import_module
2026-02-05T18:33:51.385366861Z     return _bootstrap._gcd_import(name[level:], package, level)
2026-02-05T18:33:51.385369631Z            ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-02-05T18:33:51.385372031Z   File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
2026-02-05T18:33:51.385374491Z   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
2026-02-05T18:33:51.385377061Z   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
2026-02-05T18:33:51.385379521Z   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
2026-02-05T18:33:51.385382232Z   File "<frozen importlib._bootstrap_external>", line 1026, in exec_module
2026-02-05T18:33:51.385384781Z   File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
2026-02-05T18:33:51.385387112Z   File "/opt/render/project/src/main.py", line 5, in <module>
2026-02-05T18:33:51.385389592Z     from app.routes import honeypot
2026-02-05T18:33:51.385392232Z   File "/opt/render/project/src/app/routes/__init__.py", line 2, in <module>
2026-02-05T18:33:51.385394842Z     from .honeypot import router
2026-02-05T18:33:51.385397452Z   File "/opt/render/project/src/app/routes/honeypot.py", line 10, in <module>
2026-02-05T18:33:51.385400272Z     from ..services.agent import AgentService
2026-02-05T18:33:51.385402672Z   File "/opt/render/project/src/app/services/agent.py", line 8, in <module>
2026-02-05T18:33:51.385404942Z     from openai import AsyncOpenAI
2026-02-05T18:33:51.385407762Z ModuleNotFoundError: No module named 'openai'