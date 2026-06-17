"""
Telegram Bot API Integration Module
Handles webhook and polling setup for the bot
"""

from app.config import config


class BotAPI:
    """Bot API configuration"""
    
    @staticmethod
    def get_webhook_url() -> str:
        """Get webhook URL for Telegram"""
        return f"{config.MINI_APP_URL}/webhook/telegram"
    
    @staticmethod
    def get_webhook_secret() -> str:
        """Get webhook secret token"""
        import secrets
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def get_bot_info() -> dict:
        """Get bot configuration info"""
        return {
            'domain': config.DOMAIN,
            'mini_app_url': config.MINI_APP_URL,
            'web_app_url': config.WEB_APP_URL,
            'webhook_url': BotAPI.get_webhook_url(),
        }


# Example webhook setup (for production)
"""
# To use webhook instead of polling:

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher

app = FastAPI()

@app.post("/webhook/telegram")
async def webhook_handler(request: Request):
    update_data = await request.json()
    Update(**update_data)
    # Process update
    pass

# Register webhook with Telegram
await bot.set_webhook_url(BotAPI.get_webhook_url())
"""
