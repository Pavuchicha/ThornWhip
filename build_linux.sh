#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 tests_static_09.py
python3 tests_visuals_10.py
dotnet restore ThornWhip/Source/ThornWhip.csproj
dotnet build ThornWhip/Source/ThornWhip.csproj -c Release --no-restore
test -s ThornWhip/1.7/Assemblies/ThornWhip.dll
rm -rf _release
mkdir -p _release/ThornWhip
cp -a ThornWhip/{About,Defs,Textures,1.7,LoadFolders.xml} _release/ThornWhip/
(cd _release && zip -qr ../ThornCorps_CE_Constructor_0.10_INSTALL.zip ThornWhip)
echo 'Created: ThornCorps_CE_Constructor_0.10_INSTALL.zip'
