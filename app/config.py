import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Bot configuration"""
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///data.db')
    MINI_APP_URL = os.getenv('MINI_APP_URL', 'https://cr722031.tw1.ru')
    # WEB_APP_URL is the Mini App URL that Telegram opens. On Render set it to
    # https://<your-service>.onrender.com (the root serves the Mini App page).
    WEB_APP_URL = os.getenv('WEB_APP_URL', 'https://cr722031.tw1.ru')
    DOMAIN = os.getenv('DOMAIN', 'cr722031.tw1.ru')
    PAYMENT_ENABLED = os.getenv('PAYMENT_ENABLED', 'true').lower() == 'true'
    
    # Case settings
    CASE_PRICES = {
        'test': 10  # 10 Telegram Stars for test case
    }
    
    # Case rewards (min, max stars)
    CASE_REWARDS = {
        'test': (5, 100)
    }


config = Config()
