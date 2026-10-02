. (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) 'haz_common.ps1')
Write-Host 'Heroine Anthem Zero - English revision patch installer' -ForegroundColor Cyan
if (-not (Test-Path -LiteralPath $Data)) { throw "Can't find $Data. Put this folder inside the game folder (next to HeroineAnthemZero.exe)." }
New-Item -ItemType Directory -Force -Path $Backup | Out-Null
foreach ($f in $Files) {
    $orig  = Join-Path $Data $f
    $bak   = Join-Path $Backup $f
    $patch = Open-Patch (Join-Path $Root "patches\$f.hazpatch")
    Write-Host "Checking $f ..."
    $cur = Get-Sha $orig
    if ($cur -eq $patch.NewHash) { Write-Host "  already patched, skipping." -ForegroundColor Green; continue }
    if ($cur -eq $patch.OldHash) {
        if (-not (Test-Path -LiteralPath $bak)) { Copy-Item -LiteralPath $orig -Destination $bak; Write-Host '  original backed up.' }
        $source = $bak
    } elseif ((Test-Path -LiteralPath $bak) -and ((Get-Sha $bak) -eq $patch.OldHash)) {
        $source = $bak
    } else {
        throw "  $f doesn't match the game version this patch was made for (the game may have been updated). Nothing was changed."
    }
    if ((Get-Sha $source) -ne $patch.OldHash) { throw "  backup of $f is damaged. Verify the game files in Steam and run the installer again." }
    $tmp = "$orig.haztmp"
    Write-Host '  patching...'
    Invoke-Patch $patch $source $tmp
    if ((Get-Sha $tmp) -ne $patch.NewHash) { Remove-Item -LiteralPath $tmp; throw "  patched $f failed its check. Nothing was changed." }
    Move-Item -LiteralPath $tmp -Destination $orig -Force
    Write-Host "  done." -ForegroundColor Green
}
Write-Host 'Patch installed. Run uninstall.bat to restore the original English.' -ForegroundColor Cyan
