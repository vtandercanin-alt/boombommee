"""Balance top-up via Telegram Stars (currency XTR).

Telegram Stars use currency="XTR"; amounts are integer star counts.
Two handlers are mandatory for Stars payments:
- pre_checkout_query  -> answer_pre_checkout_query(ok=True)
- successful_payment  -> credit the user balance
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram.filters import Command

from app.database.db import db
from app.database.user_repo import UserRepository
from app.utils.keyboards import get_topup_keyboard, get_main_menu

router = Router()

# Available top-up packages (stars -> price in XTR, 1 star = 1 XTR)
TOPUP_PACKAGES = {
    50: 50,
    100: 100,
    250: 250,
    500: 500,
}


async def show_topup(message: Message):
    """Show top-up amount selection (called from start menu)"""
    text = (
        "💰 <b>Пополнение баланса</b>\n\n"
        "Выбери количество звёзд. Оплата проходит прямо в Telegram через Telegram Stars.\n\n"
        "1⭐ = 1 Telegram Star"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_topup_keyboard())


@router.callback_query(F.data.startswith("topup_"))
async def create_invoice(callback: CallbackQuery):
    """Send an invoice for the selected package"""
    try:
        amount = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer("Неверный пакет", show_alert=True)
        return

    if amount not in TOPUP_PACKAGES:
        await callback.answer("Пакет недоступен", show_alert=True)
        return

    price = TOPUP_PACKAGES[amount]
    bot = callback.bot

    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f"Пополнение баланса на {amount}⭐",
        description=f"Зачислим {amount} звёзд на твой игровой баланс KRAKEN CASE.",
        payload=f"topup_{amount}",
        currency="XTR",
        prices=[LabeledPrice(label=f"{amount} звёзд", amount=price)],
        # In Stars, provider_token is not used — leave empty / omit
    )
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query):
    """Mandatory: approve the Stars payment before Telegram charges the user."""
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    """Credit the balance after a successful Stars payment."""
    payment = message.successful_payment
    payload = payment.invoice_payload  # e.g. "topup_50"

    try:
        amount = int(payload.split("_")[1])
    except (IndexError, ValueError):
        amount = int(payment.total_amount)

    session = await db.get_session()
    try:
        await UserRepository.update_balance(session, message.from_user.id, amount)
    finally:
        await session.close()

    await message.answer(
        f"✅ <b>Баланс пополнен!</b>\n\n"
        f"Зачислено: <b>+{amount}⭐</b>\n\n"
        f"Спасибо за покупку! 🎉",
        parse_mode="HTML",
        reply_markup=get_main_menu(),
    )
