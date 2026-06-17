@echo off
REM Setup script for KRAKEN CASE Bot on Windows

echo.
echo 🚀 KRAKEN CASE Bot - Setup
echo ==========================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

echo ✅ Python found

REM Install dependencies
echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo.
    echo 📝 Creating .env file...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your Telegram Bot Token
)

echo.
echo ✅ Setup complete!
echo.
echo 📖 Next steps:
echo 1. Edit .env file with your Telegram Bot Token
echo 2. Make sure PostgreSQL is running
echo 3. Run the bot: python main.py
echo.
echo 🐳 Or use Docker: docker-compose up --build
echo.
pause
