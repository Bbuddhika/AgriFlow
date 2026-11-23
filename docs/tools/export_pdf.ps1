$ErrorActionPreference = 'Stop'
$docsRoot = Split-Path -Parent $PSScriptRoot
python (Join-Path $PSScriptRoot 'build_documentation.py')
if ($LASTEXITCODE -ne 0) { throw 'Documentation generation failed.' }
$browser = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
if (-not (Test-Path -LiteralPath $browser)) { throw 'Chrome was not found. Open the generated HTML in a browser and print to PDF.' }
$pdfPath = Join-Path $docsRoot 'output\Dambulla_AgriFlow_Project_Documentation_v1.5.pdf'
$htmlPath = Join-Path $docsRoot 'output\Dambulla_AgriFlow_Project_Documentation_v1.5.html'
$profile = Join-Path ([System.IO.Path]::GetTempPath()) 'agriflow-doc-export'
$htmlUri = ([System.Uri]$htmlPath).AbsoluteUri
# Render only the trusted local generated document; no external content is used.
& $browser --headless --no-sandbox --disable-gpu --disable-software-rasterizer --no-pdf-header-footer "--print-to-pdf=$pdfPath" "--user-data-dir=$profile" $htmlUri
Write-Output $pdfPath
