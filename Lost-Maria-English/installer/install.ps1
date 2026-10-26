# LostMaria English patch: installer (run Install.bat, not this file directly).
# Patches the game in place. Every original file it touches is first copied to <game>\_original\,
# every file it adds is listed in _original\added.txt; Uninstall.bat puts everything back.
# Safe to run again (finished files are skipped). ASCII only: Windows PowerShell 5.1 reads it as ANSI.
param([string]$RtpInstaller = "")       # optional: a local copy of rpg2000_rtp_installer.exe (offline / testing)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"   # Invoke-WebRequest is very slow with the progress bar on PS 5.1
$here = Split-Path -Parent $MyInvocation.MyCommand.Path   # <game>\LostMaria_English\files
$pkg  = Split-Path -Parent $here
$game = Split-Path -Parent $pkg
$data = Join-Path $game "data"
$bak  = Join-Path $game "_original"
$tmp  = Join-Path $here "tmp"
$bin  = Join-Path $here "bin"
$RTP_URL  = "https://assets.rpgmakerweb.com/rpg2000_rtp_installer.exe"
$RTP_SHA  = "ec82b92da65ca6fdb2d3df25dfbcd7f2bb716e4fe63a079e8e5e396e91fa5e29"
$RTP_PAGE = "https://www.rpgmakerweb.com/run-time-package"

