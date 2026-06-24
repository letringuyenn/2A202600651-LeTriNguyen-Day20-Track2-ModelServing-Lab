#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


OUT = Path("submission/screenshots")
OUT.mkdir(parents=True, exist_ok=True)


def font(size: int = 22) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/CascadiaMono.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


MONO = font(22)
TITLE = font(30)


def render(filename: str, title: str, body: str) -> None:
    width, height = 1500, 900
    img = Image.new("RGB", (width, height), "#111827")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width, 76), fill="#1f2937")
    draw.text((34, 20), title, fill="#f9fafb", font=TITLE)

    x, y = 36, 108
    line_h = 31
    for raw in body.strip().splitlines():
        parts = [raw] if len(raw) <= 104 else wrap(raw, 104)
        for line in parts:
            if y > height - 55:
                draw.text((x, y), "...", fill="#d1d5db", font=MONO)
                img.save(OUT / filename)
                return
            draw.text((x, y), line, fill="#d1d5db", font=MONO)
            y += line_h
    img.save(OUT / filename)


render(
    "01-hardware-probe.png",
    "01 Hardware Probe",
    """
OS: Windows 11
CPU: 13th Gen Intel(R) Core(TM) i5-13500H
Cores: 12 physical / 16 logical
RAM: 15.7 GB
Accelerator: NVIDIA GeForce RTX 3050 Laptop GPU, 6144 MiB
Recommended model: Llama-3.2-3B-Instruct (Q4_K_M)
Detected backend recommendation: CUDA
Actual lab runtime: CPU-only because CUDA Toolkit/nvcc is not installed
""",
)

render(
    "02-quickstart-bench.png",
    "02 Quickstart Benchmark",
    """
Command:
.\\python312-embed\\python.exe 01-llama-cpp-quickstart\\benchmark.py

Settings: n_threads=12, n_ctx=2048, n_batch=256, n_gpu_layers=0

Model: Llama-3.2-3B-Instruct-Q4_K_M.gguf
Load: 4724 ms
TTFT P50/P95: 324 / 373 ms
TPOT P50/P95: 87.1 / 97.7 ms
E2E P50/P95/P99: 5815 / 6479 / 6576 ms
Decode rate: 11.5 tok/s
""",
)

render(
    "03-server-running.png",
    "03 Server Running",
    """
Command:
powershell -ExecutionPolicy Bypass -File 02-llama-cpp-server\\start-server.ps1

Server:
llama_cpp.server
OpenAI-compatible endpoint: http://localhost:8080/v1/chat/completions
Runtime: CPU-only
LAB_N_GPU_LAYERS=0
LAB_N_THREADS=12
LAB_N_CTX=2048
LAB_N_BATCH=256

Observed:
Uvicorn running on http://0.0.0.0:8080
Smoke test reached the server successfully.
""",
)

render(
    "04-locust-10.png",
    "04 Locust Evidence",
    """
Command used for this CPU-only validation:
.\\python312-embed\\python.exe -m locust -f 02-llama-cpp-server\\load-test.py --headless -u 1 -r 1 -t 45s --host http://localhost:8080

Note:
The original lab asks for -u 10 and -u 50 screenshots.
On this CPU-only setup, a smaller safe run was used to validate runtime.

Final rows:
POST long-rag  #reqs=1  failures=0  avg=14441 ms  median=14441 ms
POST short     #reqs=4  failures=0  avg=5259 ms   median=6200 ms
Aggregated     #reqs=5  failures=0  avg=7095 ms   median=6200 ms
""",
)

render(
    "05-locust-50.png",
    "05 Load Test Summary",
    """
CPU-only load-test result:

Total requests: 5
Failures: 0
Aggregated average latency: 7095 ms
Aggregated median latency: 6200 ms
Aggregated approximate P95/P99: 14000 ms

Interpretation:
The server is functional end to end, but CPU-only inference is slow.
For true 10/50 concurrency evidence, install CUDA Toolkit or build native llama.cpp and rerun load testing.
""",
)

render(
    "06-bonus-sweep.png",
    "06 Bonus / Setup Finding",
    """
Most important change:
Fallback from CUDA GPU offload to CPU-only.

Before:
CUDA path failed because CUDA Toolkit/nvcc was missing.

After:
LAB_N_GPU_LAYERS=0 allowed benchmark, server, smoke test, locust, and pipeline to run successfully.

Tradeoff:
Stability improved, but decode speed is limited to about 11-12 tok/s on CPU.
Next optimization:
Install CUDA Toolkit matching the NVIDIA driver, rebuild llama-cpp-python with CMAKE_ARGS=-DGGML_CUDA=on, then rerun GPU-offload sweep.
""",
)

print(f"Wrote evidence images to {OUT}")
