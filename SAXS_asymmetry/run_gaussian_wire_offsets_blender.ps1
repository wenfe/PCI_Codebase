<# Build and render the figure using Blender's bundled scripting runtime. #>
[CmdletBinding()]
param(
    [string]$BlenderPath,
    [double[]]$Offsets = @(-5, 0, 5),
    [double]$Fwhm,
    [int]$Resolution = 3200,
    [int]$Samples = 48,
    [string]$OutputDir,
    [string]$OutputStem = 'gaussian_wire_offsets_blender'
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not $BlenderPath) {
    $foundBlender = Get-Command blender -ErrorAction SilentlyContinue
    if ($foundBlender) { $BlenderPath = $foundBlender.Source }
}
if (-not $BlenderPath) {
    $candidates = @(
        (Join-Path $repoRoot 'tmp/blender-runtime/blender-4.5.13-windows-x64/blender.exe'),
        'C:/Program Files/Blender Foundation/Blender 4.5/blender.exe'
    )
    $BlenderPath = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if (-not $BlenderPath -or -not (Test-Path -LiteralPath $BlenderPath)) {
    throw 'Blender was not found. Pass -BlenderPath with the path to blender.exe.'
}
if ($Offsets.Count -ne 3) { throw 'Provide exactly three offsets.' }
$scriptPath = Join-Path $PSScriptRoot 'plot_gaussian_wire_offsets.py'
$arguments = @('--background', '--factory-startup', '--python-exit-code', '1', '--python', $scriptPath,
               '--', '--offsets')
$invariant = [Globalization.CultureInfo]::InvariantCulture
$arguments += @($Offsets | ForEach-Object { $_.ToString('G', $invariant) })
$arguments += @('--resolution', $Resolution.ToString($invariant), '--samples', $Samples.ToString($invariant),
                '--output-stem', $OutputStem)
if ($PSBoundParameters.ContainsKey('Fwhm')) { $arguments += @('--fwhm', $Fwhm.ToString('G', $invariant)) }
if ($OutputDir) { $arguments += @('--output-dir', [IO.Path]::GetFullPath($OutputDir)) }
# Keep this portable run's settings/cache inside the workspace.
$previousResources = $env:BLENDER_USER_RESOURCES
$env:BLENDER_USER_RESOURCES = Join-Path $repoRoot 'tmp/blender-runtime/user'
New-Item -ItemType Directory -Force -Path $env:BLENDER_USER_RESOURCES | Out-Null
try {
    & $BlenderPath @arguments
    if ($LASTEXITCODE -ne 0) { throw "Blender exited with code $LASTEXITCODE" }
}
finally {
    $env:BLENDER_USER_RESOURCES = $previousResources
}
