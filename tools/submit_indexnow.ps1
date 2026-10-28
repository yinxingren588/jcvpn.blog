$ErrorActionPreference = 'Stop'
$taskPython = Get-Command python -ErrorAction SilentlyContinue
if (-not $taskPython) { throw 'Python 3 is required. Please install Python 3 and retry.' }
& $taskPython.Source (Join-Path $PSScriptRoot 'validate_site.py')
if ($LASTEXITCODE -ne 0) { throw 'Site validation failed. No URLs submitted.' }
& $taskPython.Source (Join-Path $PSScriptRoot 'indexnow.py') --submit
if ($LASTEXITCODE -ne 0) { throw 'Not submitted successfully. Check the message above and upload the prepared files before retrying.' }
