@echo off
echo Building Markdown Viewer...
uv run pyinstaller --onefile --windowed --name markdown-viewer --icon "src/icon.ico" --add-data "src/templates;templates" --add-data "src/style.css;." --add-data "src/icon.ico;." --add-data "HELP.md;." src/main.py
echo.
echo Build complete! Executable is at: dist\markdown-viewer.exe
pause
