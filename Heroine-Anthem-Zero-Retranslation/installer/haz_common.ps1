# Heroine Anthem Zero - English retranslation patch (full game: all dialogue, UI, items, quests, maps)
$ErrorActionPreference = 'Stop'
$Root  = Split-Path -Parent $MyInvocation.MyCommand.Path
$Game  = Split-Path -Parent $Root
$Data  = Join-Path $Game 'HeroineAnthemZero_Data'
$Backup = Join-Path $Root 'backup'
$Files = @('sharedassets0.assets', 'resources.assets', 'level0', 'Managed\Assembly-CSharp.dll')

function Get-Sha([string]$Path) { (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash }

function Read-PatchBytes([string]$PatchPath) {
    $fs = [IO.File]::OpenRead($PatchPath)
    try {
        $gz = New-Object IO.Compression.GZipStream($fs, [IO.Compression.CompressionMode]::Decompress)
        $ms = New-Object IO.MemoryStream
        $gz.CopyTo($ms); $gz.Dispose()
        return ,$ms.ToArray()
    } finally { $fs.Dispose() }
}

function Open-Patch([string]$PatchPath) {
    $bytes = Read-PatchBytes $PatchPath
    $br = New-Object IO.BinaryReader((New-Object IO.MemoryStream(,$bytes)))
    $magic = [Text.Encoding]::ASCII.GetString($br.ReadBytes(5))
    if ($magic -ne 'HAZP1') { throw "Not a valid patch file: $PatchPath" }
    $oldLen  = $br.ReadUInt64()
    $newLen  = $br.ReadUInt64()
    $oldHash = ([BitConverter]::ToString($br.ReadBytes(32))).Replace('-', '')
    $newHash = ([BitConverter]::ToString($br.ReadBytes(32))).Replace('-', '')
    $ops     = $br.ReadUInt32()
    return [PSCustomObject]@{ OldLen = $oldLen; NewLen = $newLen; OldHash = $oldHash; NewHash = $newHash; OpCount = $ops; Reader = $br }
}

function Invoke-Patch($Patch, [string]$Source, [string]$Target) {
    $br = $Patch.Reader
    $src = [IO.File]::OpenRead($Source)
    $dst = [IO.File]::Create($Target)
    $buf = New-Object byte[] (1048576)
    try {
        for ($i = 0; $i -lt $Patch.OpCount; $i++) {
            $kind = $br.ReadByte()
            if ($kind -eq 67) {          # 'C' = copy from original
                $off = $br.ReadUInt64(); $len = [long]$br.ReadUInt32()
                [void]$src.Seek([long]$off, [IO.SeekOrigin]::Begin)
                while ($len -gt 0) {
                    $want = [int][Math]::Min($len, [long]$buf.Length)
                    $got = $src.Read($buf, 0, $want)
                    if ($got -le 0) { throw 'Original file ended unexpectedly.' }
                    $dst.Write($buf, 0, $got); $len -= $got
                }
            } elseif ($kind -eq 68) {    # 'D' = new data
                $len = [int]$br.ReadUInt32()
                $d = $br.ReadBytes($len)
                $dst.Write($d, 0, $d.Length)
            } else { throw 'Patch file is corrupt.' }
        }
    } finally { $src.Dispose(); $dst.Dispose() }
}
