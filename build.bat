@echo off
echo Building Markdown Viewer...
uv run pyinstaller --onefile --windowed --name markdown-viewer --add-data "src/templates;templates" --add-data "src/style.css;." src/main.py
echo.
echo Build complete! Executable is at: dist\markdown-viewer.exe
pause
