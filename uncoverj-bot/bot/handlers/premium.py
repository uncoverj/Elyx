from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from backend.database import async_session_maker
from backend.models.user import User
from backend.services.premium import PREMIUM_PLANS, activate_premium
from bot.keyboards.profile import get_settings_kb

router = Router()


def _get_premium_plans_kb() -> InlineKeyboardMarkup:
    """Inline клавиатура с тарифами"""
    buttons = []
    for key, plan in PREMIUM_PLANS.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"⭐ {plan['label']} — {plan['stars']} Stars",
                callback_data=f"buy_premium_{key}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text == "⭐ Premium")
async def show_premium_plans(message: Message):
    text = (
        "<b>⭐ Premium статус</b>\n\n"
        "Преимущества Premium:\n"
        "• 150 свайпов в день (вместо 30)\n"
        "• Значок ⭐ в профиле\n"
        "• Приоритет в выдаче анкет\n\n"
        "Выбери тариф:"
    )
    await message.answer(text, reply_markup=_get_premium_plans_kb())


@router.callback_query(F.data.startswith("buy_premium_"))
async def process_buy_premium(callback: CallbackQuery):
    """Создаём invoice через Telegram Stars"""
    plan_key = callback.data.replace("buy_premium_", "")
    plan = PREMIUM_PLANS.get(plan_key)

    if not plan:
        await callback.answer("Тариф не найден")
        return

    # Создаём invoice
    prices = [LabeledPrice(label=f"Premium {plan['label']}", amount=plan["stars"])]

    await callback.message.answer_invoice(
        title="Uncoverj Premium",
        description=f"Premium статус на {plan['label']}. {plan['days']} дней.",
        payload=f"premium_{plan_key}",
        currency="XTR",  # Telegram Stars
        prices=prices,
    )
    await callback.answer()


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    """Подтверждаем checkout — обязательный шаг для Telegram Payments"""
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message, db_user: User):
    """Обработка успешного платежа"""
    payload = message.successful_payment.invoice_payload  # "premium_1_week"
    plan_key = payload.replace("premium_", "")

    async with async_session_maker() as session:
        success = await activate_premium(session, db_user.id, plan_key)

    if success:
        plan = PREMIUM_PLANS.get(plan_key, {})
        await message.answer(
            f"Спасибо за покупку! ⭐\n\n"
            f"Premium активирован на {plan.get('label', 'N/A')}.\n"
            f"Теперь у тебя 150 свайпов в день и значок ⭐!",
            reply_markup=get_settings_kb()
        )
    else:
        await message.answer("Произошла ошибка при активации Premium. Обратись в поддержку.")
