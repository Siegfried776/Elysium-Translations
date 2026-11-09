. (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) 'gwm_common.ps1')
Write-Host "Great Wall March FA - English patch $($M.version) uninstaller" -ForegroundColor Cyan
$restored = 0; $skipped = 0
foreach ($f in $M.files) {
    $cur = Game-Path $f.path; $bak = Backup-Path $f.path
    if (-not (Test-Path -LiteralPath $bak)) { $skipped++; continue }
    if ((Get-Sha $bak) -ne $f.base) { Write-Host "$($f.path): backup doesn't match the original, left as is." -ForegroundColor Yellow; $skipped++; continue }
    Copy-Item -LiteralPath $bak -Destination $cur -Force; $restored++
}
Write-Host "  $restored game files restored." -ForegroundColor Green
if ($skipped) { Write-Host "  $skipped files had no backup (never patched) and were left as they are." -ForegroundColor Yellow }
foreach ($a in $M.add) {
    $dst = Game-Path $a.path
    if (Test-Path -LiteralPath $dst) { Remove-Item -LiteralPath $dst -Force }
}
Write-Host '  Patch plugins and English readme/credits removed.' -ForegroundColor Green
$gBackup = Backup-Path ('guide/' + $M.guide.folder)
if (Test-Path -LiteralPath $gBackup) {
    $en = Game-Path 'Character Guidebook'
    if (Test-Path -LiteralPath $en) { Remove-Item -LiteralPath $en -Recurse -Force }
    if (-not (Test-Path -LiteralPath (Game-Path $M.guide.folder))) { Move-Item -LiteralPath $gBackup -Destination $Game }
    Write-Host '  Original character guidebook folder restored.' -ForegroundColor Green
}
if (Test-Path -LiteralPath (Backup-Path 'Game.exe')) {   # optional exe icon/name step (exe_icon_and_name.bat)
    Copy-Item -LiteralPath (Backup-Path 'Game.exe') -Destination (Game-Path 'Game.exe') -Force
    if (Test-Path -LiteralPath (Game-Path 'GWMFA.exe')) { Remove-Item -LiteralPath (Game-Path 'GWMFA.exe') -Force }
    Write-Host '  Original Game.exe restored (GWMFA.exe removed).' -ForegroundColor Green
}
Write-Host 'Done. The game is back to the original Japanese.' -ForegroundColor Cyan
