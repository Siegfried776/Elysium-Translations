# Great Wall March FA - English patch: shared helpers for install.ps1 / uninstall.ps1
# (ASCII only on purpose: Japanese folder names come from manifest.json, which is read as UTF-8.)
$ErrorActionPreference = 'Stop'
$Root   = Split-Path -Parent $MyInvocation.MyCommand.Path
$Game   = Split-Path -Parent $Root
$Backup = Join-Path $Root 'backup'
$Work   = Join-Path $Root 'work'
$XD     = Join-Path $Root 'xdelta3.exe'
$M      = Get-Content -LiteralPath (Join-Path $Root 'manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json

function Get-Sha([string]$Path) { (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash }
function Game-Path([string]$Rel)   { Join-Path $Game   ($Rel -replace '/', '\') }
function Backup-Path([string]$Rel) { Join-Path $Backup ($Rel -replace '/', '\') }
function Ensure-Dir([string]$File) { New-Item -ItemType Directory -Force -Path (Split-Path -Parent $File) | Out-Null }

# Character guidebook sheets ship as overlays: a PNG the size of the sheet holding only the pixels the English
# version changes (text panel, name plate, credit), transparent elsewhere, so no artwork is in the patch. Windows'
# own System.Drawing (GDI+) reads the player's original sheet, the changed pixels are copied over byte for byte,
# and the result's raw pixels must match the SHA-256 in the manifest before it is saved. Nothing to install.
Add-Type -AssemblyName System.Drawing
if (-not ('GwmGuide' -as [type])) {
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
public static class GwmGuide {
    static byte[] Read(string path, out int w, out int h) {
        using (var bmp = new Bitmap(path)) {
            w = bmp.Width; h = bmp.Height;
            var d = bmp.LockBits(new Rectangle(0, 0, w, h), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
            try {
                if (d.Stride != w * 4) throw new Exception("unexpected stride");
                var buf = new byte[w * h * 4];
                Marshal.Copy(d.Scan0, buf, 0, buf.Length);
                return buf;
            } finally { bmp.UnlockBits(d); }
        }
    }
    static string Hash(byte[] buf) {
        using (var sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(buf)).Replace("-", "");
    }
    public static string PixelSha(string path) { int w, h; return Hash(Read(path, out w, out h)); }
    // Writes the English sheet to outPath and returns the SHA-256 of its raw BGRA pixels.
    public static string Apply(string srcPath, string overlayPath, string outPath) {
        int w, h, ow, oh;
        var px = Read(srcPath, out w, out h);
        var ov = Read(overlayPath, out ow, out oh);
        if (w != ow || h != oh) throw new Exception("overlay size does not match the sheet");
        for (int i = 0; i < px.Length; i += 4)
            if (ov[i + 3] != 0) { px[i] = ov[i]; px[i + 1] = ov[i + 1]; px[i + 2] = ov[i + 2]; px[i + 3] = ov[i + 3]; }
        using (var bmp = new Bitmap(w, h, PixelFormat.Format32bppArgb)) {
            var d = bmp.LockBits(new Rectangle(0, 0, w, h), ImageLockMode.WriteOnly, PixelFormat.Format32bppArgb);
            Marshal.Copy(px, 0, d.Scan0, px.Length);
            bmp.UnlockBits(d);
            bmp.Save(outPath, ImageFormat.Png);
        }
        return Hash(px);
    }
}
'@
}

function Invoke-GuideOverlay([string]$Source, [string]$Overlay, [string]$Target, [string]$ExpectPix) {
    New-Item -ItemType Directory -Force -Path $Work | Out-Null
    $out = Join-Path $Work 'sheet.png'
    if (Test-Path -LiteralPath $out) { Remove-Item -LiteralPath $out -Force }
    $made = [GwmGuide]::Apply($Source, $Overlay, $out)
    if ($made -ne $ExpectPix) { throw "Guidebook sheet $Target failed its check. Nothing was overwritten." }
    if ([GwmGuide]::PixelSha($out) -ne $ExpectPix) { throw "Guidebook sheet $Target failed its check after saving. Nothing was overwritten." }
    Ensure-Dir $Target
    Move-Item -LiteralPath $out -Destination $Target -Force
}

# xdelta3 is run on short ASCII names inside $Work (relative paths), so a Japanese game-folder name or user name
# never reaches its file-open calls.
function Invoke-XDelta([string]$Source, [string]$Patch, [string]$Target, [string]$ExpectSha) {
    New-Item -ItemType Directory -Force -Path $Work | Out-Null
    Copy-Item -LiteralPath $Source -Destination (Join-Path $Work 'src.bin') -Force
    Copy-Item -LiteralPath $Patch  -Destination (Join-Path $Work 'p.xdelta') -Force
    $out = Join-Path $Work 'out.bin'
    if (Test-Path -LiteralPath $out) { Remove-Item -LiteralPath $out -Force }
    $cwd = [Environment]::CurrentDirectory
    Push-Location -LiteralPath $Work
    [Environment]::CurrentDirectory = $Work
    try { & $XD -d -f -s src.bin p.xdelta out.bin; $code = $LASTEXITCODE }
    finally { Pop-Location; [Environment]::CurrentDirectory = $cwd }
    if ($code -ne 0 -or -not (Test-Path -LiteralPath $out)) { throw "xdelta3 failed on $Target" }
    if ((Get-Sha $out) -ne $ExpectSha) { throw "Patched $Target failed its check. Nothing was overwritten." }
    Ensure-Dir $Target
    Move-Item -LiteralPath $out -Destination $Target -Force
}
