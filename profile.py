from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.user_repo import UserRepository
from app.database.db import db
from app.utils.cases import RankSystem
from app.utils.keyboards import get_main_menu, get_back_button
from app.config import config

router = Router()


@router.message(F.text == "👤 Профиль")
async def show_profile(message: Message):
    """Show user profile"""
    session = await db.get_session()
    try:
        stats = await UserRepository.get_user_stats(session, message.from_user.id)
        
        if not stats:
            await message.answer("Пожалуйста, используй /start")
            return
        
        next_rank = RankSystem.get_next_rank_requirement(stats['total_earned'])
        next_rank_text = f"\n\n🎯 До {next_rank['name']}: {next_rank['needed']:.0f}⭐" if next_rank else ""
        
        profile_text = (
            f"<b>👤 Профиль {stats['first_name']}</b>\n\n"
            f"💰 Баланс: <b>{stats['stars_balance']:.0f}⭐</b>\n"
            f"📈 Всего заработано: <b>{stats['total_earned']:.0f}⭐</b>\n"
            f"📦 Кейсов открыто: <b>{stats['cases_opened']}</b>\n\n"
            f"🏅 Ранг: <b>{stats['rank']}</b> (Уровень {stats['level']})\n"
            f"👥 Рефереалов: <b>{stats['referral_count']}</b>\n"
            f"💵 Заработок от рефереалов: <b>{stats['referral_earnings']:.0f}⭐</b>"
            f"{next_rank_text}"
        )
        
        await message.answer(profile_text, reply_markup=get_back_button(), parse_mode="HTML")
    finally:
        await session.close()


@router.message(F.text == "👥 Рефереалы")
async def show_referrals(message: Message):
    """Show referral info"""
    session = await db.get_session()
    try:
        user = await UserRepository.get_user(session, message.from_user.id)
        
        if not user:
            await message.answer("Пожалуйста, используй /start")
            return
        
        # Generate referral link with domain
        referral_link = f"https://{config.DOMAIN}?ref={message.from_user.id}"
        
        referral_text = (
            f"<b>👥 Реферальная программа</b>\n\n"
            f"Твоя ссылка:\n"
            f"<code>{referral_link}</code>\n\n"
            f"📊 Статистика:\n"
            f"Рефереалов: <b>{user.referral_count}</b>\n"
            f"Заработок: <b>{user.referral_earnings:.0f}⭐</b>\n\n"
            f"💡 Как это работает:\n"
            f"1. Отправь свою ссылку друзьям\n"
            f"2. Когда они используют ссылку, ты получишь 5% от их первого открытия кейса\n"
            f"3. Зарабатывай на рефереалах!"
        )
        
        await message.answer(referral_text, reply_markup=get_main_menu(), parse_mode="HTML")
    finally:
        await session.close()


@router.message(F.text == "ℹ️ Помощь")
async def show_help(message: Message):
    """Show help"""
    help_text = (
        "📖 <b>Справка по KRAKEN CASE</b>\n\n"
        "<b>🎁 Кейсы:</b>\n"
        "Открывай кейсы за Телеграм Звёзды и получай награды!\n\n"
        "<b>👥 Рефереалы:</b>\n"
        "Приглашай друзей и получай комиссию с их открытий!\n\n"
        "<b>🏆 Рейтинг:</b>\n"
        "Поднимайся в рейтинге и получай особые привилегии!\n\n"
        "<b>💰 Система рангов:</b>\n"
        "• Bronze: 0⭐\n"
        "• Silver: 500⭐\n"
        "• Gold: 1500⭐\n"
        "• Platinum: 5000⭐\n"
        "• Diamond: 15000⭐\n\n"
        "❓ <b>Вопросы?</b>\n"
        "Напиши администратору или используй /help"
    )
    await message.answer(help_text, reply_markup=get_main_menu(), parse_mode="HTML")
