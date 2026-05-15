$ErrorActionPreference = 'Stop'
$cwd = 'C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner'
$statePath = Join-Path $cwd 'outputs\reproducibility_run_16b\long_run\state.json'
$out = Join-Path $cwd 'outputs\reproducibility_run_16c'
if (!(Test-Path $out)) { New-Item -ItemType Directory -Path $out | Out-Null }
$logPath = Join-Path $out 'supervisor_start.log'
while ($true) {
    if (Test-Path $statePath) {
        $state = Get-Content $statePath -Raw | ConvertFrom-Json
        if ($state.status -eq 'completed') {
            $stdout = Join-Path $out 'process_stdout.log'
            $stderr = Join-Path $out 'process_stderr.log'
            $args = @(
                'run_pipeline.py',
                '--input-csv','outputs/full_run_12_full/corpus.csv',
                '--output-dir','outputs/reproducibility_run_16c',
                '--run-profile','balanced_full',
                '--llm-provider','openai',
                '--model','gpt-4o-mini',
                '--policy','v1',
                '--with-llm-triage',
                '--download-content',
                '--auto-pdf-download',
                '--enable-figure',
                '--with-llm-adjudication',
                '--long-run-mode',
                '--long-run-log-every','25',
                '--resume',
                '--export-csv',
                '--no-status-panel'
            )
            Start-Process python -ArgumentList $args -WorkingDirectory $cwd -RedirectStandardOutput $stdout -RedirectStandardError $stderr | Out-Null
            "started 16c after 16b completion at $(Get-Date -Format o)" | Set-Content -Path $logPath -Encoding UTF8
            break
        }
        elseif ($state.status -ne 'running') {
            "did not start 16c because 16b ended with status=$($state.status) at $(Get-Date -Format o)" | Set-Content -Path $logPath -Encoding UTF8
            break
        }
    }
    Start-Sleep -Seconds 60
}
