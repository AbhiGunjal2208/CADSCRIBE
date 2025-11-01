@echo off
setlocal enabledelayedexpansion

echo Starting CADSCRIBE setup...
echo.

REM Create .env files if they don't exist
echo Setting up environment files...
if not exist ".env" (
    (
        echo VITE_API_URL=http://localhost:8000
    ) > .env
    echo Created frontend .env
)

if not exist "backend\.env" (
    (
        echo # Database Configuration
        echo MONGODB_URI=mongodb://127.0.0.1:27017/cadscribe
        echo DATABASE_NAME=cadscribe
        echo.
        echo # API Keys
        echo OPENAI_API_KEY=your_openai_api_key_here
        echo GEMINI_API_KEY=your_gemini_api_key_here
        echo.
        echo # Service URLs
        echo CAD_SERVICE_URL=http://localhost:9000
        echo.
        echo # Security
        echo SECRET_KEY=your-secret-key-change-in-production
        echo DEBUG=false
        echo.
        echo # CORS Origins (comma-separated^)
        echo CORS_ORIGINS=http://localhost:3000,http://localhost:5173
        echo.
        echo # File Storage
        echo UPLOAD_DIR=uploads
        echo GENERATED_MODELS_DIR=generated_models
    ) > backend\.env
    echo Created backend .env
)

REM Install frontend dependencies
echo.
echo Installing frontend dependencies...
call npm install

REM Install backend dependencies
echo.
echo Installing backend dependencies...
cd backend
python -m pip install -r requirements.txt
cd ..

REM Install CAD service dependencies
echo.
echo Installing CAD service dependencies...
cd cad-service
python -m pip install -r requirements.txt
cd ..

REM Create required directories
echo.
echo Creating required directories...
if not exist "backend\uploads" mkdir backend\uploads
if not exist "backend\generated_models" mkdir backend\generated_models
if not exist "cad-service\generated_models" mkdir cad-service\generated_models

REM Check MongoDB installation
echo.
echo Checking MongoDB installation...
mongod --version >nul 2>&1
if %errorlevel% equ 0 (
    echo MongoDB is installed
    net start MongoDB
) else (
    echo MongoDB is not installed. Please install MongoDB first:
    echo choco install mongodb
)

REM Check FreeCAD installation
echo.
echo Checking FreeCAD installation...
freecad --version >nul 2>&1
if %errorlevel% equ 0 (
    echo FreeCAD is installed
) else (
    echo FreeCAD is not installed. Please install FreeCAD first:
    echo choco install freecad
)

echo.
echo Setup completed!
echo.
echo To start the services:
echo 1. Start backend: cd backend ^&^& python main.py
echo 2. Start CAD service: cd cad-service ^&^& python cad_api.py
echo 3. Start frontend: npm run dev
echo.
echo Make sure to update the API keys in backend\.env:
echo - OPENAI_API_KEY from https://platform.openai.com/api-keys
echo - GEMINI_API_KEY from https://makersuite.google.com/app/apikey

pause