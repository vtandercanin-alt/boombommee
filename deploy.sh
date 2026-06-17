#!/bin/bash

# KRAKEN CASE Bot - Rapid Deployment Script
# Usage: chmod +x deploy.sh && ./deploy.sh

set -e

echo "🚀 KRAKEN CASE Bot - Deployment Script"
echo "======================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (sudo)${NC}"
    exit 1
fi

# Variables
DOMAIN="cr722031.tw1.ru"
PROJECT_DIR="/opt/kraken_case_bot"
TELEGRAM_BOT_TOKEN=""
DB_PASSWORD=$(openssl rand -base64 32)

# Step 1: Update system
echo -e "${YELLOW}Step 1: Updating system...${NC}"
apt update && apt upgrade -y

# Step 2: Install dependencies
echo -e "${YELLOW}Step 2: Installing dependencies...${NC}"
apt install -y \
    curl \
    git \
    wget \
    nginx \
    certbot \
    python3-certbot-nginx \
    postgresql-client

# Step 3: Install Docker
echo -e "${YELLOW}Step 3: Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Step 4: Install Docker Compose
echo -e "${YELLOW}Step 4: Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Step 5: Create project directory
echo -e "${YELLOW}Step 5: Creating project directory...${NC}"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Step 6: Clone or update repository
if [ -d ".git" ]; then
    echo -e "${YELLOW}Updating existing repository...${NC}"
    git pull
else
    echo -e "${YELLOW}Step 6: Cloning repository...${NC}"
    read -p "GitHub repository URL (or press Enter to skip): " REPO_URL
    if [ ! -z "$REPO_URL" ]; then
        git clone $REPO_URL .
    else
        echo -e "${YELLOW}Skipping git clone. Please add files manually.${NC}"
    fi
fi

# Step 7: Configure environment
echo -e "${YELLOW}Step 7: Configuring environment...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    read -p "Enter Telegram Bot Token: " TELEGRAM_BOT_TOKEN
    sed -i "s/BOT_TOKEN=.*/BOT_TOKEN=$TELEGRAM_BOT_TOKEN/" .env
    sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$DB_PASSWORD/" .env
fi

# Step 8: Setup SSL certificate
echo -e "${YELLOW}Step 8: Setting up SSL certificate...${NC}"
certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN

# Step 9: Configure Nginx
echo -e "${YELLOW}Step 9: Configuring Nginx...${NC}"
cp nginx.conf.example /etc/nginx/sites-available/$DOMAIN
# Replace domain in nginx config (если домен изменён в переменной DOMAIN)
sed -i "s/cr722031.tw1.ru/$DOMAIN/g" /etc/nginx/sites-available/$DOMAIN

# Enable site
if [ ! -L "/etc/nginx/sites-enabled/$DOMAIN" ]; then
    ln -s /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
fi

# Test and reload
nginx -t && systemctl reload nginx

# Step 10: Start Docker containers
echo -e "${YELLOW}Step 10: Starting Docker containers...${NC}"
docker-compose up -d

# Step 11: Initialize database
echo -e "${YELLOW}Step 11: Initializing database...${NC}"
sleep 10  # Wait for postgres to start
docker-compose exec -T postgres psql -U kraken_user -d kraken_case_db -c "SELECT version();" || echo "Database initialization..."

# Step 12: Setup SSL renewal
echo -e "${YELLOW}Step 12: Setting up SSL auto-renewal...${NC}"
systemctl enable certbot.timer
systemctl start certbot.timer

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo -e "${GREEN}Your bot is running at:${NC}"
echo -e "  🔗 https://$DOMAIN"
echo -e "  📱 Webhook: https://$DOMAIN/webhook/telegram"
echo ""
echo -e "${YELLOW}Important:${NC}"
echo -e "  1. Check logs: docker-compose logs -f"
echo -e "  2. Verify bot: curl https://$DOMAIN/health"
echo -e "  3. Backup: docker-compose exec postgres pg_dump -U kraken_user kraken_case_db > backup.sql"
echo ""
