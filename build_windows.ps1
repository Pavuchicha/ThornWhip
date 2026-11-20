# Windows PowerShell; Python 3 + Pillow and .NET 10 SDK required.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $root
try {
    python tests_static_09.py
    if ($LASTEXITCODE -ne 0) { throw 'Static tests failed' }
    python tests_visuals_10.py
    if ($LASTEXITCODE -ne 0) { throw 'Visual tests failed' }
    python tests_runtime_contract_011.py
    if ($LASTEXITCODE -ne 0) { throw '0.11 runtime contracts failed' }
    dotnet restore 'ThornWhip/Source/ThornWhip.csproj'
    if ($LASTEXITCODE -ne 0) { throw 'NuGet restore failed' }
    dotnet build 'ThornWhip/Source/ThornWhip.csproj' -c Release --no-restore
    if ($LASTEXITCODE -ne 0) { throw 'C# compile failed' }
    $dll = Join-Path $root 'ThornWhip/1.7/Assemblies/ThornWhip.dll'
    if (!(Test-Path $dll)) { throw 'Compiled DLL not found' }
    $release = Join-Path $root '_release'
    $stage = Join-Path $release 'ThornWhip'
    if (Test-Path $release) { Remove-Item $release -Recurse -Force }
    New-Item -ItemType Directory -Path $stage -Force | Out-Null
    foreach ($item in @('About','Defs','Textures','1.7','LoadFolders.xml')) {
        Copy-Item -Path (Join-Path $root "ThornWhip/$item") -Destination $stage -Recurse
    }
    $zip = Join-Path $root 'ThornCorps_CE_0.11_TEST_INSTALL.zip'
    if (Test-Path $zip) { Remove-Item $zip }
    Compress-Archive -Path (Join-Path $release 'ThornWhip') -DestinationPath $zip
    Write-Host "Created: $zip"
} finally { Pop-Location }
