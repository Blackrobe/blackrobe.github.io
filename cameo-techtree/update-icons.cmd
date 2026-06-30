@echo off
REM Render every buildable actor's cameo to a PNG via the OpenRA utility command
REM --export-cameos, into the extractor's cache (tools\.cache\cameos). update.cmd
REM then prefers those over the loose on-disk PNG cameos, giving ~100% coverage.
REM
REM Requires the Cameo-mod repo as a sibling of this one and a current build
REM (the --export-cameos command lives in OpenRA.Mods.Cameo; run `./make all`).
setlocal
set "MOD=%~dp0..\..\Cameo-mod"
set "OUT=%~dp0tools\.cache\cameos"
if not exist "%MOD%\engine\bin\OpenRA.Utility.dll" (
  echo Cannot find %MOD%\engine\bin\OpenRA.Utility.dll - build Cameo-mod first ^(./make all^).
  exit /b 1
)
set "MOD_SEARCH_PATHS=%MOD%\mods"
set "ENGINE_DIR=.."
pushd "%MOD%\engine"
dotnet bin\OpenRA.Utility.dll cameo --export-cameos "%OUT%"
popd
echo.
echo Done. Now run update.cmd to rebuild the dataset and copy these cameos.
