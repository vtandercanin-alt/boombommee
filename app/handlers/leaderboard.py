from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.user_repo import UserRepository
from app.database.db import db
from app.utils.keyboards import get_back_button

router = Router()


@router.message(F.text == "🏆 Топ игроков")
async def show_leaderboard(message: Message):
    """Show leaderboard"""
    session = await db.get_session()
    try:
        users = await UserRepository.get_leaderboard(session, limit=10)
        
        leaderboard_text = "<b>🏆 Топ 10 игроков</b>\n\n"
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, user in enumerate(users, 1):
            medal = medals[i-1] if i <= 3 else f"{i}️⃣"
            leaderboard_text += (
                f"{medal} <b>{user.username or user.first_name or 'Аноним'}</b>\n"
                f"   💰 {user.total_earned:.0f}⭐ | 📦 {user.cases_opened} кейсов\n\n"
            )
        
        await message.answer(leaderboard_text, reply_markup=get_back_button(), parse_mode="HTML")
    finally:
        await session.close()
