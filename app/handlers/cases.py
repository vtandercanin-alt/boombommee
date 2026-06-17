from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.user_repo import UserRepository
from app.database.db import db
from app.utils.cases import CaseManager, RankSystem
from app.utils.keyboards import get_cases_keyboard, get_confirm_open_case, get_back_button
from app.config import config

router = Router()


@router.message(F.text == "🎁 Открыть кейс")
async def show_cases(message: Message):
    """Show available cases"""
    session = await db.get_session()
    try:
        user = await UserRepository.get_user(session, message.from_user.id)
        if not user:
            await message.answer("Пожалуйста, используй /start")
            return
        
        cases_text = (
            f"<b>📦 Доступные кейсы</b>\n\n"
            f"Твой баланс: <b>{user.stars_balance:.0f}⭐</b>\n\n"
            f"<b>Тестовый кейс</b>\n"
            f"Цена: 10⭐\n"
            f"Награда: 5-100⭐\n"
            f"Тип: Одноразовый\n\n"
            f"Выбери кейс для открытия:"
        )
        
        await message.answer(cases_text, reply_markup=get_cases_keyboard(), parse_mode="HTML")
    finally:
        await session.close()


@router.callback_query(F.data == "case_test")
async def confirm_case_test(callback: CallbackQuery):
    """Confirm test case opening"""
    session = await db.get_session()
    try:
        user = await UserRepository.get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Ошибка: пользователь не найден", show_alert=True)
            return
        
        price = CaseManager.get_case_price('test')
        
        if user.stars_balance < price:
            await callback.answer(f"❌ Недостаточно звёзд! Нужно: {price}⭐, у тебя: {user.stars_balance:.0f}⭐", show_alert=True)
            return
        
        confirm_text = (
            f"<b>⚠️ Подтверждение</b>\n\n"
            f"Ты готов потратить <b>{price}⭐</b> на открытие кейса?\n\n"
            f"Ожидаемая награда: <b>5-100⭐</b>"
        )
        
        await callback.message.edit_text(confirm_text, reply_markup=get_confirm_open_case('test', price), parse_mode="HTML")
    finally:
        await session.close()


@router.callback_query(F.data == "confirm_case_test")
async def open_case_test(callback: CallbackQuery):
    """Open test case"""
    session = await db.get_session()
    try:
        user = await UserRepository.get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Ошибка: пользователь не найден", show_alert=True)
            return
        
        price = CaseManager.get_case_price('test')
        
        # Check balance again
        if user.stars_balance < price:
            await callback.answer(f"❌ Недостаточно звёзд!", show_alert=True)
            return
        
        # Open case
        reward = CaseManager.open_case('test')
        profit = reward - price
        
        # Update database
        case_opening = await UserRepository.add_case_opening(session, user.telegram_id, 'test', price, reward)
        
        # Get rank
        updated_user = await UserRepository.get_user(session, callback.from_user.id)
        rank = RankSystem.get_rank(updated_user.total_earned)
        
        # Update user rank
        if updated_user.rank != rank['name']:
            updated_user.rank = rank['name']
            updated_user.level = rank['level']
            await session.commit()
            rank_up_msg = f"\n\n🎉 <b>Повышение ранга!</b> Ты достиг <b>{rank['name']}</b>!"
        else:
            rank_up_msg = ""
        
        result_text = (
            f"<b>🎁 Кейс открыт!</b>\n\n"
            f"Цена: <b>{price}⭐</b>\n"
            f"Награда: <b>{reward:.0f}⭐</b>\n"
            f"Результат: {'✅ ПРИБЫЛЬ' if profit > 0 else '❌ УБЫТОК'} <b>{profit:.0f}⭐</b>\n\n"
            f"💰 Новый баланс: <b>{updated_user.stars_balance:.0f}⭐</b>\n"
            f"📊 Всего заработано: <b>{updated_user.total_earned:.0f}⭐</b>\n"
            f"📦 Кейсов открыто: <b>{updated_user.cases_opened}</b>"
            f"{rank_up_msg}"
        )
        
        await callback.message.edit_text(result_text, reply_markup=get_cases_keyboard(), parse_mode="HTML")
        await callback.answer()
    finally:
        await session.close()


@router.callback_query(F.data == "cancel_case")
async def cancel_case(callback: CallbackQuery):
    """Cancel case opening"""
    await callback.message.delete()
    await callback.answer("Отменено")


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Back to main menu"""
    await callback.message.delete()
    await callback.answer()
