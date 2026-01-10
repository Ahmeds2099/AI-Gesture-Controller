@echo off
title AI Gesture Controller

:: Change directory and drive at the same time
cd /d "G:\Coding\Projects\Final_AI_Controller"

:: Check if the activation script exists before trying to run it
if exist "venv\Scripts\activate.bat" (
    echo [SUCCESS] Environment Found. Initializing AI...
    
    :: Activate and run
    call venv\Scripts\activate.bat
    python run_app.py
) else (
    echo [ERROR] Virtual Environment not found at:
    echo %CD%\venv
    echo.
    echo Please make sure this .bat file is in the same folder as your 'venv'.
    pause
)

pause