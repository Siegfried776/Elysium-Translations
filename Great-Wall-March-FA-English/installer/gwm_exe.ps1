# Optional: give the game exe the game's own icon (www/icon/icon.png) and rename Game.exe -> GWMFA.exe.
# The original Game.exe is kept in backup\Game.exe; uninstall.bat (or this script with -Undo) puts it back.
# Uses only Windows' own resource API (BeginUpdateResource/UpdateResource) - no extra tools.
param([switch]$Undo)
. (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) 'gwm_common.ps1')
$exe    = Join-Path $Game 'Game.exe'
$newExe = Join-Path $Game 'GWMFA.exe'
$bak    = Join-Path $Backup 'Game.exe'

if ($Undo) {
    if (-not (Test-Path -LiteralPath $bak)) { Write-Host 'No backed-up Game.exe; nothing to undo.' -ForegroundColor Yellow; return }
    Copy-Item -LiteralPath $bak -Destination $exe -Force
    if (Test-Path -LiteralPath $newExe) { Remove-Item -LiteralPath $newExe -Force }
    Write-Host 'Original Game.exe restored.' -ForegroundColor Green
    return
}

Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
public static class GwmIcon {
    const uint LOAD_LIBRARY_AS_DATAFILE = 0x2;
    static readonly IntPtr RT_ICON = (IntPtr)3, RT_GROUP_ICON = (IntPtr)14;
    delegate bool EnumNameProc(IntPtr h, IntPtr type, IntPtr name, IntPtr p);
    delegate bool EnumLangProc(IntPtr h, IntPtr type, IntPtr name, ushort lang, IntPtr p);
    [DllImport("kernel32", SetLastError = true, CharSet = CharSet.Unicode)] static extern IntPtr LoadLibraryEx(string f, IntPtr h, uint fl);
    [DllImport("kernel32")] static extern bool FreeLibrary(IntPtr h);
    [DllImport("kernel32", CharSet = CharSet.Unicode)] static extern bool EnumResourceNames(IntPtr h, IntPtr type, EnumNameProc cb, IntPtr p);
    [DllImport("kernel32", CharSet = CharSet.Unicode)] static extern bool EnumResourceLanguages(IntPtr h, IntPtr type, IntPtr name, EnumLangProc cb, IntPtr p);
    [DllImport("kernel32", CharSet = CharSet.Unicode)] static extern bool EnumResourceLanguages(IntPtr h, IntPtr type, string name, EnumLangProc cb, IntPtr p);
    [DllImport("kernel32", CharSet = CharSet.Unicode)] static extern IntPtr FindResourceEx(IntPtr h, IntPtr type, string name, ushort lang);
    [DllImport("kernel32", SetLastError = true, CharSet = CharSet.Unicode)] static extern bool UpdateResource(IntPtr h, IntPtr type, string name, ushort lang, byte[] data, uint size);
    [DllImport("kernel32")] static extern IntPtr FindResourceEx(IntPtr h, IntPtr type, IntPtr name, ushort lang);
    [DllImport("kernel32")] static extern IntPtr LoadResource(IntPtr h, IntPtr res);
    [DllImport("kernel32")] static extern IntPtr LockResource(IntPtr data);
    [DllImport("kernel32")] static extern uint SizeofResource(IntPtr h, IntPtr res);
    [DllImport("kernel32", SetLastError = true, CharSet = CharSet.Unicode)] static extern IntPtr BeginUpdateResource(string f, bool del);
    [DllImport("kernel32", SetLastError = true)] static extern bool UpdateResource(IntPtr h, IntPtr type, IntPtr name, ushort lang, byte[] data, uint size);
    [DllImport("kernel32", SetLastError = true)] static extern bool EndUpdateResource(IntPtr h, bool discard);

