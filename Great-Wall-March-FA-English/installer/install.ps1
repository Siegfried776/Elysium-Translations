. (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) 'gwm_common.ps1')
Write-Host "Great Wall March FA - English patch $($M.version) installer" -ForegroundColor Cyan
if (-not (Test-Path -LiteralPath (Game-Path 'www/data/System.json'))) {
    throw "Can't find the game's www folder. Put the 'GWM English Patch' folder inside the game folder (next to Game.exe) and run install.bat again."
}

# 1. Check every file first. Nothing is changed unless all of them are the expected v1.043 originals
#    (or already patched, or backed up by an earlier run).
Write-Host 'Checking game files...'
$plan = @(); $bad = @()
foreach ($f in $M.files) {
    $cur = Game-Path $f.path; $bak = Backup-Path $f.path
    $curSha = if (Test-Path -LiteralPath $cur) { Get-Sha $cur } else { '' }
    if ($curSha -eq $f.new) { continue }
    if ($curSha -eq $f.base) { $plan += ,@($f, 'orig'); continue }
    if ((Test-Path -LiteralPath $bak) -and (Get-Sha $bak) -eq $f.base) { $plan += ,@($f, 'backup'); continue }
    $bad += $f.path
}
$gFolder = Game-Path $M.guide.folder
$gBackup = Backup-Path ('guide/' + $M.guide.folder)
$guideSrc = $null
if (Test-Path -LiteralPath $gBackup) { $guideSrc = $gBackup } elseif (Test-Path -LiteralPath $gFolder) { $guideSrc = $gFolder }
if ($guideSrc) {
    foreach ($s in $M.guide.sheets) {
        $src = Join-Path $guideSrc (($s.from -replace '/', '\').Substring($M.guide.folder.Length + 1))
        if (-not (Test-Path -LiteralPath $src) -or (Get-Sha $src) -ne $s.base) { $bad += $s.from }
    }
}
if ($bad.Count) {
    Write-Host "These files don't match Great Wall March FA v1.043 (the version this patch was made for):" -ForegroundColor Red
    $bad | Select-Object -First 15 | ForEach-Object { Write-Host "  $_" }
    if ($bad.Count -gt 15) { Write-Host "  ... and $($bad.Count - 15) more" }
    throw 'Nothing was changed.'
}

# 2. Patch the game files (originals are copied to backup\ first).
$i = 0
foreach ($step in $plan) {
    $f = $step[0]; $i++
    $cur = Game-Path $f.path; $bak = Backup-Path $f.path
    if ($step[1] -eq 'orig' -and -not (Test-Path -LiteralPath $bak)) { Ensure-Dir $bak; Copy-Item -LiteralPath $cur -Destination $bak }
    Write-Progress -Activity 'Patching game files' -Status $f.path -PercentComplete (100 * $i / $plan.Count)
    Invoke-XDelta $bak (Join-Path $Root $f.patch) $cur $f.new
}
Write-Progress -Activity 'Patching game files' -Completed
Write-Host "  $($plan.Count) game files patched ($($M.files.Count - $plan.Count) already up to date)." -ForegroundColor Green

# 3. New files: the patch's plugins and the English readme/credits.
foreach ($a in $M.add) {
    $dst = Game-Path $a.path; Ensure-Dir $dst
    Copy-Item -LiteralPath (Join-Path $Root $a.src) -Destination $dst -Force
}
Write-Host "  $($M.add.Count) files added (plugins, readme_en.txt, credits_en.txt)." -ForegroundColor Green

# 4. Character guidebook: the Japanese folder moves to backup\guide; "Character Guidebook" gets the English
#    sheets of both sides (the demon side in "Demon Side (Spoilers)").
if ($guideSrc) {
    if ($guideSrc -eq $gFolder) { Ensure-Dir $gBackup; Move-Item -LiteralPath $gFolder -Destination $gBackup; $guideSrc = $gBackup }
    elseif (Test-Path -LiteralPath $gFolder) { Remove-Item -LiteralPath $gFolder -Recurse -Force }
    $human = Game-Path 'Character Guidebook/Human Side'; $demon = Game-Path 'Character Guidebook/Demon Side (Spoilers)'
    New-Item -ItemType Directory -Force -Path $human, $demon | Out-Null
    # an older build put the untranslated demon-side sheets here: keep only this version's files
    $keep = @($M.guide.sheets | ForEach-Object { (Game-Path $_.path).ToLowerInvariant() })
    Get-ChildItem -LiteralPath $demon -File | Where-Object { $keep -notcontains $_.FullName.ToLowerInvariant() } | Remove-Item -Force
    foreach ($s in $M.guide.sheets) {
        $dst = Game-Path $s.path
        if ((Test-Path -LiteralPath $dst) -and [GwmGuide]::PixelSha($dst) -eq $s.pix) { continue }
        $src = Join-Path $guideSrc (($s.from -replace '/', '\').Substring($M.guide.folder.Length + 1))
        Invoke-GuideOverlay $src (Join-Path $Root $s.overlay) $dst $s.pix
    }
    Write-Host '  Character guidebook: English human side and demon side (spoilers).' -ForegroundColor Green
} else {
    Write-Host '  Character guidebook folder not found; skipped.' -ForegroundColor Yellow
}
if (Test-Path -LiteralPath $Work) { Remove-Item -LiteralPath $Work -Recurse -Force }
Write-Host 'English patch installed. Run uninstall.bat to restore the Japanese game.' -ForegroundColor Cyan
