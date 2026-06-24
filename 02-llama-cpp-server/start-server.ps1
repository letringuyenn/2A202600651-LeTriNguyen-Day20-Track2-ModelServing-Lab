# Launch llama-server (via llama-cpp-python) reading models/active.json.
# Windows PowerShell 7+.
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')

$Python = Join-Path (Get-Location) 'python312-embed\python.exe'
if (-not (Test-Path $Python)) {
    $Python = 'python'
}

$active = Get-Content 'models\active.json' -Raw -Encoding UTF8 | ConvertFrom-Json
$hardware = Get-Content 'hardware.json' -Raw -Encoding UTF8 | ConvertFrom-Json

$model   = $active.primary_model
$threads = if ($hardware.cpu.cores_physical) { $hardware.cpu.cores_physical } else { '4' }
$gpu     = if ($env:LAB_N_GPU_LAYERS) { $env:LAB_N_GPU_LAYERS } else { '0' }
$ctx     = if ($env:LAB_N_CTX) { $env:LAB_N_CTX } else { '2048' }
$batch   = if ($env:LAB_N_BATCH) { $env:LAB_N_BATCH } else { '256' }

Write-Host "==> Starting llama-server" -ForegroundColor Cyan
Write-Host "    model     : $model"
Write-Host "    threads   : $threads"
Write-Host "    gpu_layers: $gpu"
Write-Host "    ctx       : $ctx"
Write-Host "    batch     : $batch"
Write-Host "    listening : http://0.0.0.0:8080"
Write-Host ""

& $Python -m llama_cpp.server `
    --model "$model" `
    --host 0.0.0.0 --port 8080 `
    --n_threads $threads `
    --n_gpu_layers $gpu `
    --n_ctx $ctx `
    --n_batch $batch `
    --logits_all False
