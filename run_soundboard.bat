@echo off
setlocal enabledelayedexpansion
title AI Hand-Gesture Soundboard

echo ========================================================
echo   Starting AI Hand-Gesture Soundboard...
echo ========================================================
cd /d "%~dp0"

:: 1. البحث عن بايثون المناسب الذي يحتوي على المكتبات
set "PY_EXE="

if exist "C:\Users\%USERNAME%\miniconda3\python.exe" (
    set "PY_EXE=C:\Users\%USERNAME%\miniconda3\python.exe"
    goto :FOUND_PYTHON
)

if exist "C:\Program Files\Python312\python.exe" (
    set "PY_EXE=C:\Program Files\Python312\python.exe"
    goto :FOUND_PYTHON
)

:: التحقق من أمر python العادي في الـ PATH
where python >nul 2>nul
if %errorlevel% equ 0 (
    set "PY_EXE=python"
    goto :FOUND_PYTHON
)

echo [!] لم يتم العثور على Python مثبت في المسارات المعتادة.
pause
exit /b 1

:FOUND_PYTHON
echo [*] Using Python: "!PY_EXE!"

:: 2. التحقق من وجود cv2 وباقي المكتبات، وتثبيتها إذا لزم الأمر
"!PY_EXE!" -c "import cv2, mediapipe, sounddevice" >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] بعض المكتبات مفقودة في هذا الإصدار، جاري تثبيتها تلقائياً الآن...
    "!PY_EXE!" -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [!] فشل التثبيت التلقائي. يرجى التأكد من اتصال الإنترنت أو صلاحيات المدير.
        pause
        exit /b 1
    )
)

:: 3. تشغيل الساوند بورد
"!PY_EXE!" hand_soundboard.py

if %errorlevel% neq 0 (
    echo.
    echo ========================================================
    echo [!] An error occurred while running the script.
    echo ========================================================
    pause
)
