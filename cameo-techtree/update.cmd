@echo off
REM Regenerate data\techtree.json from the UPSTREAM Cameo-mod repo (master).
REM Usage:  update.cmd            (pull upstream master)
REM         update.cmd --ref foo  (a different branch/tag)
REM         update.cmd --mod "C:\path\to\mods\cameo"   (use a local checkout)
python "%~dp0tools\extract.py" %*
echo.
echo Done. To publish: commit ^& push this repo (blackrobe.github.io master).
