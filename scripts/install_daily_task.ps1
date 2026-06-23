param(
  [string]$At = "02:00"
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Run: python -m venv .venv; .\.venv\Scripts\pip install -e ." }
$action = New-ScheduledTaskAction -Execute $python -Argument "-m insights_publisher.cli daily --mode auto --push" -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -Daily -At $At
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "Reddit Product Insights Daily Publisher" -Action $action -Trigger $trigger -Settings $settings -Description "Collects and publishes the daily product-insights dump" -Force
Write-Host "Daily publisher task installed for $At."

