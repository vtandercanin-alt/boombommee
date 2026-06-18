from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, WebAppInfo,
)
from app.config import config


def get_main_menu() -> ReplyKeyboardMarkup:
    """Main menu keyboard: Играть (Mini App), Пополнить баланс, Помощь"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎮 Играть", web_app=WebAppInfo(url=config.WEB_APP_URL))],
            [KeyboardButton(text="💰 Пополнить баланс")],
            [KeyboardButton(text="ℹ️ Помощь")],
        ],
        resize_keyboard=True,
    )
    return keyboard


def get_cases_keyboard() -> InlineKeyboardMarkup:
    """Available cases keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📦 Тестовый кейс (10⭐)", callback_data="case_test")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")],
        ]
    )
    return keyboard


def get_confirm_open_case(case_type: str, price: int) -> InlineKeyboardMarkup:
    """Confirm case opening keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"✅ Открыть за {price}⭐", callback_data=f"confirm_case_{case_type}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_case")],
        ]
    )
    return keyboard


def get_topup_keyboard() -> InlineKeyboardMarkup:
    """Top-up amount selection (Telegram Stars / XTR)"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐ 50 звёзд", callback_data="topup_50"),
             InlineKeyboardButton(text="⭐ 100 звёзд", callback_data="topup_100")],
            [InlineKeyboardButton(text="⭐ 250 звёзд", callback_data="topup_250"),
             InlineKeyboardButton(text="⭐ 500 звёзд", callback_data="topup_500")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")],
        ]
    )
    return keyboard


def get_back_button() -> InlineKeyboardMarkup:
    """Back button"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")],
        ]
    )
    return keyboard


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Profile keyboard kept for backward compatibility."""
    # Historically some handlers imported `get_profile_keyboard`.
    # Return the same simple back button keyboard by default.
    return get_back_button()
