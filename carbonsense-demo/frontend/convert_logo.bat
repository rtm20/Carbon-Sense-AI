@echo off
echo CarbonSense AI Logo PNG Converter
echo ===================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install required packages
echo Installing required packages...
pip install cairosvg pillow --quiet

REM Run the converter
echo.
echo Converting SVG logos to PNG...
python convert_logo_to_png.py

echo.
echo Conversion complete!
echo Check the current folder for PNG files.
pause
