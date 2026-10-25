. (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) 'haz_common.ps1')
Write-Host 'Heroine Anthem Zero - English retranslation patch uninstaller' -ForegroundColor Cyan
foreach ($f in $Files) {
    $orig = Join-Path $Data $f
    $bak  = Join-Path $Backup $f
    $patch = Open-Patch (Join-Path $Root "patches\$f.hazpatch")
    if (-not (Test-Path -LiteralPath $bak)) { Write-Host "$f : no backup found, skipping." -ForegroundColor Yellow; continue }
    if ((Get-Sha $bak) -ne $patch.OldHash) { Write-Host "$f : backup doesn't match the original, skipping. Use Steam's 'Verify integrity of game files' instead." -ForegroundColor Yellow; continue }
    Copy-Item -LiteralPath $bak -Destination $orig -Force
    Write-Host "$f : original restored." -ForegroundColor Green
}
Write-Host 'Done.' -ForegroundColor Cyan
