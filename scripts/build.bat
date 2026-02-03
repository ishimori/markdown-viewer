@echo off
cd /d "%~dp0\.."

REM Install pyinstaller in venv if not present
.venv\Scripts\python.exe -m pip install pyinstaller

REM Build exe
.venv\Scripts\python.exe -m PyInstaller scripts\markdown_viewer.spec --noconfirm

echo.
echo Build complete! Check dist\MarkdownViewer.exe
pause