function Fail($msg) {
    Write-Host ""
    Write-Host "ERROR: $msg" -ForegroundColor Red
    Write-Host "Nothing more was changed. Run Uninstall.bat to undo any partial install." -ForegroundColor Red
    exit 1
}
function Sha($p) { (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLower() }
function ReadTsv($p) {
    $lines = Get-Content -LiteralPath $p -Encoding UTF8
    $head = $lines[0] -split "`t"
    foreach ($l in ($lines | Select-Object -Skip 1)) {
        if (-not $l) { continue }
        $c = $l -split "`t"; $o = [ordered]@{}
        for ($i = 0; $i -lt $head.Count; $i++) { $o[$head[$i]] = $c[$i] }
        [pscustomobject]$o
    }
}
function EnsureDir($file) {
    $d = Split-Path -Parent $file
    if (-not (Test-Path -LiteralPath $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}
function NoteAdded($rel) { Add-Content -LiteralPath (Join-Path $bak "added.txt") -Value $rel -Encoding UTF8 }

Write-Host "LostMaria -The Nameless Flower- English patch"
Write-Host "Game folder: $game"
Write-Host ""
if (-not (Test-Path -LiteralPath (Join-Path $data "RPG_RT.ldb"))) {
    Fail "No data\RPG_RT.ldb here. Put the LostMaria_English folder inside the game folder (next to start.exe and the data folder), then run Install.bat again."
}

# ---- 1. check the game files ---------------------------------------------------------------------
$rows = @(ReadTsv (Join-Path $here "manifest.tsv"))
$todo = @(); $bad = @()
foreach ($r in $rows) {
    $target = Join-Path $game $r.path
    if ((Test-Path -LiteralPath $target) -and ((Sha $target) -eq $r.dst_sha)) { continue }   # already done
    if ($r.base) {
        $src = Join-Path $bak $r.base                       # a backup from an earlier run is the original
        if (-not (Test-Path -LiteralPath $src)) { $src = Join-Path $game $r.base }
        if (-not (Test-Path -LiteralPath $src)) { $bad += "missing:  $($r.base)"; continue }
        if ((Sha $src) -ne $r.base_sha) { $bad += "changed:  $($r.base)"; continue }
        $r | Add-Member -NotePropertyName src -NotePropertyValue $src
    }
    $todo += $r
}
if ($bad.Count) {
    $bad | Select-Object -First 10 | ForEach-Object { Write-Host "  $_" }
    if ($bad.Count -gt 10) { Write-Host "  ... and $($bad.Count - 10) more" }
    Fail ("$($bad.Count) game files are missing or differ from LostMaria v1.20 (BOOTH). " +
          "If the missing names look garbled, the game zip was extracted without its Japanese file names: " +
          "extract it again with 7-Zip, or reinstall the game, then run Install.bat again.")
}
Write-Host "Game files OK (v1.20). $($todo.Count) of $($rows.Count) files to install."

# ---- 2. back up, then patch / copy ------------------------------------------------------------------
if (-not (Test-Path -LiteralPath $bak)) { New-Item -ItemType Directory -Path $bak | Out-Null }
# files an earlier install added (e.g. when updating to a newer version) are not originals: never back them up
$addedFile = Join-Path $bak "added.txt"
$wasAdded = @{}
if (Test-Path -LiteralPath $addedFile) {
    foreach ($l in (Get-Content -LiteralPath $addedFile -Encoding UTF8)) { if ($l) { $wasAdded[$l.ToLower()] = $true } }
}
if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Recurse -Force }
New-Item -ItemType Directory -Path $tmp | Out-Null
$n = 0
foreach ($r in $todo) {
    $target = Join-Path $game $r.path
    $saved = Join-Path $bak $r.path
    if ($wasAdded.ContainsKey($r.path.ToLower())) {
        # added by an earlier install: already listed for removal, nothing to back up
    } elseif (Test-Path -LiteralPath $target) {
        if (-not (Test-Path -LiteralPath $saved)) { EnsureDir $saved; Copy-Item -LiteralPath $target -Destination $saved }
    } else {
        NoteAdded $r.path
        $wasAdded[$r.path.ToLower()] = $true
    }
    $out = Join-Path $tmp "o.bin"
    if ($r.op -eq "patch") {
        # xdelta3 opens files through the ANSI API: give it short ASCII names in the current folder
        Copy-Item -LiteralPath $r.src -Destination (Join-Path $tmp "s.bin") -Force
        Copy-Item -LiteralPath (Join-Path $here $r.payload) -Destination (Join-Path $tmp "p.xd") -Force
        Push-Location -LiteralPath $tmp
        & (Join-Path $bin "xdelta3.exe") -d -f -s s.bin p.xd o.bin
        $code = $LASTEXITCODE
        Pop-Location
        if ($code -ne 0) { Fail "xdelta3 failed on $($r.path)" }
    } else {
        Copy-Item -LiteralPath (Join-Path $here $r.payload) -Destination $out -Force
    }
    if ((Sha $out) -ne $r.dst_sha) { Fail "result check failed on $($r.path)" }
    EnsureDir $target
    Move-Item -LiteralPath $out -Destination $target -Force
    try { Unblock-File -LiteralPath $target } catch {}
    $n++
    if ($n % 100 -eq 0) { Write-Host "  $n / $($todo.Count)" }
}
Write-Host "Installed $n files."

# ---- 3. RPG Maker 2000 RTP sound effects -------------------------------------------------------------
# The game uses sounds from KADOKAWA's free RTP that it doesn't ship. We don't redistribute them: they are
# downloaded from KADOKAWA's site, checked, and only the ones the game uses are copied into data\.
$rtp = @(ReadTsv (Join-Path $here "rtp_files.tsv"))
$need = @($rtp | Where-Object { -not (Test-Path -LiteralPath (Join-Path $data "$($_.folder)\$($_.jp).wav")) })
$installed = $null
foreach ($k in "HKCU:\Software\KADOKAWA\RPG2000", "HKLM:\SOFTWARE\WOW6432Node\KADOKAWA\RPG2000",
               "HKLM:\SOFTWARE\KADOKAWA\RPG2000", "HKLM:\SOFTWARE\WOW6432Node\ASCII\RPG2000", "HKLM:\SOFTWARE\ASCII\RPG2000") {
    try { $p = (Get-ItemProperty -Path $k -ErrorAction Stop).RuntimePackagePath; if ($p -and (Test-Path -LiteralPath $p)) { $installed = $p; break } } catch {}
}
if (-not $need.Count) {
    Write-Host "RTP sounds: already in place."
} elseif ($installed -and -not $RtpInstaller) {
    Write-Host "RTP sounds: the RPG Maker 2000 RTP is installed on this PC ($installed); the game will use it."
} else {
    Write-Host "RTP sounds: getting the official RPG Maker 2000 RTP from KADOKAWA..."
    $ok = $true
    $exe = Join-Path $tmp "rtp.exe"
    try {
        if ($RtpInstaller) { Copy-Item -LiteralPath $RtpInstaller -Destination $exe }
        else {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -Uri $RTP_URL -OutFile $exe -UseBasicParsing
        }
    } catch { $ok = $false; Write-Host "  Download failed: $($_.Exception.Message)" -ForegroundColor Yellow }
    if ($ok -and (Sha $exe) -ne $RTP_SHA) { $ok = $false; Write-Host "  The downloaded file is not the expected RTP installer (it may have been updated)." -ForegroundColor Yellow }
    if ($ok) {
        Push-Location -LiteralPath $tmp
        & (Join-Path $bin "7z.exe") x rtp.exe -ortp "Sound\*" "Music\*" -y | Out-Null
        $code = $LASTEXITCODE
        Pop-Location
        if ($code -ne 0) { $ok = $false; Write-Host "  Unpacking failed (7-Zip exit code $code)." -ForegroundColor Yellow }
    }
    if ($ok) {
        foreach ($r in $need) {
            $src = Join-Path $tmp ("rtp\" + $r.en)
            $rel = "data\$($r.folder)\$($r.jp).wav"
            if (-not (Test-Path -LiteralPath $src)) { $ok = $false; Write-Host "  Not in the RTP: $($r.en)" -ForegroundColor Yellow; continue }
            $dst = Join-Path $game $rel
            EnsureDir $dst
            Copy-Item -LiteralPath $src -Destination $dst
            NoteAdded $rel
        }
    }
    if ($ok) { Write-Host "RTP sounds: $($need.Count) sound files added to data\Sound and data\Music." }
    else {
        Write-Host ""
        Write-Host "The game is installed, but without some sound effects." -ForegroundColor Yellow
        Write-Host "Install the RPG Maker 2000 RTP from $RTP_PAGE and the game will find it," -ForegroundColor Yellow
        Write-Host "or run Install.bat again later." -ForegroundColor Yellow
    }
}
Remove-Item -LiteralPath $tmp -Recurse -Force

Set-Content -LiteralPath (Join-Path $game "ENGLISH_PATCH.txt") -Encoding UTF8 -Value @(
    "The LostMaria English patch is installed in this folder.",
    "Play: start.exe (runs EasyRPG Player, installed as data\RPG_RT.exe).",
    "Undo: run Uninstall.bat in the LostMaria_English folder. The original files are in _original\.",
    "Your saves (data\Save*.lsd) are never touched.")
Write-Host ""
Write-Host "Done! Start the game with start.exe." -ForegroundColor Green
