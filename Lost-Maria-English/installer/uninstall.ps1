# LostMaria English patch: uninstaller (run Uninstall.bat). Restores every original file from
# <game>\_original\, deletes the files the patch added (listed in _original\added.txt). Saves are kept.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$game = Split-Path -Parent (Split-Path -Parent $here)
$bak  = Join-Path $game "_original"
if (-not (Test-Path -LiteralPath $bak)) {
    Write-Host "No _original folder: the patch is not installed here (nothing to undo)."
    exit 1
}
$added = Join-Path $bak "added.txt"
$nd = 0
if (Test-Path -LiteralPath $added) {
    foreach ($rel in (Get-Content -LiteralPath $added -Encoding UTF8)) {
        if (-not $rel) { continue }
        $f = Join-Path $game $rel
        if (Test-Path -LiteralPath $f) { Remove-Item -LiteralPath $f -Force; $nd++ }
    }
    Remove-Item -LiteralPath $added -Force
}
$nr = 0
$root = (Resolve-Path -LiteralPath $bak).ProviderPath.TrimEnd("\") + "\"
foreach ($f in (Get-ChildItem -LiteralPath $bak -Recurse -File)) {
    $rel = $f.FullName.Substring($root.Length)
    $dst = Join-Path $game $rel
    $d = Split-Path -Parent $dst
    if (-not (Test-Path -LiteralPath $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
    Copy-Item -LiteralPath $f.FullName -Destination $dst -Force
    $nr++
}
Remove-Item -LiteralPath $bak -Recurse -Force
# folders the patch created and left empty (data\Font)
$font = Join-Path $game "data\Font"
if ((Test-Path -LiteralPath $font) -and -not (Get-ChildItem -LiteralPath $font -Force)) { Remove-Item -LiteralPath $font }
$note = Join-Path $game "ENGLISH_PATCH.txt"
if (Test-Path -LiteralPath $note) { Remove-Item -LiteralPath $note -Force }
Write-Host "Restored $nr original files and removed $nd added files. The game is back to the original Japanese version."
