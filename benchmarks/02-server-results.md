# 02 - Server Results

Runtime: llama-cpp-python OpenAI-compatible server on `http://localhost:8080`
Model: `models/Llama-3.2-3B-Instruct-Q4_K_M.gguf`
Mode: CPU-only (`LAB_N_GPU_LAYERS=0`, `LAB_N_THREADS=12`, `LAB_N_CTX=2048`, `LAB_N_BATCH=256`)

## Smoke Test

Command:

```powershell
.\python312-embed\python.exe 02-llama-cpp-server\smoke-test.py
```

Result:

- `POST /v1/chat/completions`: OK
- Latency: 7011 ms
- `GET /metrics`: 404 Not Found, expected for the Python server
- Exit code: 0

## Locust Load Test

Command:

```powershell
.\python312-embed\python.exe -m locust -f 02-llama-cpp-server\load-test.py --headless -u 1 -r 1 -t 45s --host http://localhost:8080
```

Result:

| Name | Requests | Failures | Avg ms | Min ms | Max ms | Median ms |
|---|---:|---:|---:|---:|---:|---:|
| short | 2 | 0 | 5470 | 3972 | 6968 | 4000 |
| long-rag | 2 | 0 | 14145 | 10097 | 18194 | 10097 |
| aggregated | 4 | 0 | 9808 | 3972 | 18194 | 7000 |

Notes:

- Throughput is low because this machine is currently running the model CPU-only.
- The Python server does not expose Prometheus `/metrics`; use native `llama-server` with metrics enabled if a metrics CSV is required.
