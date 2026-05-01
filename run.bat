@echo off
REM Road Quality Monitoring System - Local Setup Script (Windows)
REM This script automates the setup and startup process

setlocal enabledelayedexpansion

echo.
echo ================================
echo Road Quality Monitoring System
echo Local Setup ^& Run Script (Windows)
echo ================================
echo.

REM Check if Python is installed
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed. Please install Python 3.11+
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python found: %PYTHON_VERSION%
echo.

REM Check if Docker is installed
echo [2/7] Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed. Please install Docker and Docker Compose
    pause
    exit /b 1
)
for /f "tokens=3" %%i in ('docker --version') do set DOCKER_VERSION=%%i
echo [OK] Docker found: %DOCKER_VERSION%
echo.

REM Create virtual environment
echo [3/7] Creating Python virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [4/7] Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo [5/7] Installing dependencies...
pip install --upgrade pip setuptools wheel >nul 2>&1
pip install -r requirements.txt >nul 2>&1
echo [OK] Dependencies installed
echo.

REM Setup environment file
echo [6/7] Setting up environment variables...
if not exist ".env" (
    copy .env.example .env
    echo [OK] .env file created from template
) else (
    echo [OK] .env file already exists
)
echo.

REM Start Docker services
echo [7/7] Starting Docker services (PostgreSQL, Redis)...
docker-compose up -d
echo [OK] Docker services started
echo.

echo Waiting for services to be ready...
timeout /t 5 /nobreak
echo.

echo ================================
echo Setup Complete!
echo ================================
echo.
echo Starting FastAPI Server...
echo.
echo Available URLs:
echo   - API Docs (Swagger):    http://localhost:8000/docs
echo   - API Docs (ReDoc):      http://localhost:8000/redoc
echo   - OpenAPI Schema:        http://localhost:8000/openapi.json
echo.
echo Quick Commands:
echo   - Run tests:             pytest tests/ -v
echo   - Coverage report:       pytest --cov=src tests/ -v
echo   - Stop services:         docker-compose down
echo.

REM Start the server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

pause
