# Reflection - Lab 20 Personal Report

**Ho Ten:** Le Tri Nguyen  
**Cohort:** A20  
**Ngay submit:** 2026-06-24

## 1. Hardware Spec

- **OS:** Windows 11
- **CPU:** 13th Gen Intel(R) Core(TM) i5-13500H
- **Cores:** 12 physical / 16 logical
- **CPU extensions:** x86_64 / AMD64
- **RAM:** 15.7 GB
- **Accelerator:** NVIDIA GeForce RTX 3050 Laptop GPU, 6 GB VRAM
- **llama.cpp backend da chon:** CPU for this run
- **Recommended model tier:** Llama-3.2-3B-Instruct Q4_K_M

**Setup story:** The laptop has an NVIDIA GPU, but CUDA Toolkit/nvcc was not installed, so the CUDA build path failed. I switched the lab to CPU-only by setting `LAB_N_GPU_LAYERS=0`, reduced batch/context pressure, and used the portable Python 3.12 environment. This made benchmark, server, load test, and pipeline run end to end.

## 2. Track 01 - Quickstart Numbers

Settings: `n_threads=12`, `n_ctx=2048`, `n_batch=256`, `n_gpu_layers=0`.

| Model | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode rate (tok/s) |
|---|---:|---:|---:|---:|---:|
| Llama-3.2-3B-Instruct-Q4_K_M.gguf | 4724 | 324 / 373 | 87.1 / 97.7 | 5815 / 6479 / 6576 | 11.5 |
| Llama-3.2-3B-Instruct-Q2_K.gguf | not downloaded | not run | not run | not run | not run |

**Observation:** Q4_K_M was usable on this 16 GB laptop even in CPU-only mode. I kept Q4_K_M because it is the recommended quality/performance tradeoff; Q2_K was skipped because the compare model download was interrupted.

## 3. Track 02 - llama-server Load Test

Runtime: llama-cpp-python OpenAI-compatible server on `http://localhost:8080`.

| Concurrency | Total RPS | TTFB P50 (ms) | E2E P95 (ms) | E2E P99 (ms) | Failures |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.13 | 6200 | 14000 | 14000 | 0 |
| 10 | not run on this CPU-only setup | not run | not run | not run | not run |
| 50 | not run on this CPU-only setup | not run | not run | not run | not run |

**Batching observation:** The Python `llama_cpp.server` path does not expose Prometheus `/metrics`, so `llamacpp:n_busy_slots_per_decode` was not available. The server still passed OpenAI-compatible smoke testing and Locust requests with 0 failures. For full native metrics, I would need to build native `llama-server` with metrics enabled.

## 4. Track 03 - Milestone Integration

- **N16 (Cloud/IaC):** stub: localhost server on port 8080
- **N17 (Data pipeline):** stub: in-memory toy pipeline
- **N18 (Lakehouse):** stub: in-memory documents
- **N19 (Vector + Feature Store):** stub: `TOY_DOCS` keyword retrieval

Pipeline timings from the latest run:

| Query | Retrieve (ms) | llama-server (ms) | Total (ms) |
|---|---:|---:|---:|
| Why is goodput more useful than throughput? | 0.1 | 8682.4 | 8682.5 |
| What problem does PagedAttention actually solve? | 0.1 | 5750.3 | 5750.4 |
| When should I think about disaggregated serving? | 0.1 | 18222.5 | 18222.6 |

**Reflection:** The bottleneck is clearly llama-server inference, not retrieval. This matches expectation for a CPU-only local LLM run: retrieval is almost free because it is toy in-memory keyword search, while decode dominates latency.

## 5. Bonus - The Single Change That Mattered Most

**Change:** Fall back from CUDA GPU offload to CPU-only with stable settings: `LAB_N_GPU_LAYERS=0`, `LAB_N_THREADS=12`, `LAB_N_CTX=2048`, `LAB_N_BATCH=256`.

Before vs after:

```text
before: CUDA build failed because CUDA Toolkit/nvcc was missing
after : CPU-only benchmark and server both ran successfully
speedup: not a speedup; this was a stability fix that unblocked the lab
```

**Why it worked:** The NVIDIA driver alone is not enough to compile the CUDA backend for llama-cpp-python. Without CUDA Toolkit and `nvcc`, the GPU build path fails before runtime. CPU-only mode avoids that native build dependency and keeps memory use predictable on a 16 GB laptop. The tradeoff is slower decode, around 11-12 tokens/s in this run, but the system becomes reliable enough to finish the core lab.

## 6. Most Surprising Thing

The biggest surprise was that the Python server has no `/metrics` endpoint, even though the native llama.cpp server can expose Prometheus metrics. For this setup, Locust output became the practical Track 02 evidence.

## 7. Self-Graded Checklist

- [x] `hardware.json` exists
- [x] `models/active.json` exists
- [x] `benchmarks/01-quickstart-results.md` exists
- [x] `benchmarks/02-server-results.md` exists
- [ ] `benchmarks/bonus-*.md` committed
- [x] At least 6 screenshots/evidence images in `submission/screenshots/`
- [x] `scripts/verify.py` checked after setup fixes
- [ ] Repo is public on GitHub
- [ ] Public repo URL pasted into VinUni LMS
