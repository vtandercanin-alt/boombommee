from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.database.user_repo import UserRepository
from app.utils.keyboards import get_main_menu, get_back_button
from app.database.db import db

router = Router()


async def _ensure_user(message: Message):
    """Get or create user, return the user object"""
    session = await db.get_session()
    try:
        user = await UserRepository.get_or_create_user(
            session,
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
        )
        return user
    finally:
        await session.close()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Start command handler"""
    user = await _ensure_user(message)

    welcome_text = (
        f"🎮 <b>KRAKEN CASE</b>\n\n"
        f"Твой баланс: <b>{user.stars_balance:.0f}⭐</b>\n\n"
        f"Выбери действие:\n"
        f"🎮 <b>Играть</b> — открыть кейсы в Mini App\n"
        f"💰 <b>Пополнить баланс</b> — купить звёзды\n"
        f"ℹ️ <b>Помощь</b> — справка и правила\n"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu(), parse_mode="HTML")


@router.message(F.text == "💰 Пополнить баланс")
async def menu_topup(message: Message):
    """Top-up balance menu"""
    # Import here to avoid circular import
    from app.handlers.topup import show_topup
    await show_topup(message)


@router.message(F.text == "ℹ️ Помощь")
async def menu_help(message: Message):
    """Help menu"""
    help_text = (
        "📖 <b>KRAKEN CASE — Справка</b>\n\n"
        "🎮 <b>Играть</b>\n"
        "Открывает Mini App с кейсами. Открывай кейсы за ⭐ и выигрывай награды!\n\n"
        "💰 <b>Пополнить баланс</b>\n"
        "Купить Telegram Stars прямо в боте (оплата звёздами).\n\n"
        "🏆 <b>Ранги</b>\n"
        "• 🥉 Bronze: 0⭐\n"
        "• 🥈 Silver: 500⭐\n"
        "• 🥇 Gold: 1500⭐\n"
        "• 💎 Platinum: 5000⭐\n"
        "• 👑 Diamond: 15000⭐\n\n"
        "❓ Поддержка: @admin"
    )
    await message.answer(help_text, parse_mode="HTML", reply_markup=get_back_button())


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Back to main menu"""
    await callback.message.answer(
        "🏠 Главное меню", reply_markup=get_main_menu()
    )
    await callback.answer()


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """User stats command"""
    session = await db.get_session()
    try:
        stats = await UserRepository.get_user_stats(session, message.from_user.id)
        if not stats:
            await message.answer("Пользователь не найден. Напиши /start")
            return

        stats_text = (
            f"📊 <b>Твоя статистика</b>\n\n"
            f"💰 Баланс: <b>{stats['stars_balance']:.0f}⭐</b>\n"
            f"📈 Всего заработано: <b>{stats['total_earned']:.0f}⭐</b>\n"
            f"📦 Кейсов открыто: <b>{stats['cases_opened']}</b>\n"
            f"🏅 Ранг: <b>{stats['rank']}</b>\n"
            f"📍 Уровень: <b>{stats['level']}</b>"
        )
        await message.answer(stats_text, parse_mode="HTML")
    finally:
        await session.close()
