@echo off
echo Building Optimized Markdown Viewer...
echo.
echo Excluding unnecessary modules to reduce size...
uv run pyinstaller ^
    --onefile ^
    --windowed ^
    --name markdown-viewer ^
    --icon "src/icon.ico" ^
    --add-data "src/templates;templates" ^
    --add-data "src/style.css;." ^
    --add-data "src/icon.ico;." ^
    --add-data "HELP.md;." ^
    --exclude-module tkinter ^
    --exclude-module matplotlib ^
    --exclude-module numpy ^
    --exclude-module pandas ^
    --exclude-module PIL ^
    --exclude-module Pillow ^
    --exclude-module PyQt6.QtBluetooth ^
    --exclude-module PyQt6.QtNfc ^
    --exclude-module PyQt6.QtSensors ^
    --exclude-module PyQt6.QtSerialPort ^
    --exclude-module PyQt6.QtTest ^
    --exclude-module PyQt6.QtMultimedia ^
    --exclude-module PyQt6.QtMultimediaWidgets ^
    --exclude-module PyQt6.Qt3DCore ^
    --exclude-module PyQt6.Qt3DRender ^
    --exclude-module PyQt6.QtCharts ^
    --exclude-module PyQt6.QtDataVisualization ^
    src/main.py
echo.
echo Build complete! Executable is at: dist\markdown-viewer.exe
pause
