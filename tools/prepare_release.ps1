$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskPython = Get-Command python -ErrorAction SilentlyContinue
if (-not $taskPython) { throw 'Python 3 is required. Please install Python 3 and retry.' }
& $taskPython.Source (Join-Path $PSScriptRoot 'prepare_site.py')
if ($LASTEXITCODE -ne 0) { throw 'Site preparation failed.' }
& $taskPython.Source (Join-Path $PSScriptRoot 'validate_site.py')
if ($LASTEXITCODE -ne 0) { throw 'Site validation failed. No archive created.' }
& $taskPython.Source (Join-Path $PSScriptRoot 'indexnow.py')
if ($LASTEXITCODE -ne 0) { throw 'IndexNow payload preparation failed.' }
$taskArchive = Join-Path (Split-Path -Parent $taskRoot) 'jcvpn-blog-upload.zip'
& $taskPython.Source (Join-Path $PSScriptRoot 'prepare_site.py') --zip $taskArchive
if ($LASTEXITCODE -ne 0) { throw 'Packaging failed.' }
Write-Output 'Ready. Upload the contents of jcvpn-blog-upload.zip to your website root. No URLs have been submitted.'