    // images: PNG bytes per size (width = height); written as PNG-compressed icon entries (Vista and later).
    public static string Replace(string exe, int[] sizes, byte[][] pngs) {
        IntPtr mod = LoadLibraryEx(exe, IntPtr.Zero, LOAD_LIBRARY_AS_DATAFILE);
        if (mod == IntPtr.Zero) throw new Exception("Can't open " + exe);
        IntPtr groupName = IntPtr.Zero; string groupStr = null; ushort lang = 0; var oldIds = new List<ushort>(); int maxId = 0;
        try {
            bool found = false;
            EnumResourceNames(mod, RT_GROUP_ICON, (h, t, n, p) => {
                found = true;
                if (((long)n >> 16) == 0) groupName = n; else groupStr = Marshal.PtrToStringUni(n);
                return false; }, IntPtr.Zero);
            if (!found) throw new Exception("The exe has no icon to replace.");
            EnumLangProc lp = (h, t, n, l, p) => { lang = l; return false; };
            if (groupStr != null) EnumResourceLanguages(mod, RT_GROUP_ICON, groupStr, lp, IntPtr.Zero);
            else EnumResourceLanguages(mod, RT_GROUP_ICON, groupName, lp, IntPtr.Zero);
            IntPtr res = groupStr != null ? FindResourceEx(mod, RT_GROUP_ICON, groupStr, lang) : FindResourceEx(mod, RT_GROUP_ICON, groupName, lang);
            if (res == IntPtr.Zero) throw new Exception("Icon group not found.");
            byte[] grp = new byte[SizeofResource(mod, res)];
            Marshal.Copy(LockResource(LoadResource(mod, res)), grp, 0, grp.Length);
            int count = BitConverter.ToUInt16(grp, 4);
            for (int i = 0; i < count; i++) oldIds.Add(BitConverter.ToUInt16(grp, 6 + i * 14 + 12));
            EnumResourceNames(mod, RT_ICON, (h, t, n, p) => { if (((long)n >> 16) == 0) maxId = Math.Max(maxId, (int)n); return true; }, IntPtr.Zero);
        } finally { FreeLibrary(mod); }
        var ids = new List<ushort>();
        for (int i = 0; i < pngs.Length; i++) ids.Add(i < oldIds.Count ? oldIds[i] : (ushort)(++maxId));
        IntPtr upd = BeginUpdateResource(exe, false);
        if (upd == IntPtr.Zero) throw new Exception("Can't write to " + exe + " (is the game running?)");
        bool ok = false;
        try {
            for (int i = pngs.Length; i < oldIds.Count; i++) UpdateResource(upd, RT_ICON, (IntPtr)oldIds[i], lang, null, 0);
            var ms = new MemoryStream(); var w = new BinaryWriter(ms);
            w.Write((ushort)0); w.Write((ushort)1); w.Write((ushort)pngs.Length);
            for (int i = 0; i < pngs.Length; i++) {
                if (!UpdateResource(upd, RT_ICON, (IntPtr)ids[i], lang, pngs[i], (uint)pngs[i].Length)) throw new Exception("UpdateResource failed");
                int s = sizes[i];
                w.Write((byte)(s >= 256 ? 0 : s)); w.Write((byte)(s >= 256 ? 0 : s)); w.Write((byte)0); w.Write((byte)0);
                w.Write((ushort)1); w.Write((ushort)32); w.Write((uint)pngs[i].Length); w.Write(ids[i]);
            }
            byte[] g = ms.ToArray();
            bool okg = groupStr != null ? UpdateResource(upd, RT_GROUP_ICON, groupStr, lang, g, (uint)g.Length)
                                        : UpdateResource(upd, RT_GROUP_ICON, groupName, lang, g, (uint)g.Length);
            if (!okg) throw new Exception("UpdateResource failed");
            ok = true;
        } finally {
            if (!EndUpdateResource(upd, !ok) && ok) throw new Exception("Writing the exe failed.");
        }
        return string.Format("group {0}, lang {1}, {2} images", groupStr ?? ((int)groupName).ToString(), lang, pngs.Length);
    }
}
'@

Write-Host 'Great Wall March FA - exe icon and name (optional)' -ForegroundColor Cyan
if (Test-Path -LiteralPath $newExe) { Write-Host 'GWMFA.exe already exists; nothing to do.' -ForegroundColor Green; return }
if (-not (Test-Path -LiteralPath $exe)) { throw "Can't find Game.exe next to the www folder." }
$png = Game-Path 'www/icon/icon.png'
if (-not (Test-Path -LiteralPath $png)) { throw "Can't find www\icon\icon.png." }
if (-not (Test-Path -LiteralPath $bak)) { New-Item -ItemType Directory -Force -Path $Backup | Out-Null; Copy-Item -LiteralPath $exe -Destination $bak }

# Icon sizes Windows uses (16-256), scaled from the game's 128 px icon with high-quality resampling.
$src = [Drawing.Image]::FromFile($png)
$sizes = @(16, 24, 32, 48, 64, 128, 256); $pngs = @()
foreach ($s in $sizes) {
    $bmp = New-Object Drawing.Bitmap($s, $s, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $gr = [Drawing.Graphics]::FromImage($bmp)
    $gr.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $gr.PixelOffsetMode = [Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $gr.DrawImage($src, 0, 0, $s, $s); $gr.Dispose()
    $ms = New-Object IO.MemoryStream; $bmp.Save($ms, [Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
    $pngs += ,$ms.ToArray()
}
$src.Dispose()

$tmp = Join-Path $Game 'GWMFA.exe.tmp'
Copy-Item -LiteralPath $exe -Destination $tmp -Force
try { $info = [GwmIcon]::Replace($tmp, [int[]]$sizes, [byte[][]]$pngs) }
catch { Remove-Item -LiteralPath $tmp -Force; throw }
Move-Item -LiteralPath $tmp -Destination $newExe
Remove-Item -LiteralPath $exe -Force
Write-Host "  Icon replaced ($info)." -ForegroundColor Green
Write-Host '  Game.exe renamed to GWMFA.exe (original kept in backup\Game.exe).' -ForegroundColor Green
Write-Host 'Start the game with GWMFA.exe. If Windows still shows the old icon, it is the icon cache; it updates on its own.' -ForegroundColor Cyan
