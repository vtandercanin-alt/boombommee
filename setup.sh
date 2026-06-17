#!/bin/bash

# Setup script for KRAKEN CASE Bot

echo "🚀 KRAKEN CASE Bot - Setup"
echo "=========================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE "[0-9]+\.[0-9]+")
echo "✅ Python $python_version detected"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your Telegram Bot Token"
fi

# Create PostgreSQL database (optional)
read -p "Do you want to setup PostgreSQL? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Setting up PostgreSQL..."
    createdb kraken_case_db 2>/dev/null || echo "Database might already exist"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📖 Next steps:"
echo "1. Edit .env file with your Telegram Bot Token"
echo "2. Start PostgreSQL: pg_ctl start (or use Docker: docker-compose up -d postgres)"
echo "3. Run the bot: python main.py"
echo ""
echo "🐳 Or use Docker: docker-compose up --build"
